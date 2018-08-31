from channels.routing import route

from chat import consumers


# There's no path matching on these routes; we just rely on the matching
# from the top-level routing. We _could_ path match here if we wanted.
channel_routing = [
    # route("websocket.connect", consumers.ws_connect),
    # route("websocket.receive", consumers.ws_receive),
    # route("websocket.disconnect", consumers.ws_disconnect),
    # Handling different chat commands (websocket.receive is decoded and put
    # onto this channel) - routed on the "command" attribute of the decoded
    # message.
    # route("chat.receive", consumers.chat_join, command="^join$"),
    # route("chat.receive",consumers. chat_leave, command="^leave$"),
    # route("chat.receive", consumers.chat_send, command="^send$")
]

# The channel routing defines what channels get handled by what consumers,
# including optional matching on message attributes. WebSocket messages of all
# types have a 'path' attribute, so we're using that to route the socket.
# While this is under stream/ compared to the HTML page, we could have it on the
# same URL if we wanted; Daphne separates by protocol as it negotiates with a browser.
thread_websocket = [
    # Called when incoming WebSockets connect
    route("websocket.connect", consumers.ws_thread_connect),

    # Called when the client closes the socket
    route("websocket.disconnect", consumers.ws_thread_disconnect),

    # Called when the client sends message on the WebSocket
    route("websocket.receive", consumers.ws_thread_message)

    # A default "http.request" route is always inserted by Django at the end of the routing list
    # that routes all unmatched HTTP requests to the Django view system. If you want lower-level
    # HTTP handling - e.g. long-polling - you can do it here and route by path, and let the rest
    # fall through to normal views.
]

direct_websocket = [
    route("websocket.connect", consumers.ws_direct_connect),
    route("websocket.receive", consumers.ws_direct_message),
    route("websocket.disconnect", consumers.ws_direct_disconnect)
]
