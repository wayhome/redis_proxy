#!/usr/bin/env python
# encoding: utf-8
import sys
import json
from twisted.python import usage
from twisted.python import log
from twisted.internet import reactor
from .proxy import ProxyServerFactory


class Options(usage.Options):

    optParameters = [
        ["config", "c", "config.json", "server config file"]
    ]


def run():
    option = Options()
    try:
        option.parseOptions()
    except usage.UsageError, errortext:
        print '%s: %s' % (sys.argv[0], errortext)
        print '%s: Try --help for usage details.' % (sys.argv[0])
        sys.exit(1)
    log.startLogging(sys.stdout)
    config = json.load(file(option["config"]))
    for server_setting in config:
        reactor.listenTCP(server_setting["listen"], ProxyServerFactory(server_setting["master"], server_setting["slave"]), interface="0.0.0.0")
    reactor.run()

if __name__ == '__main__':
    run()
