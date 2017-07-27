from dnslib import RR, QTYPE, A


class DatabaseLookupResolver:
    def __init__(self, storage, zone, keymaker=None, ttl=60):
        self.storage = storage
        self.zone = zone
        self.keymaker = keymaker
        self.ttl = ttl

    def resolve(self, request, handler):
        reply = request.reply()
        key = (
            self.keymaker(request, handler) if self.keymaker
            else str(request.q.qname)
        )
        address = self.storage.get(key)
        if address is not None:
            reply.add_answer(
                RR(self.zone, QTYPE.A, rdata=A(address), ttl=self.ttl)
            )
        return reply


def main():
    import argparse
    import json
    import time
    from importlib import import_module

    from dnslib.server import DNSLogger, DNSServer

    from labDNS.storages import RedisStorage, DictStorage

    parser = argparse.ArgumentParser(
        description="Database lookup based DNS resolver"
    )

    parser.add_argument(
        "--storage", "-s", default='dict', choices=['redis', 'dict']
    )
    parser.add_argument("--config", "-c", type=json.loads, default=dict())
    parser.add_argument("--zone", "-z")
    parser.add_argument("--ttl", "-t", default=10, type=int)
    parser.add_argument("--log", "-l", default="request,reply,truncated,error")
    parser.add_argument("--port", "-p", default=53, type=int)
    parser.add_argument("--address", "-a", default="localhost")
    parser.add_argument("--keymaker", "-k", default=None)

    args = parser.parse_args()

    config = args.config

    if args.storage == 'redis':
        storage = RedisStorage(config)
    elif args.storage == 'dict':
        storage = DictStorage(config)

    keymaker = import_module(args.keymaker).keymaker if args.keymaker else None

    resolver = DatabaseLookupResolver(
        storage, args.zone, ttl=args.ttl, keymaker=keymaker
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
