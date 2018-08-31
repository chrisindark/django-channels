import random
import string
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from haikunator import Haikunator
from rest_framework import mixins, viewsets, permissions
import django_filters
from rest_framework.exceptions import NotFound

from .models import *
from .serializers import *


# Create your views here.
def about(request):
    return render(request, "about.html")


def new_room(request):
    """
    Randomly create a new room, and redirect to it.
    """
    new_room = None
    while not new_room:
        with transaction.atomic():
            haikunator = Haikunator()
            label = haikunator.haikunate()
            if Room.objects.filter(label=label).exists():
                continue
            new_room = Room.objects.create(label=label)
    return redirect(chat_room, label=label)


def chat_room(request, label):
    """
    Room view - show the room, with latest messages.

    The template for this view has the WebSocket business to send and stream
    messages, so see the template for where the magic happens.
    """
    # If the room with the given label doesn't exist, automatically create it
    # upon first visit (a la etherpad).
    room, created = Room.objects.get_or_create(label=label)

    # We want to show the last 50 messages, ordered most-recent-last
    messages = reversed(room.messages.order_by('-timestamp')[:50])

    return render(request, "room.html", {
        'room': room,
        'messages': messages,
    })


@login_required
def index(request):
    """
    Root page view. This is essentially a single-page app, if you ignore the
    login and admin parts.
    """
    # Get a list of rooms, ordered alphabetically
    rooms = Room.objects.order_by("title")

    # Render that in the index template
    return render(request, "index.html", {
        "rooms": rooms,
    })


def thread_direct(request, username):
    user = get_object_or_404(User, username=username)
    return render(request, 'thread-direct.html')


class IsOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.user:
            return obj.user == request.user
        return False


class MessageFilter(django_filters.FilterSet):
    # username = django_filters.CharFilter(name="user__username")
    o = django_filters.OrderingFilter(
        # tuple-mapping retains order
        fields=(
            ('created_at', 'created_at'),
        ),
    )

    class Meta:
        model = Message
        fields = (
            'created_at',
        )


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwner)

    def get_serializer_context(self):
        context = super(MessageViewSet, self).get_serializer_context()
        context['kwargs'] = self.kwargs
        return context

    def get_queryset(self):
        context = self.get_serializer_context()
        thread = self.serializer_class(context=context).get_thread()
        queryset = self.queryset.filter(thread=thread)

        return queryset

    def perform_create(self, serializer):
        thread = serializer.get_thread()
        serializer.save(thread=thread, user=self.request.user)
        pass
