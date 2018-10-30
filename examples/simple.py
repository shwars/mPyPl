# mPyPl - Monadic Pipeline Library for Python
# http://github.com/shwars/mPyPl

# Simple samples

sys.path.append('z:\\GitWork\mPyPl')

import mPyPl as mp
from pipe import *
from mPyPl.utils.pipeutils import *


range(100) | mp.as_field('n') | mp.apply('n','n5', lambda x:x%5) | mp.dict_group_by('n5')


data = range(100) | mp.as_field('n') | mp.apply('n','class_id', lambda x:x%5) | mp.datasplit(split_value=0.2)
Tr,Te = data | mp.make_train_test_split()
len(Tr | as_list)
len(Te | as_list)


data = range(100) | mp.as_field('n') | mp.apply('n','class_id', lambda x:x%5) | pshuffle

data | mp.sample_classes('class_id',1,classes=range(15)) | as_list

x = mp.get_xmlstream_fromdir('e:\\data\\babylon\\')