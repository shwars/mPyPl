# mPyPl - Monadic Pipeline Library for Python
# http://github.com/shwars/mPyPl

# Different sinks to consume mdict streams

import csv
import json

def write_csv(l,filename):
    with open(filename,'wb') as f:
        w = csv.writer(f)
        for x in l:
            w.writerow(x)

def write_json(l,filename):
    with open(filename,'w') as f:
        f.write(json.dumps(l))
