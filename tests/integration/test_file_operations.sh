#!/bin/bash
set -e # exit if any command fails
set -x # print each command before executing

# Define cleanup procedure
cleanup() {
    echo "Cleaning up..."
    popd || true
    umount -l /tmp/vfs-mount || true
    kill $vfs_pid || true
    sleep 1
    rm -rf /tmp/vfs-root /tmp/vfs-mount
}

# Register the cleanup function to be called on the EXIT signal
trap cleanup EXIT

# Mount the file system
rm -rf /tmp/vfs-root /tmp/vfs-mount
mkdir /tmp/vfs-root
mkdir /tmp/vfs-mount
vfs-fuse /tmp/vfs-root /tmp/vfs-mount & # run in the background
vfs_pid=$!

# Give it a moment to mount
sleep 5

# Go to the mount point
pushd /tmp/vfs-mount

# Check Git Status
git status

# Create a new file
echo "Hello, World!" > test.txt
[ "$(cat test.txt)" = "Hello, World!" ] || { echo "File contents mismatch"; exit 1; }

# Modify the file
echo "Goodbye, World!" > test.txt
[ "$(cat test.txt)" = "Goodbye, World!" ] || { echo "File contents mismatch"; exit 1; }

# Remove the file
rm test.txt
[ -f test.txt ] && { echo "File still exists after removal"; exit 1; }

# View the commit history
echo "Commit history:"
git --no-pager log --oneline
