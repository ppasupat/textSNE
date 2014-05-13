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
        if i >= limit:
            break
        if line.strip():
            toks = line.strip().split()
            titles.append(toks[0])
            x.append([float(f) for f in toks[1:]])
    assert len(titles) == len(x)
    assert all(len(row) == num_dims for row in x)
    x = np.array(x)
    return titles, x

def read_separated(fwords, fWe, limit=0):
    titles, x = [], []
    for i, line in enumerate(fwords):
        if i >= limit:
            break
        if line.strip():
            titles.append(line.strip())
    for i, line in enumerate(fWe):
        if i >= limit:
            break
        if line.strip():
            x.append([float(f) for f in line.strip().split()])
    assert len(titles) == len(x)
    assert all(len(row) == len(x[0]) for row in x)
    x = np.array(x)
    return titles, x

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('inputs', nargs='+',
                        help='either [embedding] or [input.We] [input.words]')
    parser.add_argument('output',
                        help='output filename [outfile.png]')
    parser.add_argument('-l', '--limit', metavar='L', type=int,
                        help='limit to the first L words', default=500)
    parser.add_argument('-n', '--normalize', action='store_true',
                        help='normalize each word vector to unit L2 norm')
    parser.add_argument('-f', '--fast', action='store_true',
                        help='ignore transparency to speed up rendering')
    parser.add_argument('-F', '--font', help='path to font file')
    parser.add_argument('-p', '--pca', type=int, default=0,
                        help='perform PCA with this number of dimensions'
                        'before calling SNE')
    parser.add_argument('-s', '--scale', type=float, default=1.0,
                        help='scale up the image by this factor')
    args = parser.parse_args()

    if len(args.inputs) == 1:
        i_emb = args.inputs[0]
        with open(i_emb, 'rb') as fin:
            print 'Reading combined data from %s ...' % i_emb
            titles, x = read_combined(fin, limit=args.limit)
    elif len(args.inputs) == 2:
        i_We, i_words = args.inputs
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
    
    out = calc_tsne.tsne(x, use_pca=bool(args.pca), initial_dims=args.pca)
    data = [(title, point[0], point[1]) for (title, point) in zip(titles, out)]
    render.render(data, args.output, transparency=(0 if args.fast else 0.4),
                  width=int(3000*args.scale), height=int(2000*args.scale),
                  fontfile=args.font)

if __name__ == '__main__':
    main()
