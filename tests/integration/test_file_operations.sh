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

# Git Status should be clean
check_git_status() {
    [ "$(git status --porcelain)" = "" ] || { echo "Unexpected changes in git status"; exit 1; }
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

# Create a new file
echo "Hello, World!" > test.txt
[ "$(cat test.txt)" = "Hello, World!" ] || { echo "File contents mismatch"; exit 1; }
check_git_status

# Write same contents to file (testing 'write')
echo "Hello, World!" > test.txt
[ "$(cat test.txt)" = "Hello, World!" ] || { echo "File contents mismatch"; exit 1; }
check_git_status

# Read file (testing 'read')
cat test.txt
check_git_status

# Truncate file (testing 'truncate')
truncate -s 0 test.txt
[ "$(cat test.txt)" = "" ] || { echo "File not truncated correctly"; exit 1; }
check_git_status

# Check file permissions (testing 'access')
touch test.txt || { echo "Cannot touch test.txt"; exit 1; }
check_git_status

# Change file permissions (testing 'chmod')
chmod 777 test.txt
check_git_status

# Check symbolic link (testing 'readlink')
ln -s test.txt link.txt
[ "$(readlink link.txt)" = "test.txt" ] || { echo "Symlink not created correctly"; exit 1; }
check_git_status
rm link.txt

# Create a special file (testing 'mknod')
mknod pipefile p
rm pipefile
check_git_status

# Check file system stats (testing 'statfs')
df .

# Check symbolic link creation (testing 'symlink')
ln -s test.txt symlink.txt
[ -L symlink.txt ] || { echo "Symlink not created"; exit 1; }
check_git_status
rm symlink.txt

# Check hard link creation (testing 'link')
ln test.txt hardlink.txt
[ -e hardlink.txt ] || { echo "Hardlink not created"; exit 1; }
check_git_status
rm hardlink.txt

# Check time stamp update (testing 'utimens')
touch -a -m -t 202307101830.00 test.txt
check_git_status

# Flush the file buffer (testing 'flush')
sync
check_git_status

# Release the file (testing 'release')
: > test.txt
check_git_status

# File synchronization (testing 'fsync')
sync
check_git_status

# Modify the file
echo "Goodbye, World!" > test.txt
[ "$(cat test.txt)" = "Goodbye, World!" ] || { echo "File contents mismatch"; exit 1; }
check_git_status

# Rename the file
mv test.txt test2.txt
[ -f test.txt ] && { echo "File still exists after rename"; exit 1; }
[ "$(cat test2.txt)" = "Goodbye, World!" ] || { echo "File contents mismatch"; exit 1; }
check_git_status

# Create a new directory
mkdir test_dir
mv test2.txt test_dir/test2.txt
[ -d test_dir ] || { echo "Directory not created"; exit 1; }
check_git_status

# Rename the directory
mv test_dir test2_dir
[ -d test_dir ] && { echo "Directory still exists after rename"; exit 1; }
[ -d test2_dir ] || { echo "Directory not renamed"; exit 1; }
check_git_status

# Remove the directory
rm -rf test2_dir
[ -d test2_dir ] && { echo "Directory still exists after removal"; exit 1; }
check_git_status

# Check `/tmp/vfs-mount` only has the `.git` directory
[ "$(ls -A /tmp/vfs-mount)" = ".git" ] || { echo "Unexpected files in /tmp/vfs-mount"; exit 1; }

# View the commit history
echo "Commit history:"
git --no-pager log --oneline
