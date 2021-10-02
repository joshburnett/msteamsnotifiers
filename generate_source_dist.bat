rmdir /S /Q build
rmdir /S /Q canaveral.egg-info
rmdir /S /Q dist
python setup.py sdist --formats=gztar
python setup.py bdist_wheel