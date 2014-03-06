"""
Render t-SNE text labels.
Requires PIL (Python Imaging Library) or Pillow.
"""

import os, sys
from PIL import Image, ImageFont, ImageDraw, ImageChops

DEFAULT_FONT = None
BLACK = 0
WHITE = 255

def render(points, filename, width=3000, height=1800, fontfile=DEFAULT_FONT,
           fontsize=12, margin=0.05, transparency=0.4):
    """
    Render t-SNE text points to an image file.
    points: a list of tuples of the form (title, x, y).
    filename: should be a .png, typically.
    margin: the amount of extra whitespace added at the edges.
    transparency: the amount of transparency in the text.
    """
    W = width
    H = height

    im = Image.new("L", (W, H), WHITE)

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

    alpha = Image.new("L", im.size, BLACK)

    for (idx, pt) in enumerate(points):
        (title, x, y) = pt
        x = 1. * (x - minx) / (maxx - minx) * W
        y = 1. * (y - miny) / (maxy - miny) * H
        if idx % 10 == 0:
            print >> sys.stderr, "\033[F\033[KRendering title (#%d): %s" % \
                (idx, repr(title))
        
        # Make a grayscale image of the font, white on black.
        pos = (x, y)
        imtext = Image.new("L", im.size, BLACK)
        drtext = ImageDraw.Draw(imtext)
        drtext.text(pos, title, font=font, fill=(256-256*transparency))

        # Add the white text to our collected alpha channel. Gray pixels around
        # the edge of the text will eventually become partially transparent
        # pixels in the alpha channel.
        alpha = ImageChops.add(alpha, imtext)
    
    im.paste(Image.new('L', im.size, 0), mask=alpha)
    print >> sys.stderr, "\033[F\033[KRendering image to file", filename
    im.save(filename)
