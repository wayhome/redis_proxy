#!/usr/bin/env python
# encoding: utf-8
DELIMITER = "\r\n"

readOnlyCommands = [
    'info', 'smembers', 'hlen', 'hmget', 'srandmember', 'hvals', 'randomkey', 'strlen',
    'dbsize', 'keys', 'ttl', 'lindex', 'type', 'llen', 'dump', 'scard', 'echo', 'lrange',
    'zcount', 'exists', 'sdiff', 'zrange', 'mget', 'zrank', 'get', 'getbit', 'getrange',
    'zrevrange', 'zrevrangebyscore', 'hexists', 'object', 'sinter', 'zrevrank', 'hget',
    'zscore', 'hgetall', 'sismember']


def parse(data):
    processed, index = 0, data.find(DELIMITER)
    if index == -1:
        index = len(data)
    term = data[processed]
    if term == "*":
        return parse_multi_chunked(data)
    elif term == "$":
        return parse_chunked(data)
    elif term == "+":
        return parse_status(data)
    elif term == "-":
        return parse_error(data)
    elif term == ":":
        return parse_integer(data)


def parse_multi_chunked(data):
    index = data.find(DELIMITER)
    count = int(data[1:index])
    result = []
    start = index + len(DELIMITER)
    for i in range(count):
        chunk, length = parse_chunked(data, start)
        start = length + len(DELIMITER)
        result.append(chunk)
    return result


def parse_chunked(data, start=0):
    index = data.find(DELIMITER, start)
    if index == -1:
        index = start
    length = int(data[start + 1:index])
    if length == -1:
        return None
    else:
        result = data[index + len(DELIMITER):index + len(DELIMITER) + length]
        return result if start == 0 else [result, index + len(DELIMITER) + length]


def parse_status(data):
    return [True, data[1:]]


def parse_error(data):
    return [False, data[1:]]


def parse_integer(data):
    return [int(data[1:])]
