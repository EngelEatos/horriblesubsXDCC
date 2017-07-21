import os
import re

def get_valid_filename(s):
    s = str(s).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', s)

def ren(path, fname):
    os.rename(os.path.join(path, fname), os.path.join(path, get_valid_filename(fname)))
    print(os.path.join(path, fname), "==>", os.path.join(path, get_valid_filename(fname)))

for dirpath, dnames, fnames in os.walk("/home/chaos/downloads"):
    for f in fnames:
        ren(dirpath, f)
    for d in dnames:
        ren(dirpath, d)
