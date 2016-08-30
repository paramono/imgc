#!/usr/bin/env python3

import argparse
import os
import re
import sys
import time
import threading

from multiprocessing.dummy import Pool as ThreadPool

from PIL import Image
from imgc.utils.types import quality_type, size_type
from imgc.image import ImageSize


IMAGE_EXTS = ['jpg', 'jpeg', 'png', 'gif']
IMAGE_JPG = ['jpg', 'jpeg']




def extension(path):
    return os.path.splitext(path)[1][1:].strip().lower()


class ImageHandler:
    dir_postfix = 'imgc'
    dir_files = '_files-imgc'

    imgs_done = 0
    imgs_total = 0

    def __init__(self, queue=None, **kwargs):
        self.__dict__.update(kwargs)
        self.images = [] # list of (src, dst) tuples
        # threading.Thread.__init__(self)
        # self.queue = queue
        # self._stop = threading.Event()
        self.finished = False
        self.generate_image_paths()
    
    def generate_image_paths(self):
        for arg in self.src_images:

            # process directory path
            if os.path.isdir(arg):
                src = os.path.abspath(arg)
                dst = os.path.abspath("{}-{}".format(src, self.dir_postfix))
                if not os.path.exists(dst):
                    os.makedirs(dst) # target path must always exist

                for root, dirs, files in os.walk(src):
                    for d in dirs:
                        src_dir = os.path.join(root, d)
                        dst_dir = src_dir.replace(src, dst)
                    for f in files:
                        if extension(f) not in IMAGE_EXTS: continue
                        # if os.path.splitext(f)[1][1:].strip().lower() not in IMAGE_EXTS: continue
                        src_file = os.path.join(root, f)
                        dst_file = src_file.replace(src, dst)

                        parent_dir = os.path.dirname(dst_file)
                        print(parent_dir)
                        if not os.path.exists(parent_dir):
                            os.makedirs(parent_dir)
                        print(dst_file)
                        self.append((src_file, dst_file))

            # process file path
            elif os.path.isfile(arg):
                src = os.path.abspath(arg)
                dst_dir = os.path.join(os.path.dirname(src), self.dir_files)
                if not os.path.exists(dst_dir):
                    os.makedirs(dst_dir)
                dst = os.path.join(dst_dir, os.path.basename(arg))
                self.append((src, dst))
            # print (self.images)
        self.imgs_total = len(self.images)

    # def stop(self):
    #     self._stop.set()

    # def stopped(self):
    #     return self._stop.isSet()

    def terminate_pool(self):
        if not self.finished:
            self.pool.close()
            self.pool.terminate()
        return self.finished

    def on_finish(self, x):
        print("{}: finished successfully!".format(self.__class__.__name__))
        self.finished = True        
        self.error = False

    def on_error(self, x):
        raise x
        # print("{}: error - {}".format(self.__class__.__name__, str(x)))
        # self.finished = True
        # self.error = True

    def run(self):

        if not self.images: 
            print("No images found!") 
            sys.exit()

        # print("Images found: {}".format(self.imgs_total))
        print("Images found: {}".format(len(self.images)))
        # print(self.images)

        self.pool = ThreadPool(self.workers)

        time_start = time.time()
        # self.pool.starmap(self.resize_image, self.images)
        self.pool.starmap_async(
            self.resize_image, self.images, 1,
            self.on_finish, self.on_error)
        # pool.close()
        # pool.join()
        # time_end = time.time()

        # # window = tkinter.Tk()
        # # window.wm_withdraw()
        # # tkinter.messagebox.showinfo('imgc - work finished', 'Images compressed: {}'.format(self.imgs_done))
        # print("Time elapsed: {}".format(time_end - time_start))

    def append(self, path_tuple):
        self.images.append(path_tuple)

    def print_status(self, dst):
        print("[{}/{}] processed image {}".format(
            self.imgs_done, self.imgs_total, os.path.split(dst)[1]))

    # FIXME: add watermark feature
    # def watermark():
    #     try:
    #         watermark = Image.open(self.wmfile)
    #         # if extension(self.wmfile) in "png":
    #         #     watermark.load()                
    #         wm_oldsize = watermark.size
    #         wm_newdim = min(wnew, hnew) * 0.2
    #         wm_oldindex, wm_olddim = min(enumerate(wm_oldsize))
    #         print(wm_oldindex, wm_olddim)
    #         wm_ratio = wm_newdim/wm_olddim
    #         wm_newsize = (int(wm_oldsize[0] * wm_ratio), 
    #                       int(wm_oldsize[1] * wm_ratio))
    #         print(wm_newsize)
    #         watermark = watermark.resize(wm_newsize)
    #         # mask = watermark.convert("L").point(lambda x: min(x, 50))
    #         # .point(lambda x: 240)
    #         # mask.show()
    #         # watermark.putalpha(mask)
    #         im.paste(watermark, (0, 0), watermark)
    #     except AttributeError:
    #         pass

    def resize_image(self, src, dst):
        print("resizing")
        pattern = self.size
        quality = self.quality

        im = Image.open(src)

        new_size = ImageSize.parse(pattern, image=im)
        print('new_size:', new_size)
        im = im.resize(new_size, Image.BICUBIC)


        if os.path.splitext(dst)[1][1:].strip().lower() not in IMAGE_JPG:
            im.save(dst)
            print("saving non-jpeg %s" % dst)
        else:
            # quality supported by jpegs only
            im.save(dst, 'JPEG', quality=quality)
            print("saving jpeg %s" % dst )
        self.imgs_done += 1
        # self.print_status(dst)

        print ("processed")
        try:
            self.on_image_processed(self.imgs_done, self.imgs_total)
            print ("method called")
        except AttributeError:
            self.print_status(dst)


def main():
    # import tkinter
    # import tkinter.messagebox

    parser = argparse.ArgumentParser(description="Batch process pictures")
    parser.add_argument('src_images', metavar="path", type=str, nargs='+')
    parser.add_argument(
        '-q', '--quality',
        default=90, type=quality_type,
        help='Quality for JPEG images')
    parser.add_argument(
        '-s', '--size',
        default="1000x", type=size_type,
        help='New image size')
    parser.add_argument(
        '-w', '--workers',
        default=2, type=int,
        help='Number of pool workers')
    parser.add_argument(
        '-f', '--wmfile',
        default=None, type=str,
        help='Path to watermark')

    args = parser.parse_args()
    imgh = ImageHandler(**vars(args))
    imgh.run()

    while not imgh.finished:
        time.sleep(0.25)


if __name__ == '__main__':
    main()
