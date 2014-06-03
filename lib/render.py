"""
Render t-SNE text labels.
Requires PIL (Python Imaging Library) or Pillow.
"""

import os, sys
from PIL import Image, ImageFont, ImageDraw, ImageChops

def render(points, filename, highlights, width=3000, height=2000,
           fontfile=None, fontsize=12, margin=0.05, anonymize=False):
    """
    Render t-SNE text points to an image file.
    points: a list of tuples of the form (title, x, y).
    filename: should be a .png, typically.
    margin: the amount of extra whitespace added at the edges.
    transparency: the amount of transparency in the text.
    """
    W = width
    H = height
    if not highlights:
        highlights = dict()

    im = Image.new("RGB", (W, H), (255, 255, 255))
    dr = ImageDraw.Draw(im)

    if fontfile is not None:
        assert os.path.exists(fontfile)
        font = ImageFont.truetype(fontfile, fontsize)
    else:
        font = None
    
    minx, maxx, miny, maxy = 0, 0, 0, 0
    for (title, x, y) in points:
        if minx > x: minx = x
        if maxx < x: maxx = x
        if miny > y: miny = y
        if maxy < y: maxy = y

    dx = maxx - minx
    dy = maxy - miny
    assert dx > 0
    assert dy > 0
    minx -= dx * margin
    miny -= dy * margin
    maxx += dx * margin
    maxy += dy * margin

    # Sort by highlight color (so that highlighted words are rendered last)
    points = sorted((int(pt[0] in highlights) * 255, pt) for pt in points)

    for (fill, pt) in points:
        (title, x, y) = pt
        x = 1. * (x - minx) / (maxx - minx) * W
        y = 1. * (y - miny) / (maxy - miny) * H
        if anonymize:
            title = 'X'
        if font:
            title = title.decode('utf8')
        pos = (x, y)
        dr.text(pos, title, font=font, fill=fill)
    
    print >> sys.stderr, "Rendering image to file", filename
    im.save(filename)
