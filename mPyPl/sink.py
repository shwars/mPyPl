# mPyPl - Monadic Pipeline Library for Python
# http://github.com/shwars/mPyPl

# Different sinks to consume mdict streams

from pipe import *
import csv
import json

@Pipe
def write_csv(l,filename):
    with open(filename,'a') as f:
        w = csv.writer(f)
        for x in l:
            w.writerow(x)

@Pipe
def write_json(l,filename):
    with open(filename,'w') as f:
        f.write(json.dumps(l))
