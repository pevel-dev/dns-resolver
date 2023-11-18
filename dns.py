import argparse
import asyncio

from server import DNSServer

parser = argparse.ArgumentParser('DNS')

parser.add_argument('--bind', default='0.0.0.0', type=str)
parser.add_argument('--port', default=53, type=int)
parser.add_argument('--timeout', default=2, type=float)
parser.add_argument('--retry_count', default=2, type=int)
parser.add_argument('--max_hops', default=10, type=int)


async def main(args):
    dns = DNSServer(args.timeout, args.retry_count, args.max_hops)
    await dns.listen(args.bind, args.port)


if __name__ == "__main__":
    args = parser.parse_args()
    asyncio.run(main(args))
