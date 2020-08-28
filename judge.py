#! --*-- coding: utf-8 --*--

import re
from collections import Counter
import ast
import json
from collections import defaultdict
import redis

def left_judge_bak(response_map, threshold=3, total=3):
    """左括号裁决"""
    f = {}
    len_response_map = len(response_map)
    if len_response_map >= threshold:
        hds = []
        for fd, msg in response_map.items():
            msg_str = str(msg)
            msg_str = re.sub(r'\(.*\)', "", msg_str)
            hds.append(msg_str)
        c = Counter(hds)
        f = list(dict((filter(lambda x: x[1] > total - 1, c.items()))))
        f[0] = f[0].strip("]['").split(', ')
    if f:
        return f[0] if not isinstance(f[0], list) else f[0]
    return []

def left_judge(response_map, threshold=3, total=3, switch='on'):
    """左括号裁决"""
    keys = list(response_map.keys())
    if not keys:
        return []
    if switch == 'on':
        from itertools import combinations
        combin_keys = list(combinations(keys, 2))
        same_count = 0
        counter = []
        if len(keys) >= threshold:
            for ck in combin_keys:
                if set(response_map[ck[0]][:-1]) == set(response_map[ck[1]][:-1]):
                    same_count += 1
                    counter.append(ck[0])
                    counter.append(ck[1])
            if same_count >= total - 1:
                a = Counter(counter)
                a = sorted(a.items(), key=lambda x:x[0], reverse=True)
                key = a[0][0]
                return response_map[key]
        return []
    # print(keys, response_map)
    return response_map[keys[1]]

client = redis.Redis(host='rproxy.moonmoonbird.com', port=6379, db=0)

def right_judge(data, threshold=3, total=3):
    """右括号裁决"""
    keys = list(set(data.keys()))
    if len(keys) == total:
        if data[keys[0]] != data[keys[1]]:
            return data[keys[0]]
        elif data[keys[0]] != data[keys[2]] and total == 3:
            return data[keys[0]]
        elif data[keys[1]] != data[keys[2]] and total == 3:
            return data[keys[1]]
    return ''