#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, re, argparse, json
from codecs import open
from collections import defaultdict

import numpy as np
from lib import calc_tsne, render

def read_combined(fin, limit=0, highlights=None):
    titles, x = [], []
    remaining_highlights = set(highlights)
    num_words, num_dims = [float(f) for f in fin.readline().split()]
    for i, line in enumerate(fin):
        if i >= limit and not remaining_highlights:
            break
        if line.strip():
            toks = line.strip().split()
            titles.append(toks[0])
            x.append([float(f) for f in toks[1:]])
            remaining_highlights.discard(toks[0])
    assert len(titles) == len(x)
    assert all(len(row) == num_dims for row in x)
    x = np.array(x)
    return titles, x

def read_separated(fwords, fWe, limit=0, highlights=None):
    titles, x = [], []
    remaining_highlights = set(highlights)
    i = 0
    while True:
        word = fwords.readline().strip()
        vec = fWe.readline().strip()
        if not word or not vec or (i >= limit and not remaining_highlights):
            break
        if i < limit or word in remaining_highlights:
            titles.append(word)
            x.append([float(f) for f in vec.split()])
            remaining_highlights.discard(word)
        i += 1
    assert len(titles) == len(x)
    assert all(len(row) == len(x[0]) for row in x)
    x = np.array(x)
    return titles, x

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('inputs', nargs='+',
                        help='either [embedding] or [input.We] [input.words]')
    parser.add_argument('outdir', help='output directory')
    parser.add_argument('-l', '--limit', metavar='L', type=int,
                        help='limit to the first L words', default=500)
    parser.add_argument('-n', '--normalize', action='store_true',
                        help='normalize each word vector to unit L2 norm')
    parser.add_argument('-p', '--pca', type=int, default=0,
                        help='perform PCA with this number of dimensions'
                        'before calling SNE')
    parser.add_argument('-H', '--highlights', metavar='FILENAME', nargs='+',
                        help='load words to highlight from files')
    args = parser.parse_args()

    highlights = []
    all_highlight_words = set()
    for filename in args.highlights:
        with open(filename, 'r') as fin:
            highlight_words = set()
            for line in fin:
                line = line.strip()
                if line:
                    highlight_words.add(line)
            print 'Read %d highlight words from %s!' % \
                (len(highlight_words), filename)
            highlights.append((os.path.basename(filename), highlight_words))
            all_highlight_words.update(highlight_words)

    if len(args.inputs) == 1:
        i_emb = args.inputs[0]
        with open(i_emb, 'rb') as fin:
            print 'Reading combined data from %s ...' % i_emb
            titles, x = read_combined(fin, limit=args.limit,
                                      highlights=all_highlight_words)
    elif len(args.inputs) == 2:
        i_We, i_words = args.inputs
        with open(i_words, 'rb') as fwords:
            print 'Reading vocab from %s ...' % i_words
            with open(i_We, 'rb') as fWe:
                print 'Reading vectors from %s ...' % i_We
                titles, x = read_separated(fwords, fWe, limit=args.limit,
                                           highlights=all_highlight_words)
    else:
        parser.print_usage()
        exit(1)
    print 'Read %d words!' % len(titles)

    if args.normalize:
        x /= np.sqrt((x ** 2).sum(-1))[:, np.newaxis]
    
    out = calc_tsne.tsne(x, use_pca=bool(args.pca), initial_dims=args.pca)
    data = [(title, point[0], point[1]) for (title, point) in zip(titles, out)]
    for filename, highlight_words in highlights:
        filename = os.path.join(args.outdir, filename + '.png')
        render.render(data, filename, highlight_words)

if __name__ == '__main__':
    main()
