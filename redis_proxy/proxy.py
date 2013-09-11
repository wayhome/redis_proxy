#!/usr/bin/env python
# coding: utf-8
# http://musta.sh/2012-03-04/twisted-tcp-proxy.html
import sys
import json
import itertools

from twisted.internet import defer
from twisted.internet import protocol
from twisted.internet import reactor
from twisted.python import log
import redis_protocol


readOnlyCommands = [
    'info', 'smembers', 'hlen', 'hmget', 'srandmember', 'hvals', 'randomkey', 'strlen',
    'dbsize', 'keys', 'ttl', 'lindex', 'type', 'llen', 'dump', 'scard', 'echo', 'lrange',
    'zcount', 'exists', 'sdiff', 'zrange', 'mget', 'zrank', 'get', 'getbit', 'getrange',
    'zrevrange', 'zrevrangebyscore', 'hexists', 'object', 'sinter', 'zrevrank', 'hget',
    'zscore', 'hgetall', 'sismember']


class ProxyClientProtocol(protocol.Protocol):
    def connectionMade(self):
        log.msg("Client: connected to peer")
        self.cli_queue = self.factory.cli_queue
        self.cli_queue.get().addCallback(self.serverDataReceived)

    def serverDataReceived(self, chunk):
        if chunk is False:
            self.cli_queue = None
            log.msg("Client: disconnecting from peer")
            self.factory.continueTrying = False
            self.transport.loseConnection()
        elif self.cli_queue:
            log.msg("Client: writing %d bytes to peer" % len(chunk))
            self.transport.write(chunk)
            self.cli_queue.get().addCallback(self.serverDataReceived)
        else:
            self.factory.cli_queue.put(chunk)

    def dataReceived(self, chunk):
        log.msg("Client: %d bytes received from peer" % len(chunk))
        self.factory.srv_queue.put(chunk)

    def connectionLost(self, why):
        if self.cli_queue:
            self.cli_queue = None
            log.msg("Client: peer disconnected unexpectedly")


class ProxyClientFactory(protocol.ReconnectingClientFactory):
    maxDelay = 10
    continueTrying = True
    protocol = ProxyClientProtocol

    def __init__(self, srv_queue, cli_queue):
        self.srv_queue = srv_queue
        self.cli_queue = cli_queue


class ProxyServerProtocol(protocol.Protocol):
    def __init__(self, factory):
        self.factory = factory

    def connectionMade(self):
        self.srv_queue = defer.DeferredQueue()
        self.srv_queue.get().addCallback(self.clientDataReceived)
        self.master_cli_queue = defer.DeferredQueue()
        self.slave_cli_queues = []

        factory = ProxyClientFactory(self.srv_queue, self.master_cli_queue)
        master_settings = self.factory.master_settings
        reactor.connectTCP(master_settings["host"], master_settings["port"], factory)

        for slave_settings in self.factory.slave_settings:
            slave_cli_queue = defer.DeferredQueue()
            self.slave_cli_queues.append(slave_cli_queue)
            factory = ProxyClientFactory(self.srv_queue, slave_cli_queue)
            reactor.connectTCP(slave_settings["host"], slave_settings["port"], factory)

        self.iter_slave_cli_queues = itertools.cycle(self.slave_cli_queues)

    def clientDataReceived(self, chunk):
        log.msg("Server: writing %d bytes to original client" % len(chunk))
        self.transport.write(chunk)
        self.srv_queue.get().addCallback(self.clientDataReceived)

    def dataReceived(self, chunk):
        log.msg("Server: %d bytes received" % len(chunk))
        command = redis_protocol.decode(chunk)[0]
        log.msg("command: %s" % command)
        if command.lower() in readOnlyCommands:
            slave_cli_queue = self.iter_slave_cli_queues.next()
            slave_cli_queue.put(chunk)
        else:
            self.master_cli_queue.put(chunk)

    def connectionLost(self, why):
        self.master_cli_queue.put(False)
        for slave_cli_queue in self.slave_cli_queues:
            slave_cli_queue.put(False)


class ProxyServerFactory(protocol.Factory):

    def __init__(self, master_settings, slave_settings):
        self.master_settings = master_settings
        self.slave_settings = slave_settings

    def buildProtocol(self, addr):
        return ProxyServerProtocol(self)


if __name__ == "__main__":
    log.startLogging(sys.stdout)
    config = json.load(file(sys.argv[1]))
    for server_setting in config:
        reactor.listenTCP(server_setting["listen"], ProxyServerFactory(server_setting["master"], server_setting["slave"]), interface="0.0.0.0")
    reactor.run()
