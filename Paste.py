#!/usr/bin/env python
# -*- coding: utf-8 -*-

#不指定输入的行数，但是必须以最后下一行只输入空格或者什么都不输入为结束
import sys
try:
    mx = []
    while True:
        m = sys.stdin.readline().strip()
        #若是多输入，strip()默认是以空格分隔，返回一个包含多个字符串的list。
        if m == 'quit':
            break
        m = list(m.split())
        mx.append(m)

xm = [ "" if len(c) == 0 else c for c in mx]

print(xm)

for i in xm:
    if isinstance(i, str):
        print(i)
    else:
        print(i[0])
except:
    pass
