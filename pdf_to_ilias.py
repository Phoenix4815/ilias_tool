#!/usr/bin/env python3
"""
Module Docstring
"""

__version__ = "0.1.0"
__license__ = "GPL3"

import os
import sys

import PyPDF2
import yaml
from PyPDF2 import PdfFileWriter


def print_usage():
    print(f"Usage: python3.8 {sys.argv[0]} [graded_pdf.pdf] [page_counts.yaml]")


def main(args):
    if not args or len(args) <= 2:
        print_usage()
        exit()

    graded_pdf_path = args[1]
    page_counts_path = args[2]
    os.makedirs("gen_split", exist_ok=True)

    print("Generating files...")

    with open(graded_pdf_path, "rb") as pdf_file, open(page_counts_path, "r") as f:
        y = yaml.load(f, Loader=yaml.SafeLoader)

        pdf = PyPDF2.PdfFileReader(pdf_file)
        offset = 0
        for name in y:
            print(f"\t{name}: {offset + 1}-{offset + y[name]} = {y[name]} pages")
            writer = PdfFileWriter()
            for i in range(offset, offset + y[name]):
                writer.addPage(pdf.getPage(i))

            out_path = os.path.join("gen_split", name + "_corrected.pdf")
            print(f"\t-> {out_path}")
            with open(out_path, "wb") as out:
                writer.write(out)

            offset += y[name]


if __name__ == "__main__":
    main(sys.argv)
