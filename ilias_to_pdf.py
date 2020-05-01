#!/usr/bin/env python3
"""
Module Docstring
"""

__version__ = "0.1.0"
__license__ = "GPL3"

import io
import os
import yaml
import shutil
import sys

from PIL import Image
from PyPDF2 import PdfFileMerger, PdfFileReader

########################################################################################################################
# File handlers
########################################################################################################################

pdfs_by_dirname = {}


def zip_handler(dirpath, filename, abspath):
    print(f"\tUnzipping {abspath} to {dirpath}")
    shutil.unpack_archive(abspath, dirpath)


def image_handler(dirpath, filename, abspath):
    pdf_abspath = os.path.join(dirpath, os.path.splitext(filename)[0] + ".pdf")
    print(f"\tConverting {abspath} into {pdf_abspath}")

    Image.open(abspath).convert('RGB').save(pdf_abspath, ignore_discard=False)


def pdf_handler(dirpath, filename, abspath):
    print(f"\tAdding {abspath} to concatenation queue")
    pdfs_by_dirname.setdefault(dirpath, []).append(abspath)


########################################################################################################################


def print_usage():
    print(f"Usage: python3.8 {sys.argv[0]} [ilias_export_folder_path]")


def file_extention(filename):
    return os.path.splitext(filename)[1][1:].lower()


def walk_files(path, ignore_files):
    # store function references in a dict to dispatch, this is a common python idiom
    func_map = {'zip': zip_handler,
                'tar': zip_handler,
                'gztar': zip_handler,
                'jpg': image_handler,
                'jpeg': image_handler,
                'png': image_handler,
                'pdf': pdf_handler}

    handled_files = []

    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            abspath = os.path.join(dirpath, filename)

            if abspath in ignore_files:
                #print(f"Ignoring {abspath}")
                continue

            handled_files.append(abspath)

            ext = file_extention(filename)
            print(f"Handling file {abspath} ({ext})...")
            try:
                function = func_map[ext]
            except KeyError:
                # no function to process files with extension 'ext', ignore it
                print(f"No handler for {ext}! Skipping...")
                pass
            else:
                #with open(abspath) as f:
                function(dirpath, filename, abspath)

    return handled_files


def concat_pdfs(pdfs_by_dirname):
    page_nums = {}

    for dir in pdfs_by_dirname:
        print(f"Entering {dir}")
        contents = pdfs_by_dirname[dir]
        contents.sort()

        merger = PdfFileMerger(strict=False)
        for pdf in contents:
            print(f"\t{pdf}")
            merger.append(pdf)

        name = os.path.normpath(dir).split(os.sep)[2]
        page_num = len(merger.pages)
        page_nums[name] = page_num
        new_pdf = os.path.join("gen", name + ".pdf")
        print(f"\t-> {new_pdf} ({page_num} pages)")

        merger.write(new_pdf)

    print("saving page counts...")
    with open(os.path.join("gen", "page_counts.yaml"), "w") as f:
        f.write(yaml.dump(page_nums))



def main(args):
    if not args or len(args) == 1:
        print_usage()
        exit()

    path = args[1]
    os.makedirs("gen", exist_ok=True)

    ignore_files = handled_files = walk_files(path, [])
    while True:
        if not handled_files:
            break

        ignore_files.extend(handled_files)
        handled_files = walk_files(path, ignore_files)

    print("\nConcatenating PDF-Files")
    concat_pdfs(pdfs_by_dirname)


if __name__ == "__main__":
    main(sys.argv)
