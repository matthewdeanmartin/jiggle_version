# install visual studio build tools for C++

[Windows CPP Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)

# compile

mypyc -m jiggle_version

Now python -m jiggle_version fails

# do the install -e .

mypyc: $(PYSOURCES)
MYPYPATH=mypy-stubs pip install --verbose -e . \
&& pytest -rs -vv ${PYTEST_EXTRA}

ref: https://github.com/common-workflow-language/cwltool/blob/c5e2912863449934bd278c6a81dfc4aa27967221/Makefile#L200

# Bad annotations? It will fail, possibly with no messages (?)

Use black's mypy.ini

Get a clean run of mypy!

# mypyc -m my_module seems to do nothing?

pip install 
- [hatch](https://github.com/pypa/hatch) 
- [hatch-mypyc](hatch-mypyc)

Update pyproject.toml file, using inspiration from
black's [pyproject.toml](https://github.com/psf/black/blob/main/pyproject.toml)

# How do you know it "worked"

On windows, .pyd files next to every file.

OR a build folder with files/folders that mirror your module(s)

Stacktraces now have `???` instead of normal looking stack trace

# Won't work for

- dunder main (exclude from compilation)
- docopts (exlcude from compilation)

# Honorary Docs

- [How black was compiled with mypyc](https://ichard26.github.io/blog/2022/05/compiling-black-with-mypyc-part-1/)
- [more](https://github.com/mypyc/mypyc/issues/978)

# Now how to build and publish? We need a wheel per python per OS!
[github action example](https://github.com/jleclanche/tan/blob/7334dfe139d819707bcd20c5dca29dacb2074e48/.github/workflows/pypi_upload.yml#L36)
[mypy's example](https://github.com/mypyc/mypy_mypyc-wheels/blob/master/cibuildwheel.toml)


# How do we do quality checks now?

https://mypy.readthedocs.io/en/stable/stubgen.html#stubgen

and stubtest to see if you need to regen the stubs


# Serialization flags?
```python
from mypy_extensions import mypyc_attr
@mypyc_attr
```

# Setup.py way to do it

https://github.com/common-workflow-language/schema_salad/blob/main/setup.py#L23


# Youtube

(mypyc)[https://www.youtube.com/watch?v=3v4YLG3-xnw]
(mypy pycon.lt)[https://www.youtube.com/watch?v=kFKRbo9tFNw]