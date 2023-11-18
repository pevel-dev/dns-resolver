import struct
from dataclasses import dataclass

from models.qname import QNameUtils


@dataclass
class Question:
    name: str
    qtype: int
    qclass: int

    def pack(self, offset: int, utils: QNameUtils) -> tuple[bytes, int]:
        data = []
        name, offset = utils.pack(self.name, offset)
        data.append(name)
        data.append(int.to_bytes(self.qtype, 2, 'big'))
        data.append(int.to_bytes(self.qclass, 2, 'big'))

        return b''.join(data), offset + 4

    @staticmethod
    def parse(data: bytes, offset: int, utils: QNameUtils) -> tuple['Question', int]:
        name, offset = utils.parse(data, offset)

        qtype, qclass = struct.unpack_from('!2H', data, offset)

        return Question(name, qtype, qclass), offset + 4
