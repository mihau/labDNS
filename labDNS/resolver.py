import socket
from pydoc import locate

from dnslib import RR, QTYPE, A, DNSRecord, RCODE


class DatabaseLookupResolver:
    def __init__(self, storage, zone, keymaker=None, ttl=60, upstream=None,
                 processor=None, bypass=None):
        self.storage = storage
        self.zone = zone
        self.keymaker = keymaker
        self.ttl = ttl
        self.upstream = upstream
        self.processor = processor
        self.bypass = bypass or []

    def resolve(self, request, handler):
        reply = request.reply()
        qname = request.q.qname
        if any([qname.matchGlob(pattern) for pattern in self.bypass]):
            pass
        elif qname.matchGlob(self.zone):
            key = (
                self.keymaker(request, handler, self.storage) if self.keymaker
                else str(qname)
            )
            storage_result = self.storage.get(key)
            address = (
                self.processor(storage_result) if self.processor
                else storage_result
            )
            if address is not None:
                reply.add_answer(
                    RR(qname, QTYPE.A, rdata=A(address), ttl=self.ttl)
                )

        if self.upstream and not reply.rr:
            try:
                if handler.protocol == 'udp':
                    proxy_r = request.send(
                        self.upstream, port=53, timeout=60
                    )
                else: proxy_r = request.send(
                        self.upstream, port=53, tcp=True, timeout=60
                    )
                reply = DNSRecord.parse(proxy_r)
            except socket.timeout:
                reply.header.rcode = getattr(RCODE, 'NXDOMAIN')
        return reply


def main():
    import argparse
    import json
    import time
    from importlib import import_module

    from dnslib.server import DNSLogger, DNSServer

    parser = argparse.ArgumentParser(
        description="Database lookup based DNS resolver"
    )

    parser.add_argument(
        "--storage", "-s", default='labDNS.storages.DictStorage'
    )
    parser.add_argument("--config", "-c", type=json.loads, default=dict())
    parser.add_argument("--zone", "-z")
    parser.add_argument("--ttl", "-t", default=10, type=int)
    parser.add_argument("--log", "-l", default="request,reply,truncated,error")
    parser.add_argument("--port", "-p", default=53, type=int)
    parser.add_argument("--address", "-a", default="localhost")
    parser.add_argument("--keymaker", "-k", default=None)
    parser.add_argument("--processor", default=None)
    parser.add_argument("--upstream", "-u", default=None)
    parser.add_argument("--bypass", "-b", default=[], nargs='+')

    args = parser.parse_args()

    config = args.config

    Storage = locate(args.storage)
    storage = Storage(config)

    keymaker = import_module(args.keymaker).keymaker if args.keymaker else None
    processor = (
        import_module(args.processor).processor if args.processor else None
    )

    resolver = DatabaseLookupResolver(
        storage,
        args.zone,
        ttl=args.ttl,
        keymaker=keymaker,
        upstream=args.upstream,
        processor=processor,
        bypass=args.bypass,
    )
    logger = DNSLogger(args.log)

    server = DNSServer(
        resolver,
        port=args.port,
        address=args.address,
        logger=logger,
    )

    server.start_thread()

    while server.isAlive():
        time.sleep(1)

if __name__ == '__main__':
    main()
