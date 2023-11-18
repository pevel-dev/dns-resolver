import socket
from dataclasses import dataclass


@dataclass
class AData:
    ip: str

    def pack(self) -> bytes:
        ip = self.ip.split('.')
        data = b''
        for i in ip:
            data += int.to_bytes(int(i), 1, byteorder='big')
        return data

    @staticmethod
    def parse(data: bytes, offset: int) -> tuple['AData', int]:
        return AData(socket.inet_ntoa(data[offset:offset + 4])), offset + 4
