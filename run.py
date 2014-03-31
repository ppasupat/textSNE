#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, re, argparse, json
from codecs import open
from collections import defaultdict

import numpy as np
from lib import calc_tsne, render

def read_combined(fin, limit=0):
    titles, x = [], []
    num_words, num_dims = [float(f) for f in fin.readline().split()]
    for i, line in enumerate(fin):
        if line.strip():
            toks = line.strip().split()
            titles.append(toks[0])
            x.append([float(f) for f in toks[1:]])
        if i >= limit:
            break
    assert len(titles) == len(x)
    assert all(len(row) == num_dims for row in x)
    x = np.array(x)
    return titles, x

def read_separated(fwords, fWe, limit=0):
    titles, x = [], []
    for i, line in enumerate(fwords):
        if line.strip():
            titles.append(line.strip())
        if i >= limit:
            break
    for i, line in enumerate(fWe):
        if line.strip():
            x.append([float(f) for f in line.strip().split()])
        if i >= limit:
            break
    assert len(titles) == len(x)
    assert all(len(row) == len(x[0]) for row in x)
    x = np.array(x)
    return titles, x

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('inputs', nargs='+',
                        help='either [embedding] or [input.words] [input.We]')
    parser.add_argument('output',
                        help='output filename [outfile.png]')
    parser.add_argument('-l', '--limit', metavar='L', type=int,
                        help='limit to the first L words', default=500)
    parser.add_argument('-n', '--normalize', action='store_true',
                        help='normalize each word vector to unit L2 norm')
    parser.add_argument('-f', '--fast', action='store_true',
                        help='ignore transparency to speed up rendering')
    args = parser.parse_args()

    if len(args.inputs) == 1:
        i_emb = args.inputs[0]
        with open(i_emb, 'rb') as fin:
            print 'Reading combined data from %s ...' % i_emb
            titles, x = read_combined(fin, limit=args.limit)
    elif len(args.inputs) == 2:
        i_words, i_We = args.inputs
        with open(i_words, 'rb') as fwords:
            print 'Reading vocab from %s ...' % i_words
            with open(i_We, 'rb') as fWe:
                print 'Reading vectors from %s ...' % i_We
                titles, x = read_separated(fwords, fWe, limit=args.limit)
    else:
        parser.print_usage()
        exit(1)

    if args.normalize:
        x /= np.sqrt((x ** 2).sum(-1))[:, np.newaxis]
    
    out = calc_tsne.tsne(x, no_dims=2, perplexity=30, initial_dims=30)
    data = [(title, point[0], point[1]) for (title, point) in zip(titles, out)]
    render.render(data, args.output, transparency=(0 if args.fast else 0.4))

if __name__ == '__main__':
    main()
