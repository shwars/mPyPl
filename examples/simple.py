# mPyPl - Monadic Pipeline Library for Python
# http://github.com/shwars/mPyPl

# Simple samples

sys.path.insert(0,'z:\\GitWork\mPyPl')

import mPyPl as mp
from pipe import *
from mPyPl.utils.pipeutils import *

print("Using mPyPl version "+mp.__version__)

range(100) | mp.as_field('n') | mp.apply('n','n5', lambda x:x%5) | mp.dict_group_by('n5')


data = range(100) | mp.as_field('n') | mp.apply('n','class_id', lambda x:x%5) | mp.datasplit(split_value=0.2)
Tr,Te = data | mp.make_train_test_split()
len(Tr | as_list)
len(Te | as_list)


data = range(100) | mp.as_field('n') | mp.apply('n','class_id', lambda x:x%5) | pshuffle

data | mp.sample_classes('class_id',1,classes=range(15)) | as_list

x = mp.get_xmlstream_fromdir('e:\\data\\babylon\\')

# Compute sum of integers from 1 to 100. Should return 5050
mp.infinite() | mp.fenumerate('x',start=1) | take(100) | mp.fold('x',lambda x,y: x+y,0)

mp.jsonstream("z:\\GitWork\\mPyPl\\examples\\demo.json") | as_list