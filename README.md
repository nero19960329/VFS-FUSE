![lint workflow](https://github.com/nero19960329/vfs-fuse/actions/workflows/lint.yml/badge.svg)
![integration tests workflow](https://github.com/nero19960329/vfs-fuse/actions/workflows/integration_tests.yml/badge.svg)

# VFS-FUSE

A versioned file system based on FUSE and Git, written in Python.

## Description

VFS-FUSE is a file system that tracks every version of files, just like Git. It uses FUSE (Filesystem in Userspace) to create a user-space file system, and uses Git to store and manage file versions.

## Requirements

- Python 3.7 or later

## Installation

### From PyPI

```bash
pip install vfsfusepy
```

### From Source

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
vfs-fuse /path/to/git_dir /path/to/mount_point  # if installed from PyPI

python vfsfusepy/__main__.py /path/to/git_dir /path/to/mount_point  # if installed from source
```

Where:

- `git_dir` is the directory of the Git repository that will be used to store and manage file versions.
- `mount_point` is the directory where the VFS-FUSE file system will be mounted.

Please ensure you have write permissions on both directories.

## Example

Here is an example of how to use VFS-FUSE:

```bash
# Mount the file system
mkdir /data/vfs-root
mkdir /data/vfs-mount
vfs-fuse /data/vfs-root /data/vfs-mount

# Go to the mount point
cd /data/vfs-mount

# Create a new file
echo "Hello, World!" > test.txt

# View the file
cat test.txt

# Remove the file
rm test.txt

# View the commit history
git log
```

In this example, when you write to test.txt, the file system automatically commits the changes to the Git repository located at `/data/vfs-root`. You can then use standard Git commands to view the commit history and checkout previous versions of the file.

## FAQ

### Why not use Git directly?

`VFS-FUSE` offers automatic git commits for all file changes, creating a real-time version control system. It simplifies the use of git, allowing operations via a standard file system interface. Essentially, it's git made easy for everyday file operations.

### How to solve `raise EnvironmentError('Unable to find libfuse')`?

You need to install the FUSE library. On Ubuntu, you can install it with the following command:

```bash
sudo apt-get update && sudo apt-get install fuse
```

## Contributing
We welcome contributions to this repository! If you would like to contribute code, please take a moment to read our [contribution guidelines](https://github.com/nero19960329/VFS-FUSE/blob/main/CONTRIBUTING.md).

By following these guidelines, you can ensure that your contributions are in line with our coding standards and testing procedures.

We appreciate your interest and look forward to your contributions!

## License

This project is licensed under the terms of the MIT license.
