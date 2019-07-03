# mPyPl - Monadic Pipeline Library for Python
# http://github.com/shwars/mPyPl

# Cognitive samples
import sys
sys.path.insert(0,'z:\\GitWork\mPyPl')

import mPyPl as mp
from mPyPl.cognitive.bing import BingImageSearch7

print("Using mPyPl version "+mp.__version__)

bis = BingImageSearch7("e3dd74503c0243f0b6d9a5a576aaab24")

r = list(bis.search("герман греф"))