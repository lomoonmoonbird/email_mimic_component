#! --*-- coding: utf-8 --*--

import re
from collections import Counter

def left_judge(response_map, threshold=2, total=2):
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
        f = dict(filter(lambda x: x[1] > total - 1, c.items()))
    if f:
        return list(msg)
    return []


def right_jedge():
    """右括号裁决"""

