"""
Render t-SNE text labels.
Requires PIL (Python Imaging Library) and ImageMagick "convert" command.
"""

import os, sys, string
from PIL import Image, ImageFont, ImageDraw, ImageChops

DEFAULT_FONT=None

import tempfile

def render(points, filename, width=3000, height=1800, fontfile=DEFAULT_FONT,
           fontsize=12, margin=0.05, transparency=0.4):
    """
    Render t-SNE text points to an image file.
    points is a list of tuples of the form (title, x, y).
    filename should be a .png, typically.
    margin is the amount of extra whitespace added at the edges.
    transparency is the amount of transparency in the text.
    @warning: Make sure you open the PNG in Gimp, or something that supports alpha channels. Otherwise, it will just look completely black.
    """
    W = width
    H = height

    im = Image.new("L", (W, H), 255)

    if fontfile is not None:
        assert os.path.exists(fontfile)
        font = ImageFont.truetype(fontfile, fontsize)
    
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

    alpha = Image.new("L", im.size, "black")

    for (idx, pt) in enumerate(points):
        (title, x, y) = pt
        x = 1. * (x - minx) / (maxx - minx) * W
        y = 1. * (y - miny) / (maxy - miny) * H

        # Make a grayscale image of the font, white on black.
        pos = (x, y)
        imtext = Image.new("L", im.size, 0)
        drtext = ImageDraw.Draw(imtext)
        if idx % 10 == 0:
            print >> sys.stderr, "\033[F\033[KRendering title (#%d): %s" % \
                (idx, repr(title))
        if fontfile is not None:
            drtext.text(pos, title, font=font, fill=(256-256*transparency))
        else:
            drtext.text(pos, title, fill=(256-256*transparency))

        # Add the white text to our collected alpha channel. Gray pixels around
        # the edge of the text will eventually become partially transparent
        # pixels in the alpha channel.
        alpha = ImageChops.add(alpha, imtext)
    
    im.paste(Image.new('L', im.size, 0), mask=alpha)
    print >> sys.stderr, "\033[F\033[KRendering image to file", filename
    im.save(filename)
