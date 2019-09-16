cd ..\docs\pydoc
set pydoccmd=python ..\..\mpydoc\mpydoc.py
echo ==== CORE ====
%pydoccmd% -w mPyPl.core
%pydoccmd% -w mPyPl.funcs
%pydoccmd% -w mPyPl.jsonstream
%pydoccmd% -w mPyPl.keras
%pydoccmd% -w mPyPl.mdict
%pydoccmd% -w mPyPl.multiclass_datastream
%pydoccmd% -w mPyPl.sink
%pydoccmd% -w mPyPl.sources
%pydoccmd% -w mPyPl.video
%pydoccmd% -w mPyPl.xmlstream
echo ==== UTILS ====
%pydoccmd% -w mPyPl.utils.coreutils
%pydoccmd% -w mPyPl.utils.fileutils
%pydoccmd% -w mPyPl.utils.flowutils
%pydoccmd% -w mPyPl.utils.image
%pydoccmd% -w mPyPl.utils.lambdas
%pydoccmd% -w mPyPl.utils.pipeutils
%pydoccmd% -w mPyPl.utils.video
echo ==== MAIN ====
%pydoccmd% -w mPyPl
