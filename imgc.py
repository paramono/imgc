#!/usr/bin/env python3

from multiprocessing.dummy import Pool as ThreadPool
from PIL import Image

import sys, os, time
import argparse
import re

IMAGE_EXTS = ['jpg', 'jpeg', 'png', 'gif']
IMAGE_JPG  = ['jpg', 'jpeg']


def tofrac(x):
    """Convert percentage to floating point fraction"""
    return x/100.0


def size_parse_tuple(orig_image, new_size):
    if not new_size[0] and not new_size[1]: 
        raise ArgumentTypeError("Size requires at least one dimension defined")

    orig_size = orig_image.size
    aratio = orig_size[0]/orig_size[1]

    w, h = new_size
    if not w:
        w = int(h * aratio) # wnew = hnew * (w / h)
    if not h:
        h = int(w / aratio) # wnew = hnew * (w / h)
    return (w, h)


def size_parse_abs(orig_image, new_size):
    return size_parse_tuple(orig_image, (new_size))


def size_parse_rel(orig_image, new_size):
    w, h = new_size
    if not w and not h:
        raise ArgumentTypeError("Relative size requires at least one dimension defined")

    if not w: w = h
    if not h: h = w

    w = int(tofrac(w) * orig_image.size[0])
    h = int(tofrac(h) * orig_image.size[1])

    return size_parse_tuple(orig_image, (w, h))


pat_rel = re.compile("^((?P<width>\d+)%)?(x((?P<height>\d+)%)?)?$")
pat_abs = re.compile("^(?P<width>\d+)?(x(?P<height>\d+)?)?$")

# attempt to imitate imagemagick
size_patterns  = [
    ("abs", pat_abs, size_parse_abs),
    ("rel", pat_rel, size_parse_rel),
]


class ImageHandler:
    dir_postfix = 'imgc'
    dir_files = '_files-imgc'

    imgs_done = 0
    imgs_total = 0

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.images = [] # list of (src, dst) tuples
    
    def generate_image_paths(self):
        for arg in self.src_images:

            # process directory path
            if os.path.isdir(arg):
                src = os.path.abspath(arg)
                dst = os.path.abspath("{}-{}".format(src, self.dir_postfix))
                if not os.path.exists(dst):
                    os.makedirs(dst)
                for root, dirs, files in os.walk(src):
                    for d in dirs:
                        src_dir = os.path.join(root, d)
                        dst_dir = src_dir.replace(src, dst)
                        if not os.path.exists(dst_dir):
                            os.makedirs(dst_dir)
                    for f in files:
                        if os.path.splitext(f)[1][1:].strip().lower() not in IMAGE_EXTS: continue
                        src_file = os.path.join(root, f)
                        dst_file = src_file.replace(src, dst)
                        self.append((src_file, dst_file))

            # process file path
            elif os.path.isfile(arg):
                src = os.path.abspath(arg)
                dst_dir = os.path.join(os.path.dirname(src), self.dir_files)
                if not os.path.exists(dst_dir):
                    os.makedirs(dst_dir)
                dst = os.path.join(dst_dir, os.path.basename(arg))
                self.append((src, dst))


    def process(self):
        self.generate_image_paths()

        if not self.images: 
            print("No images found!") 
            sys.exit()

        self.imgs_total = len(self.images)
        print("Images found: {}".format(self.imgs_total))

        pool = ThreadPool(self.workers)

        time_start = time.time()
        pool.starmap(self.resize_image, self.images)
        pool.close()
        pool.join()
        time_end = time.time()

        window = tkinter.Tk()
        window.wm_withdraw()
        tkinter.messagebox.showinfo('imgc - work finished', 'Images compressed: {}'.format(self.imgs_done))
        print("Time elapsed: {}".format(time_end - time_start))


    def append(self, path_tuple):
        self.images.append(path_tuple)


    def print_status(self, dst):
        print("[{}/{}] processed image {}".format(
            self.imgs_done, self.imgs_total, os.path.split(dst)[1]))


    def resize_image(self, src, dst):
        size = self.size
        quality = self.quality

        im = Image.open(src)
        origsize = im.size
        aratio = origsize[0]/origsize[1]

        # process size tuples 
        # with absolute image dimensions (800x600 etc.)
        if isinstance(size, (tuple, list)):
            wnew, hnew = size_parse_tuple(im, size)
        # process string pattern provided by user:
        # takes the first match from size_patterns
        # and runs validator callback embedded in a tuple
        elif isinstance(size, str):
            for p in size_patterns:
                m = p[1].match(size)
                if m: 
                    wpat, hpat = m.group('width'), m.group('height')
                    if wpat: wpat = int(wpat)
                    if hpat: hpat = int(hpat)
                    wnew, hnew = p[2](im, (wpat, hpat))
                    break
            else:
                raise argparse.ArgumentTypeError("Invalid size pattern")
        else:
            raise argparse.ArgumentTypeError("Invalid size type: only str, tuple and list supported")

        im = im.resize((wnew, hnew), Image.BICUBIC)
        if os.path.splitext(dst)[1][1:].strip().lower() not in IMAGE_JPG:
            im.save(dst)
        else:
            # quality supported by jpegs only
            im.save(dst, 'JPEG', quality=quality)
        self.imgs_done += 1
        self.print_status(dst)


def quality_type(x):
    """argparse quality validator for JPEGs
    accepts values from 1 to 100"""

    x = int(x)
    if x < 1:
        raise argparse.ArgumentTypeError("Minimum JPEG quality is 1")
    if x > 100:
        raise argparse.ArgumentTypeError("Maximum JPEG quality is 100")
    return x


def size_type(x):
    """argparse size validator for images
    attempts to imitate imagemagick patterns
    (see size_patterns for additional info)

    EXAMPLES:
    relative size patterns:
    70%x80%
    70%
    70%x
    x80%

    absolute size patterns:
    800x600
    800
    800x
    x600

    TODO:
    ! < > ^ flags 
    """

    for p in size_patterns:
        m = p[1].match(x)
        if m: break
    else:
        raise argparse.ArgumentTypeError("Invalid size pattern")

    return x
        # if m:
        #     print("match: {} | {} x {}".format(p[0], m.group('width'), m.group('height')))
        # else:
        #     print("no match: {}".format(p[0]))
    

if __name__ == '__main__':

    import tkinter
    import tkinter.messagebox

    parser = argparse.ArgumentParser(description="Batch process pictures")
    parser.add_argument('src_images', metavar="path", type=str, nargs='+')
    parser.add_argument('-q', '--quality', type=quality_type, default=90,
        help='Quality for JPEG images')
    parser.add_argument('-s', '--size', type=size_type, default="1000x",
        help='New image size')
    parser.add_argument('-w', '--workers', type=int, default=None,
        help='Number of pool workers')

    args = parser.parse_args()
    print(args)

    imgh = ImageHandler(**vars(args))
    imgh.process()