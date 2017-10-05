from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404
from django.db.models.signals import post_save

from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import User, UserProfile
from .serializers import UserSerializer
from .forms import UserChangeForm, UserProfileChangeForm


# Create your views here.
# Method the current user can use to find their user ID
@api_view(['GET'])
def current_user(request):
    if request.user.is_authenticated():
        return Response({'id': request.user.id,})
    return Response({})


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


@login_required
def user_account(request, username):
    user = get_object_or_404(User, username=username)
    if request.user.pk == user.pk:
        if request.method == "POST":
            form = UserChangeForm(request.POST, instance=user)
            if form.is_valid():
                form.save()
        else:
            form = UserChangeForm(instance=user)
        return render(request, 'user_account.html', {'form': form})
    else:
        raise PermissionDenied


@login_required
def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    profile = UserProfile.objects.get_or_create(user=user)[0]

    if request.user.pk == user.pk:
        if request.method == "POST":
            form = UserProfileChangeForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                form.save()
        else:
            form = UserProfileChangeForm(instance=user)
        return render(request, 'user_profile.html', {'form': form})
    else:
        raise PermissionDenied


def create_profile(sender, **kwargs):
    user = kwargs.get('instance')
    if kwargs.get('created'):
        user_profile = UserProfile(user=user)
        user_profile.save()

post_save.connect(create_profile, sender=User)
