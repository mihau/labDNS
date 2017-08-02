# labDNS
DNS Server that returns records based on lookups in configured storage.

This tool provides an intercepting DNS server that allows to override DNS query
results for a defined zone. The results are looked up in the configured storage
(currently supporting dict, Redis and Consul). It is possible to specify
custom functions to create lookup keys and to process the results.

## Usage
For the usage please refer to `labDNS --help`. Note that `config` option
expects json input that is used to init storages.

    usage: labDNS [-h] [--storage {redis,consul,dict}] [--config CONFIG]
                  [--zone ZONE] [--ttl TTL] [--log LOG] [--port PORT]
                  [--address ADDRESS] [--keymaker KEYMAKER]
                  [--processor PROCESSOR] [--upstream UPSTREAM]

    Database lookup based DNS resolver

    optional arguments:
      -h, --help            show this help message and exit
      --storage {redis,consul,dict}, -s {redis,consul,dict}
      --config CONFIG, -c CONFIG
      --zone ZONE, -z ZONE
      --ttl TTL, -t TTL
      --log LOG, -l LOG
      --port PORT, -p PORT
      --address ADDRESS, -a ADDRESS
      --keymaker KEYMAKER, -k KEYMAKER
      --processor PROCESSOR
      --upstream UPSTREAM, -u UPSTREAM

## Example
    labDNS --zone "*.foo.bar.com" --port 53 -s redis --keymaker labDNS.keymakers.client_ip --processor labDNS.processors.resolve --upstream 8.8.8.8
