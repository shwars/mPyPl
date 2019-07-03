# mPyPl - Monadic Pipeline Library for Python
# http://github.com/shwars/mPyPl

# Simple samples

sys.path.insert(0,'z:\\GitWork\mPyPl')

import mPyPl as mp
from pipe import *
from mPyPl.utils.pipeutils import *
import cv2
import mPyPl.utils.image as mpui

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


im = mp.im_resize(cv2.imread('e:\\temp\\data\\img.jpg'),size=300)

mpui.show_images(mpui.im_tilecut(im,tile_size=110),cols=3)


([{"a": [1,2,3], "b" : 12, "c" : [11,12,13]}, {"a" : [3,4,5], "b" : 13, "c": [13,14,15] }]
 | select(lambda x: mp.mdict(x))
 | mp.set_eval_strategy("a",mp.EvalStrategies.OnDemand)
 | mp.inspect()
 | mp.unroll(['a','c'])
 | mp.inspect()
 | mp.as_list
 )

## Check is select_fields preserves strategies
( [1,2,3,4,5]
  | mp.as_field("x")
  | mp.apply('x','y',(lambda x: x+1),eval_strategy=mp.EvalStrategies.OnDemand)
  | mp.select_fields(['x','y'])
  | mp.inspect()
  | mp.execute
)

