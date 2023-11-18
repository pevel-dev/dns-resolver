from dataclasses import dataclass

from models.qname import QNameUtils


@dataclass
class NSData:
    name: str

    def pack(self) -> bytes:
        pass

    @staticmethod
    def parse(data: bytes, offset: int) -> tuple['NSData', int]:
        utils = QNameUtils()
        name, offset = utils.parse(data, offset)
        return NSData(name), offset
