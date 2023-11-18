import struct
from dataclasses import dataclass


@dataclass
class Headers:
    id: int
    qr: bool
    opcode: int
    aa: bool
    tc: bool
    rd: bool
    ra: bool
    z: int
    rcode: int
    qdcount: int
    ancount: int
    nscount: int
    arcount: int

    def pack(self) -> bytes:
        flags = (
            (self.qr << 15) |
            (self.opcode << 11) |
            (self.aa << 10) |
            (self.tc << 9) |
            (self.rd << 8) |
            (self.ra << 7) |
            (self.z << 4) |
            self.rcode
        )
        return struct.pack("!6H", self.id, flags, self.qdcount, self.ancount, self.nscount, self.arcount)

    @staticmethod
    def parse(data: bytes, offset: int) -> tuple['Headers', int]:
        id, flags, qdcount, ancount, nscount, arcount = struct.unpack_from("!6H", data, offset)

        qr = (flags & 0x8000) != 0
        opcode = (flags & 0x7800) >> 11
        aa = (flags & 0x0400) != 0
        tc = (flags & 0x200) != 0
        rd = (flags & 0x100) != 0
        ra = (flags & 0x80) != 0
        z = (flags & 0x70) >> 4
        rcode = flags & 0xF

        return Headers(id, qr, opcode, aa, tc, rd, ra, z, rcode, qdcount, ancount, nscount, arcount), offset + 12
