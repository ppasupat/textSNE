#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
separate word file by categories

Example: if [inprefix].cats contains
    1
    2
    1
    3
    2
and [inprefix].words contains
    avocado
    banana
    carrot
    donut
    elderberry
The output [outdir]/1 will contain
    avocado
    carrot
The same goes for [outdir]/2 and [outdir]/3
'''

import sys, os, re, argparse, json
from codecs import open
from collections import defaultdict

def main():
    parser = argparse.ArgumentParser(description=__doc__,
            formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('inprefix')
    parser.add_argument('outdir')
    args = parser.parse_args()

    os.mkdir(args.outdir)
    with open(args.inprefix + '.cats') as fin:
        cats = [int(line) for line in fin]
    with open(args.inprefix + '.words') as fin:
        data = [line for line in fin]
    bins = defaultdict(list)
    for cat, datum in zip(cats, data):
        bins[cat].append(datum)
    for cat in bins:
        with open(os.path.join(args.outdir, '%02d' % cat), 'w') as fout:
            for datum in bins[cat]:
                fout.write(datum)

if __name__ == '__main__':
    main()
