#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, re, argparse, json, random
from codecs import open
from collections import defaultdict

import numpy as np
from lib import calc_tsne, render

def combined_reader(fin):
    def reader():
        print fin.readline().split()
        for line in fin:
            toks = line.strip().split()
            if toks:
                yield (toks[0], [float(f) for f in toks[1:]])
    return reader

def separated_reader(fWe, fwords):
    def reader():
        while True:
            word = fwords.readline().strip()
            vec = fWe.readline().strip()
            if not word or not vec:
                break
            yield (word, [float(f) for f in vec.split()])
    return reader

def read_data(reader, limit=0, highlights=None, random_threshold=0.0):
    titles, x = [], []
    remaining_highlights = set(highlights)
    non_highlight_count = 0
    for i, (word, vec) in enumerate(reader()):
        if non_highlight_count >= limit and not remaining_highlights:
            break
        if word in remaining_highlights:
            titles.append(word)
            x.append(vec)
            remaining_highlights.discard(word)
        elif non_highlight_count < limit and random.random() > random_threshold:
            titles.append(word)
            x.append(vec)
            non_highlight_count += 1
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
    parser.add_argument('-r', '--random-threshold', type=float, default=0.0,
                        help='randomly ignore words with this probability'
                        'when finding top L words')
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
            titles, x = read_data(combined_reader(fin),
                                  limit=args.limit,
                                  highlights=all_highlight_words,
                                  random_threshold=args.random_threshold)
    elif len(args.inputs) == 2:
        i_We, i_words = args.inputs
        with open(i_words, 'rb') as fwords:
            print 'Reading vocab from %s ...' % i_words
            with open(i_We, 'rb') as fWe:
                print 'Reading vectors from %s ...' % i_We
                titles, x = read_data(separated_reader(fWe, fwords),
                                      limit=args.limit,
                                      highlights=all_highlight_words,
                                      random_threshold=args.random_threshold)
    else:
        parser.print_usage()
        exit(1)
    print 'Read %d words!' % len(titles)

    if args.normalize:
        x /= np.sqrt((x ** 2).sum(-1))[:, np.newaxis]
    
    out = calc_tsne.tsne(x, use_pca=bool(args.pca), initial_dims=args.pca)
    data = [(title, point[0], point[1]) for (title, point) in zip(titles, out)]
    if not os.path.exists(args.outdir):
        os.makedirs(args.outdir)
    for filename, highlight_words in highlights:
        filename = os.path.join(args.outdir, filename + '.png')
        render.render(data, filename, highlight_words)

if __name__ == '__main__':
    main()
