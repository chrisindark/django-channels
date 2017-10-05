import re
import json
import logging
from channels import Group, Channel
from channels.sessions import channel_session
from channels.auth import channel_session_user_from_http, channel_session_user
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound

from .constants import *
from .utils import get_room_or_error, catch_client_error
from .exceptions import ClientError
from .models import Thread, Message, Room, Channel
from .serializers import ThreadSerializer, MessageSerializer


logger = logging.getLogger(__name__)


@channel_session
def ws_connect(message):
    # Extract the room from the message. This expects message.path to be of the
    # form /chat/{label}/, and finds a Room if the message path is applicable,
    # and if the Room exists. Otherwise, bails (meaning this is a some othersort
    # of websocket). So, this is effectively a version of _get_object_or_404.
    try:
        prefix, label = message['path'].strip('/').split('/')
        if prefix != 'chat':
            logger.debug('invalid ws path=%s', message['path'])
            return
        room = Room.objects.get(label=label)
    except ValueError:
        logger.debug('invalid ws path=%s', message['path'])
        return
    except Room.DoesNotExist:
        logger.debug('ws room does not exist label=%s', label)
        return

    logger.debug('chat connect room=%s client=%s:%s',
                 room.label, message['client'][0], message['client'][1])
    Group('chat-'+label).add(message.reply_channel)
    message.channel_session['room'] = room.label


@channel_session
def ws_receive(message):
    # Look up the room from the channel session, bailing if it doesn't exist
    try:
        label = message.channel_session['room']
        room = Room.objects.get(label=label)
    except KeyError:
        logger.debug('no room in channel_session')
        return
    except Room.DoesNotExist:
        logger.debug('recieved message, but room does not exist label=%s', label)
        return

    # Parse out a chat message from the content text, bailing if it doesn't
    # conform to the expected message format.
    try:
        data = json.loads(message['text'])
    except ValueError:
        logger.debug("ws message isn't json text=%s", message['text'])
        return

    if set(data.keys()) != {'handle', 'message'}:
        logger.debug("ws message unexpected format data=%s", data)
        return

    if data:
        logger.debug('chat message room=%s handle=%s message=%s',
            room.label, data['handle'], data['message'])
        m = room.messages.create(**data)
        Group('chat-'+label).send({'text': json.dumps(m.as_dict())})


@channel_session
def ws_disconnect(message):
    try:
        label = message.channel_session['room']
        room = Room.objects.get(label=label)
        Group('chat-'+label).discard(message.reply_channel)
    except (KeyError, Room.DoesNotExist):
        pass


# Chat channel handling #

# Channel_session_user loads the user out from the channel session and presents
# it as message.user. There's also a http_session_user if you want to do this on
# a low-level HTTP handler, or just channel_session if all you want is the
# message.channel_session object without the auth fetching overhead.
@channel_session_user
@catch_client_error
def chat_join(message):
    print("hello2")
    # Find the room they requested (by ID) and add ourselves to the send group
    # Note that, because of channel_session_user, we have a message.user
    # object that works just like request.user would. Security!
    room = get_room_or_error(message["room"], message.user)

    # Send a "enter message" to the room if available
    if NOTIFY_USERS_ON_ENTER_OR_LEAVE_ROOMS:
        room.send_message(None, message.user, MSG_TYPE_ENTER)

    # OK, add them in. The websocket_group is what we'll send messages
    # to so that everyone in the chat room gets them.
    room.websocket_group.add(message.reply_channel)
    message.channel_session['rooms'] = list(set(message.channel_session['rooms']).union([room.id]))
    # Send a message back that will prompt them to open the room
    # Done server-side so that we could, for example, make people
    # join rooms automatically.
    message.reply_channel.send({
        "text": json.dumps({
            "join": str(room.id),
            "title": room.title,
        }),
    })


@channel_session_user
@catch_client_error
def chat_leave(message):
    print("hello3")
    # Reverse of join - remove them from everything.
    room = get_room_or_error(message["room"], message.user)

    # Send a "leave message" to the room if available
    if NOTIFY_USERS_ON_ENTER_OR_LEAVE_ROOMS:
        room.send_message(None, message.user, MSG_TYPE_LEAVE)

    room.websocket_group.discard(message.reply_channel)
    message.channel_session['rooms'] = list(set(message.channel_session['rooms']).difference([room.id]))
    # Send a message back that will prompt them to close the room
    message.reply_channel.send({
        "text": json.dumps({
            "leave": str(room.id),
        }),
    })


@channel_session_user
@catch_client_error
def chat_send(message):
    print("hello4")
    # Check that the user in the room
    if int(message['room']) not in message.channel_session['rooms']:
        raise ClientError("ROOM_ACCESS_DENIED")
    # Find the room they're sending to, check perms
    room = get_room_or_error(message["room"], message.user)
    # Send the message along
    room.send_message(message["message"], message.user)


# 'http_session_user' will provide a message.user attribute as well as the session attribute
# only available in connect message of a WebSocket connection

# Connected to websocket.connect
@channel_session_user_from_http
def ws_thread_connect(message, slug):
    print(slug)
    """
    When the user opens a WebSocket to a thread stream, adds them to the
    group for that stream so they receive new post notifications.
    The notifications are actually sent in the Post model on save.
    """
    # Try to fetch the thread by slug; if that fails, close the socket.
    try:
        thread = Thread.objects.get(slug=slug)
    except Thread.DoesNotExist:
        # You can see what messages back to a WebSocket look like in the spec:
        # http://channels.readthedocs.org/en/latest/asgi.html#send-close
        # Here, we send "close" to make Daphne close off the socket, and some
        # error text for the client.
        message.reply_channel.send({
            # WebSockets send either a text or binary payload each frame.
            # We do JSON over the text portion.
            "text": json.dumps({"error": "bad_slug"}),
            "close": True
        })
        return
    message.reply_channel.send({"accept": True})
    # Each different client has a different "reply_channel", which is how you
    # send information back to them. We can add all the different reply channels
    # to a single Group, and then when we send to the group, they'll all get the
    # same message.
    Group(thread.title).add(message.reply_channel)


# Connected to websocket.disconnect
@channel_session_user
def ws_thread_disconnect(message, slug):
    """
    Removes the user from the thread group when they disconnect.
    Channels will auto-cleanup eventually, but it can take a while, and having old
    entries cluttering up your group will reduce performance.
    """
    try:
        thread = Thread.objects.get(slug=slug)
    except Thread.DoesNotExist:
        # This is the disconnect message, so the socket is already gone; we can't
        # send an error back. Instead, we just return from the consumer.
        return
    # It's called .discard() because if the reply channel is already there it
    # won't fail - just like the set() type.
    Group(thread.title).discard(message.reply_channel)


@channel_session_user
def ws_thread_message(message, slug):
    print(slug)
    """
    Saves new message to the respective thread in the database.
    """
    data = json.loads(message.content.get('text'))
    serializer = MessageSerializer(data=data)
    if serializer.is_valid(raise_exception=True):
        thread = Thread.objects.get(slug=slug)
        serializer.save()
        serializer.send_message()


@channel_session_user_from_http
def ws_direct_connect(message, username):
    if username < message.user.username:
        thread_name = '-'.join([username, message.user.username])
    else:
        thread_name = '-'.join([message.user.username, username])
    try:
        thread = Thread.objects.get(title=thread_name, slug=thread_name)
    except Thread.DoesNotExist:
        # You can see what messages back to a WebSocket look like in the spec:
        # http://channels.readthedocs.org/en/latest/asgi.html#send-close
        # Here, we send "close" to make Daphne close off the socket, and some
        # error text for the client.
        message.reply_channel.send({
            # WebSockets send either a text or binary payload each frame.
            # We do JSON over the text portion.
            "text": json.dumps({"error": "bad_slug"}),
            "close": True
        })
        return
    message.reply_channel.send({"accept": True})
    # Each different client has a different "reply_channel", which is how you
    # send information back to them. We can add all the different reply channels
    # to a single Group, and then when we send to the group, they'll all get the
    # same message.
    Group(thread.title).add(message.reply_channel)

    # Group(thread.title).send({
    #     'text': json.dumps({
    #         'username': message.user.username,
    #         'is_logged_in': True
    #     })
    # })
    # from .models import LoggedInUser
    # user_obj = LoggedInUser.objects.get_or_create(user=message.user)
    # user_obj.status = 'Online'
    # user_obj.save()


@channel_session_user
def ws_direct_message(message, username):
    if username < message.user.username:
        thread_name = '-'.join([username, message.user.username])
    else:
        thread_name = '-'.join([message.user.username, username])

    data = json.loads(message.content.get('text'))

    # if data.get('action') == 'create':
    #     serializer = MessageSerializer(data=data)
    # elif data.get('action') == 'update':
    #     instance = get_object_or_404(Message, pk=data.get('id'))
    #     serializer = MessageSerializer(data=data, instance=instance)
    # elif data.get('action') == 'delete':
    #     try:
    #         Message.objects.get(pk=data.get('id')).delete()
    #     except Message.DoesNotExist:
    #         raise NotFound

    serializer = MessageSerializer(data=data)
    if serializer.is_valid(raise_exception=True):
        thread = Thread.objects.get(title=thread_name, slug=thread_name)
        serializer.save(user=message.user, thread=thread)
        print(serializer.data)

    else:
        print(serializer.errors)

    serializer.send_message()


@channel_session_user
def ws_direct_disconnect(message, username):
    if username < message.user.username:
        thread_name = '-'.join([username, message.user.username])
    else:
        thread_name = '-'.join([message.user.username, username])

    try:
        thread = Thread.objects.get(title=thread_name, slug=thread_name)
    except Thread.DoesNotExist:
        return

    Group(thread.title).discard(message.reply_channel)

    # Group('users').send({
    #     'text': json.dumps({
    #         'username': message.user.username,
    #         'is_logged_in': False
    #     })
    # })

    # from .models import LoggedInUser
    # user_obj = LoggedInUser.objects.get_or_create(user=message.user)
    # user_obj.status = 'Offline'
    # user_obj.save()
