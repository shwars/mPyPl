cd ..\docs
echo ==== CORE ====
python ..\mpydoc\mpydoc.py -w mPyPl.core
python ..\mpydoc\mpydoc.py -w mPyPl.funcs
python ..\mpydoc\mpydoc.py -w mPyPl.jsonstream
python ..\mpydoc\mpydoc.py -w mPyPl.keras
python ..\mpydoc\mpydoc.py -w mPyPl.mdict
python ..\mpydoc\mpydoc.py -w mPyPl.multiclass_datastream
python ..\mpydoc\mpydoc.py -w mPyPl.sink
python ..\mpydoc\mpydoc.py -w mPyPl.sources
python ..\mpydoc\mpydoc.py -w mPyPl.video
python ..\mpydoc\mpydoc.py -w mPyPl.xmlstream
echo ==== UTILS ====
python ..\mpydoc\mpydoc.py -w mPyPl.utils.coreutils
python ..\mpydoc\mpydoc.py -w mPyPl.utils.fileutils
python ..\mpydoc\mpydoc.py -w mPyPl.utils.flowutils
python ..\mpydoc\mpydoc.py -w mPyPl.utils.image
python ..\mpydoc\mpydoc.py -w mPyPl.utils.lambdas
python ..\mpydoc\mpydoc.py -w mPyPl.utils.pipeutils
python ..\mpydoc\mpydoc.py2 -w mPyPl.utils.video
echo ==== MAIN ====
python ..\mpydoc\mpydoc.py -w mPyPl

