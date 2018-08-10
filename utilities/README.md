# pre-commit

1. pip install autopep8
2. In the utilites folder is the _pre-commit.sample_
3. In this file there is a line of the form:<p> 
_PATH/python.exe  PATH/utilities/pre-commit.py --check_ <p>
In the first argument, write down the path to _pyhon_ <p>
In the first argument, write down the path to file  _pre-commit.py_ <p>
3. Move _pre-commit.sample_ to the _.git / hooks_ folder
4. Delete the file extension (_pre-commit.sample_ -> _pre-commit_)
5. Now your python files will auto-formating!