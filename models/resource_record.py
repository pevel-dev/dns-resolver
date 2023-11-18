import struct
import time
from dataclasses import dataclass

from models.qname import QNameUtils
from models.rdata.a import AData
from models.rdata.ns import NSData


@dataclass
class ResourceRecord:
    name: str
    rrtype: int
    rrclass: int
    ttl: int
    rdlength: int
    rdata: AData | NSData
    expired_at: time

    def pack(self, offset: int, utils: QNameUtils) -> tuple[bytes, int]:
        data = b''
        name, offset = utils.pack(self.name, offset)
        data += name
        data += int.to_bytes(self.rrtype, 2, 'big')
        data += int.to_bytes(self.rrclass, 2, 'big')
        data += int.to_bytes(self.ttl, 4, 'big')
        data += int.to_bytes(self.rdlength, 2, 'big')
        if self.rrtype == 1:
            rdata_bytes = self.rdata.pack()
            data += rdata_bytes
        else:
            data += 0x00 * self.rdlength
            offset += self.rdlength
        return data, offset + 10 + self.rdlength

    @staticmethod
    def parse(data: bytes, offset: int, utils: QNameUtils) -> tuple['ResourceRecord', int]:
        name, offset = utils.parse(data, offset)
        rrtype, rclass, ttl, rdlength = struct.unpack_from("!2HIH", data, offset)
        offset += 10
        if rrtype == 1:  # A
            rdata, _ = AData.parse(data, offset)
        elif rrtype == 2:  # NS
            rdata, _ = NSData.parse(data, offset)
        else:
            rdata = 0x00 * rdlength
        return ResourceRecord(name, rrtype, rclass, ttl, rdlength, rdata, time.time() + ttl), offset + rdlength
