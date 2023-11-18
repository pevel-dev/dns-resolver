import logging
import socket
import socketserver
import threading
import time

from models.headers import Headers
from models.packet import Packet
from resolver import Resolver

logging.basicConfig(level=logging.INFO, filename="py_log.log", filemode="w")


class ThreadedUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    def __init__(self, server_address, request_handler_class, resolver: Resolver, bind_and_activate=True):
        super().__init__(server_address, request_handler_class, bind_and_activate)
        self.resolver = resolver


class DNSHandler(socketserver.BaseRequestHandler):

    def __init__(self, request, client_address, server: ThreadedUDPServer):
        super().__init__(request, client_address, server)
        self.start_time = None
        self.data = None
        self.socket: socket.SocketType = None
        self.resolver: Resolver = server.resolver

    def setup(self):
        self.start_time = time.time()
        self.data, self.socket = self.request[0], self.request[1]
        print(f'Start handle {self.client_address}')
        logging.info(f'Start handle {self.client_address}')

    def handle(self):
        try:
            parsed_packet = Packet.parse(self.data)
            if len(parsed_packet.answers) != 1:
                ...
                # TODO: error packet
            answer = self.server.resolver.resolve_address(parsed_packet.questions[0].name)
            print(answer)
            answer_packet = Packet(Headers(parsed_packet.headers.id, True, 0, False, False, False, False, 0, 0,
                                           parsed_packet.headers.qdcount, len(answer), 0, 0),
                                   questions=parsed_packet.questions, answers=answer, additions=[], authorities=[])
            answer_bytes = answer_packet.pack()
            self.socket.sendto(answer_bytes, self.client_address)

        except Exception as ex:
            print(ex)
            ...  # TODO: send error packet

    def finish(self):
        print(f'Handled {self.client_address} | {time.time() - self.start_time} seconds')
        logging.info(f'Handled {self.client_address} | {time.time() - self.start_time} seconds')


class DNSServer:
    def __init__(self, timeout, retry_count, max_hops):
        self.max_hops = max_hops
        self.retry_count = retry_count
        self.timeout = timeout

    async def listen(self, host='127.0.0.1', port=53):
        resolver = Resolver(self.max_hops, self.timeout, self.retry_count)
        server = ThreadedUDPServer((host, port), DNSHandler, resolver)

        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True

        try:
            server_thread.start()
            while True:
                time.sleep(100)
        except (KeyboardInterrupt, SystemExit):
            server.shutdown()
            server.server_close()
            exit()
