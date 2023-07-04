# VFS-FUSE

A versioned file system based on FUSE and Git, written in Python.

## Description

VFS-FUSE is a file system that tracks every version of files, just like Git. It uses FUSE (Filesystem in Userspace) to create a user-space file system, and uses Git to store and manage file versions.

## Requirements

- Python 3.7 or later

## Installation

1. Clone the repository:

```bash
git clone https://github.com/nero19960329/VFS-FUSE.git
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

To use VFS-FUSE, you need to specify the directory of the Git repository and the mount point of the file system:

```bash
python vfs.py /path/to/git_dir /path/to/mount_point
```

Where:

- `git_dir` is the directory of the Git repository that will be used to store and manage file versions.
- `mount_point` is the directory where the VFS-FUSE file system will be mounted.

Please ensure you have write permissions on both directories.

## Example

Here is an example of how to use VFS-FUSE:

```bash
# Mount the file system
python vfs.py /data/vfs-root /data/vfs-mount

# Go to the mount point
cd /data/vfs-mount

# Create a new file
echo "Hello, World!" > test.txt

# View the file
cat test.txt

# View the commit history
git log
```

In this example, when you write to test.txt, the file system automatically commits the changes to the Git repository located at /data/vfs-root. You can then use standard Git commands to view the commit history and checkout previous versions of the file.

## License

This project is licensed under the terms of the MIT license.
