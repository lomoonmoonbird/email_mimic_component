#! --*-- coding: utf-8 --*--

import re
from collections import Counter
import ast
import json
from collections import defaultdict

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

def left_judge(response_map, threshold=3, total=3):
    """左括号裁决"""
    keys = list(response_map.keys())
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


def right_judge(tag, share_data, threshold=3, total=3):
    """右括号裁决"""
    # f = {}
    # if len(mails) >= total:
    #     hds = []
    #     for mail in mails:
    #         msg_str = str(mail)
    #         msg_str = re.sub(r'\(.*\)', "", msg_str)
    #         hds.append(msg_str)
    #     c = Counter(hds)
    #     f = list(dict(filter(lambda x: x[1] > total - 1, c.items())))
    #     print(f)
    # if f:
    #     return f[0] if not isinstance(f[0], list) else f[0]
    # return []
    tag_data = share_data[tag]
    tags = tag_data['tags']
    mails = tag_data['mails']

    if len(tags) == total:
        if tags[0] == tags[1]:
            share_data['same'].append(0)
            share_data['same'].append(1)
        if tags[0] == tags[2]:
            share_data['same'].append(0)
            share_data['same'].append(2)
        if tags[1] == tags[2]:
            share_data['same'].append(1)
            share_data['same'].append(2)
    share_data['same'] = list(set(share_data['same']))
    if len(share_data['same']) >= threshold - 1:
        share_data[tag]['choice'] = mails[share_data['same'][0]]


