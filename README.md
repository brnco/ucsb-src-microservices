# hashmove
file movement for people without rsync

**General Usage**

python hashmove.py [flags] [source file or directory full path] [destination parent directory full path]

**to move a file**

python hashmove.py C:/path/to/file.ext C:/path/to/parent/dir

**to move a directory**

python hashmove.py /home/path/to/dir/a /home/path/to/dir/b

**to copy a file**

python hashmove.py -c C:/path/to/file.ext C:/path/to/parent/dir

**log the transfer**

python hashmove.py -l /home/path/to/dir/a /home/path/to/dir/b

**verify against another hash or set of hashes**

python hashmove.py -v "/home/path to/dir/you question" /home/path/to/dir/with/hashes


##pro-tip

if you have a directory with lots of subdirectories you'd like to move, it's probably better to loop through your parent dir and hashmove each subdir individually, rather than just hashmoving the parent.\

e.g.

/parent/itemA

/parent/itemB

...

/parent/itemZ

rather than: python hashmove.py /parent /newparent

try:

for subdir in parent:

python hashmove subdir /newparent/subdirname