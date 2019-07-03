# mPyPl - Monadic Pipeline Library for Python
# http://github.com/shwars/mPyPl

# Different sinks to consume mdict streams

from pipe import *
import csv
import json
from .utils.image import show_images
from .core import select_field, pexec
from .utils.coreutils import unzip_list

@Pipe
def write_csv(l,filename,write_headers=True,file_mode='w'):
    with open(filename,file_mode,newline='') as f:
        w = csv.writer(f)
        fst = True
        for x in l:
            if fst and write_headers:
                w.writerow(x.keys())
                fst = False
            w.writerow(x.values())

@Pipe
def write_json(l,filename):
    with open(filename,'w') as f:
        f.write(json.dumps(l))

@Pipe
def pshow_images(stream,image_field_name,title_field_name=None,cols=1):
    """
    Show images from the source stream
    :param image_field_name: Field name that contains images
    :param title_field_name: Field name that contains titles (optional)
    :param cols: Columns (defaults to 1)
    """
    if title_field_name is None:
        stream | select_field(image_field_name) | pexec(lambda x : show_images(x,cols=cols))
    else:
        ims,titles = unzip_list(stream | select_field([image_field_name,title_field_name]) | as_list)
        show_images(ims,titles=titles,cols=cols)