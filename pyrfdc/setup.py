from distutils.core import setup, Extension
setup(name="_pyrfdc", version="1.0",
      ext_modules=[
          Extension("_pyrfdc",
                    ["pyrfdc_lib_python.c",
                     "py_xrfdc_config.c"],
                    include_dirs=['pymetal','xrfdc'])
          ])
