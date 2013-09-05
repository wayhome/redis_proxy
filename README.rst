redis_proxy
================
A redis proxy that supprot read/write splitting. It works like haproxy,
but only used with redis.For now it's a very rough project.

Usage
===============
redis-proxy -c config.json

Config Example
===============
For example::

    [
     {"listen": 6378, 
      "master":{"host": "host01", "port": 6378},
      "slave": [{"host": "host02", "port": 6380}]
     },
     {"listen": 6377, 
      "master":{"host": "host01", "port": 6379},
      "slave": [{"host": "host02", "port": 6380}, {"host": "host03", "port": 6380}]
     }
    ]

The proxy will listen on port 6377 and 6378, and forward read to the slave, write to the master.
