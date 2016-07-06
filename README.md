# hashmove
better file movement

**General Usage**

python hashmove.py [source file or directory full path] [destination parent directory full path] [flags]

**to move a file**

python hashmove.py C:/path/to/file.ext C:/path/to/parent/dir

**to move a directory**

python hashmove.py /home/path/to/dir/a /home/path/to/dir/b

**to copy a file**

python hashmove.py C:/path/to/file.ext C:/path/to/parent/dir -c

**log the transfer**

python hashmove.py /home/path/to/dir/a /home/path/to/dir/b -l

**verify against another hash or set of hashes**

python hashmove.py "/home/path to/dir/you question" /home/path/to/dir/with/hashes -v
