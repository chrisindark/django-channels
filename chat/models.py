from __future__ import unicode_literals

from django.db import models
from channels import Group

from .constants import MSG_TYPE_MESSAGE
from accounts.models import User


# Create your models here.
class Channel(models.Model):
    admin = models.ForeignKey(User, related_name='channels')
    users = models.ManyToManyField(User)
    channel_name = models.CharField(max_length=50)
    channel_type = models.CharField(max_length=50)

    def __unicode__(self):
        return self.channel_name

    def __repr__(self):
        return '<Channel: {channel_name}>'.format(channel_name=self.channel_name)


class Thread(models.Model):
    title = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=100, unique=True)  # Slug for routing (both HTML pages and WebSockets)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.title

    def __repr__(self):
        return '<Thread: {title}>'.format(title=self.title)


class Message(models.Model):
    user = models.ForeignKey(User, related_name='posts')
    thread = models.ForeignKey(Thread, related_name="posts")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.content

    def __repr__(self):
        return '<Message: {content}>'.format(content=self.content)


class LoggedInUser(models.Model):
    from django.conf import settings
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name='logged_in_user')
    status = models.CharField(max_length=20, default='Offline')


class Room(models.Model):
    """
    A room for people to chat in.
    """
    # Room title
    title = models.CharField(max_length=255, null=True)
    # If only "staff" users are allowed (is_staff on django's User)
    staff_only = models.BooleanField(default=False)

    def __unicode__(self):
        return self.title

    @property
    def websocket_group(self):
        """
        Returns the Channels Group that sockets should subscribe to to get sent
        messages as they are generated.
        """
        return Group("room-%s" % self.id)

    def send_message(self, message, user, msg_type=MSG_TYPE_MESSAGE):
        """
        Called to send a message to the room on behalf of a user.
        """
        final_msg = {'room': str(self.id), 'message': message, 'username': user.username, 'msg_type': msg_type}

        # Send out the message to everyone in the room
        import json
        self.websocket_group.send(
            {"text": json.dumps(final_msg)}
        )
