import time
from dataclasses import dataclass

from models.headers import Headers
from models.qname import QNameUtils
from models.question import Question
from models.resource_record import ResourceRecord


@dataclass
class ZoneServer:
    name: str
    address: str
    rtype: int
    expired_at: time


@dataclass
class Packet:
    headers: Headers
    questions: list[Question]
    answers: list[ResourceRecord]
    authorities: list[ResourceRecord]
    additions: list[ResourceRecord]

    def pack(self) -> bytes:
        qname_utils = QNameUtils()
        data = [self.headers.pack()]
        offset = 12
        for question in self.questions:
            b, offset = question.pack(offset, qname_utils)
            data.append(b)
        all_resource_records = self.answers + self.authorities + self.additions
        for record in all_resource_records:
            b, offset = record.pack(offset, qname_utils)
            data.append(b)
        return b''.join(data)

    @staticmethod
    def parse(data: bytes) -> 'Packet':
        qname_utils = QNameUtils()
        header, offset = Headers.parse(data, 0)

        questions = []
        for _ in range(header.qdcount):
            question, offset = Question.parse(data, offset, qname_utils)
            questions.append(question)

        resource_records = []
        for t in [header.ancount, header.nscount, header.arcount]:
            for _ in range(t):
                resource_record, offset = ResourceRecord.parse(data, offset, qname_utils)
                resource_records.append(resource_record)

        return Packet(
            header,
            questions,
            resource_records[:header.ancount],
            resource_records[header.ancount:header.nscount],
            resource_records[header.nscount:],
        )

    @staticmethod
    def get_error_packet(id: int, error_code: int) -> bytes:
        return Packet(
            Headers(id, True, 0, False, False, False, False, 0, error_code, 0, 0, 0, 0),
            questions=[], answers=[], additions=[], authorities=[]
        ).pack()
