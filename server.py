"""
 This file is part of FaldaTouch.

    Faldatouch is a framework to add multi-pointer support to pygame
    applications
    Copyright (C) 2011 Felipe Lerena, Alejandro Cura, Hugo Ruscitti

    FaldaTouch is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    FaldaTouch is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with FaldaTouch.  If not, see <http://www.gnu.org/licenses/>.
"""
from twisted.internet import reactor
from twisted.web import server
from twisted.web.resource import Resource

from txosc import osc
from txosc import dispatch
from txosc import async


class UDPSenderApplication(object):
    def __init__(self, canvas, host="192.168.1.147", port=57110):#83
        self.port = port
        self.host = host
        self.client = async.DatagramClientProtocol()
        self._client_port = reactor.listenUDP(0, self.client)

    def send_move(self, dx, dy):
        element = osc.Message("/mouse", 2, dx, dy)
        self.client.send(element, (self.host, self.port))

    def send_click(self, button, state=True):
        button_map = {
            1: '/leftbutton',
            2: '/middlebutton',
            3: '/rightbutton',
        }
        button_state = 0 if state else 1
        button = button_map.get(button, None)
        if button is not None:
            element = osc.Message(button, button_state)
            self.client.send(element, (self.host, self.port))

class UDPReceiverApplication(object):
    """
    Example that receives UDP OSC messages.
    """
    def __init__(self, canvas, host="localhost", port=57110):#83
        self.canvas = canvas
        self.port = port
        self.host = host
        self.receiver = dispatch.Receiver()
        self._server_port = reactor.listenUDP(self.port,
            async.DatagramServerProtocol(self.receiver))

        print("Listening on osc.udp://localhost:%s" % (self.port))

        self.receiver.fallback = self.handle

        self.users = {}

    def handle(self, message, address):
        ip_address = address[0]
        if ip_address not in self.users:
            user = self.canvas.user_class(ip_address, self.canvas)
            self.users[ip_address] = user
        else:
            user = self.users[ip_address]
        method_name = 'handle' + message.address.replace('/', '_')
        method = getattr(user, method_name, None)
        if method:
            method(*message.getValues())
        else:
            print("  Got unhandled method %s from %s" % (message, address))


try:
    touchpad = open('/var/www/touchpad.html').read()
except Exception:
    touchpad = ""

class HTTPServer(Resource):
    isLeaf = True
    def render_GET(self, request):
        return self.render_POST(request)
    def render_POST(self, request):
        return self.handle(request.args, request.getClientIP(), request.uri)


    def handle(self, message, ip_address, address):
        if address == "/touchpad.html":
            return touchpad
        else:
            if ip_address not in app.users:
                user = self.user_class(ip_address, self.app.canvas, True)
                self.app.users[ip_address] = user
            else:
                user = self.app.users[ip_address]
            method_name = 'handle' + address.replace('/', '_')
            method = getattr(user, method_name, None)
            filter_method = getattr(self, method_name, None)

            if method and filter_method:
                message = filter_method(message)
                method(*message)
            else:
                print("  Got unhandled method %s from %s" % (message, address))

            return ""

    def handle_mouse(self, state):
        return (int(state['state'][0]), int(state['dx'][0]),
                int(state['dy'][0]))

    def handle_leftbutton(self, state):
        return [int(state['state'][0])]

    def handle_rightbutton(self, estado):
        return [int(state['state'][0])]

def start_http_server(app, user_class):
    web_server = HTTPServer()
    web_server.user_class = user_class
    web_server.app = app
    factory = server.Site(web_server)
    reactor.listenTCP(8888, factory)

def start(canvas, host):
    start_client(canvas, host)
    start_server(canvas, host)
    start_http_server(canvas.server, canvas.user_class)

    reactor.callWhenRunning(canvas.loop)
    reactor.run()

def start_server(canvas, host):
    canvas.server = UDPReceiverApplication(canvas, host)

def start_client(canvas, host):
    canvas.client = UDPSenderApplication(canvas, host)
