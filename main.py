#!/usr/bin/env python3
"""news-image-20261123 entrypoint (Python 3.13, standard library only).

Copies the pre-built entry.png beside this file to
$MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png).

The image itself is drawn at build time by build.py (PIL flat-vector art);
the grader container has no Pillow and no network, so this entrypoint only
copies the image the repository holds, as the kit's starter does.
"""

import hashlib
import os
import shutil
import sys

MAX_BYTES = 1024 * 1024  # the gate accepts at most 1 MiB


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    size = os.path.getsize(dst)
    if size > MAX_BYTES:
        print("entry.png is %d bytes, over the 1 MiB limit" % size,
              file=sys.stderr)
        return 1
    digest = hashlib.sha256(open(dst, "rb").read()).hexdigest()
    print("wrote %s (%d bytes) sha256=%s" % (dst, size, digest))
    return 0


if __name__ == "__main__":
    sys.exit(main())
