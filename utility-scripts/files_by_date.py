'''
filter files by date
'''
import os
import re
import sys
import time
import shutil

start = 12000
end = 29000
sept3rd = 1504472890
dest = "R:/audio/avlab/new_ingest"
while (start <= end):
    dir = "R:/audio"
    dir = os.path.join(dir,str(start))
    print dir
    for dirs, subdirs, files in os.walk(dir):
        for s in subdirs:
            sfull = os.path.join(dirs,s)
            age = os.path.getctime(sfull)
            if age > sept3rd:
                print s
                for file in os.listdir(os.path.join(dir,s)):
                    match = ''
                    match = re.search(r'\w{8}-\w{4}-\w{4}-\w{4}-\w{12,13}.wav(?!.md5)', file)
                    if match:
                        print file
                        try:
                            if not os.path.exists(os.path.join(dest,file)):
                                shutil.move(os.path.join(dir,s,file),os.path.join(dest,file))
                            else:
                                pass
                            for file in os.listdir(os.path.join(dir,s)):
                                match = ''
                                match = re.search(r'\w{8}-\w{4}-\w{4}-\w{4}-\w{12,13}.wav(?!.md5)', file)
                                if match:
                                    print file
                                    try:
                                        if not os.path.exists(os.path.join(dest,file)):
                                            shutil.move(os.path.join(dir,s,file),os.path.join(dest,file))
                                        else:
                                            pass
                                    except:
                                        sys.exit()
                            shutil.rmtree(os.path.join(dir,s))
                        except:
                            sys.exit()
    start = start + 1000
