import socket
from dataclasses import dataclass


@dataclass
class AData:
    ip: str

    def pack(self) -> bytes:
        ip = self.ip.split('.')
        return b''.join(int.to_bytes(int(octet), 1, byteorder='big') for octet in ip)

    @staticmethod
    def parse(data: bytes, offset: int) -> tuple['AData', int]:
        return AData(socket.inet_ntoa(data[offset:offset + 4])), offset + 4
