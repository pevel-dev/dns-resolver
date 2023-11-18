import random
import socket
import time
from dataclasses import dataclass

from models.headers import Headers
from models.packet import Packet
from models.question import Question
from models.resource_record import ResourceRecord

YEAR_IN_SECONDS = 60 * 60 * 24 * 365


@dataclass
class ZoneRecord:
    address: str
    expired_at: time.time


@dataclass
class ZoneInfo:
    name: str
    records: list[ZoneRecord]


@dataclass
class AddressInfo:
    records: list[ResourceRecord]


class Resolver:
    def __init__(self, hops, timeout, retry_count):
        self.zone_info_cache: dict[str, ZoneInfo] = dict()
        self.address_info_cache: dict[str, AddressInfo] = dict()
        self.zone_info_cache['.'] = ZoneInfo('.', [ZoneRecord('192.5.5.241', time.time() + YEAR_IN_SECONDS)])

        self.MAX_HOPS = hops
        self.TIMEOUT = timeout
        self.RETRY_COUNT = retry_count

    def resolve_address(self, address: str) -> list[ResourceRecord] | None:
        last_zone = self.zone_info_cache['.']
        zones = address.split('.')

        zone_index = len(zones) - 1
        hops = 0
        while True:
            search_zone = '.'.join(zones[zone_index:])
            new_zone, answer = self.resolve_zone(address, search_zone, last_zone)
            if answer:
                return answer.records
            elif new_zone:
                last_zone = new_zone
            else:
                return list()  # error

            if zone_index != 0:
                zone_index -= 1
            hops += 1
            if hops > self.MAX_HOPS:
                return list()  # error

    def resolve_zone(
            self,
            zone: str,
            cache_zone: str,
            last_zone: ZoneInfo
    ) -> tuple[ZoneInfo, None] | tuple[None, AddressInfo] | tuple[None, None]:
        if address_cache_info := self.check_in_cache(self.address_info_cache, cache_zone):
            return None, address_cache_info
        if (cache_zone != last_zone.name) and (
        zone_cache_info := self.check_in_cache(self.zone_info_cache, cache_zone)):
            return zone_cache_info, None
        packet: Packet = None
        for record in last_zone.records:
            packet_answer = self.dns_query(zone, record.address)
            if packet_answer:
                packet = packet_answer
                break

        if not packet:
            return None, None
        if len(packet.answers) != 0 and (answer := self.parse_address_info(packet)):
            self.address_info_cache[cache_zone] = answer
            return None, answer
        if (len(packet.additions) != 0 or len(packet.authorities) != 0) and (
                zone_info := self.parse_zone_info(cache_zone, packet)):
            self.zone_info_cache[cache_zone] = zone_info
            return zone_info, None
        return None, None

    def dns_query(self, query: str, address: str):
        for _ in range(self.RETRY_COUNT):
            try:
                dns_packet = Packet(
                    Headers(random.randint(0, 16000), False, 0, False, False, False, False, 0, 0, 1, 0, 0, 0),
                    [Question(query, 1, 1)], [], [], []
                )
                packet_dns = dns_packet.pack()

                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(self.TIMEOUT)
                sock.sendto(packet_dns, (address, 53))

                start_time = time.time()
                while time.time() - start_time < self.TIMEOUT:
                    data = sock.recv(4096)
                    if data:
                        return Packet.parse(data)
            except Exception as ex:
                print(ex)
                continue

        return None

    def parse_zone_info(self, name: str, packet: Packet) -> ZoneInfo:
        ns_servers = set()
        for authority_resource_record in packet.authorities:
            if authority_resource_record.rrtype == 2:  # NS
                ns_servers.add(authority_resource_record.rdata.name)

        records = []

        for additional_resource_record in packet.additions:
            if additional_resource_record.rrtype == 1 and additional_resource_record.name in ns_servers:  # A
                records.append(ZoneRecord(additional_resource_record.rdata.ip, additional_resource_record.expired_at))
            if additional_resource_record.rrtype == 2:
                ns_servers.add(additional_resource_record.rdata.name)

        if len(ns_servers) != 0 and len(records) == 0:
            while len(ns_servers) > 0:
                addr = ns_servers.pop()
                resource_records = self.resolve_address(addr)
                for rr in resource_records:
                    records.append(ZoneRecord(rr.rdata.ip, rr.expired_at))

        if len(records) > 0:
            return ZoneInfo(name, records)

    @staticmethod
    def parse_address_info(packet: Packet) -> AddressInfo:
        records = []

        for answer_resource_record in packet.answers:
            if answer_resource_record.rrtype == 1:  # A
                records.append(answer_resource_record)

        if len(records) > 0:
            return AddressInfo(records)

    @staticmethod
    def check_in_cache(cache: dict, query: str):  # check AddressInfo or ZoneInfo
        if cache_info := cache.get(query):
            answer = []
            for resource_record in cache_info.records:
                if time.time() < resource_record.expired_at:
                    answer.append(resource_record)
            if len(answer) > 0:
                return ZoneInfo(query, answer)
