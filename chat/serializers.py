import json
from rest_framework import serializers
from rest_framework.exceptions import NotFound, AuthenticationFailed
from channels import Group

from .models import *
from accounts.models import User


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(read_only=True, required=False)
    username = serializers.CharField(required=False, max_length=20, min_length=8)

    class Meta:
        model = User
        fields = (
            'id', 'uuid', 'username', 'email', 'first_name', 'last_name',
        )
        read_only_fields = (
            'uuid',
            # 'created_at', 'updated_at',
        )

    def validate(self, data):
        username = data.get('username')
        # Check that the username does not already exist
        if User.objects.exclude(pk=self.instance.pk).filter(username=username).first():
            raise serializers.ValidationError({
                'username': 'Username already exists. Please try another.'
            })

        return data


class ThreadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thread
        fields = (
            'id', 'title', 'slug', 'created_at', 'updated_at',
        )
        read_only_fields = ('created_at', 'updated_at',)


class MessageSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True, required=False)
    thread = ThreadSerializer(read_only=True, required=False)

    class Meta:
        model = Message
        fields = (
            'id', 'content', 'created_at', 'updated_at',
            'user', 'thread',
        )
        read_only_fields = ('created_at', 'updated_at',)

    def get_thread(self):
        username = self.context.get('kwargs').get('username', None)
        if username == self.context.get('request').user.username:
            raise AuthenticationFailed
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise NotFound

        if username < self.context.get('request').user.username:
            thread_name = '-'.join([username, self.context.get('request').user.username])
        else:
            thread_name = '-'.join([self.context.get('request').user.username, username])

        thread = Thread.objects.get_or_create(title=thread_name, slug=thread_name)[0]

        return thread

    # call this function after is_valid() and save()
    # so we get the saved, serialized data to send
    # to the channel group via websockets
    def send_message(self):
        # Encode and send that message to the whole channels Group for our
        # thread. Note how you can send to a channel or Group from any part
        # of Django, not just inside a consumer.
        Group(self.data['thread']['title']).send({
            # WebSocket text frame, with JSON content
            "text": json.dumps(self.data),
        })

