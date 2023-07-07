#!/usr/bin/env python3
from argparse import ArgumentParser
from fuse import FUSE

from vfsfusepy.vfs import VFS


def parse_args():
    parser = ArgumentParser(
        description="A versioned file system based on FUSE and Git."
    )
    parser.add_argument(
        "git_dir", type=str, help="The directory of the git repository."
    )
    parser.add_argument(
        "mount_point", type=str, help="The mount point of the file system."
    )
    return parser.parse_args()


def main():
    args = parse_args()
    FUSE(VFS(args.git_dir), args.mount_point, foreground=True)


if __name__ == "__main__":
    main()
