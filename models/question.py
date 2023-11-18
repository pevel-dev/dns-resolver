import struct
from dataclasses import dataclass

from models.qname import QNameUtils


@dataclass
class Question:
    name: str
    qtype: int
    qclass: int

    def pack(self, offset: int, utils: QNameUtils) -> tuple[bytes, int]:
        data = b''
        name, offset = utils.pack(self.name, offset)
        data += name
        data += int.to_bytes(self.qtype, 2, 'big')
        data += int.to_bytes(self.qclass, 2, 'big')

        return data, offset + 4

    @staticmethod
    def parse(data: bytes, offset: int, utils: QNameUtils) -> tuple['Question', int]:
        name, offset = utils.parse(data, offset)

        qtype, qclass = struct.unpack_from('!2H', data, offset)

        return Question(name, qtype, qclass), offset + 4
