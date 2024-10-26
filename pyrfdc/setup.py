from distutils.core import setup, Extension
setup(name="_pyrfdc", version="1.0",
      ext_modules=[
          Extension("_pyrfdc",
                    ["pyrfdc_lib_python.c",
                     "py_xrfdc_config.c",
                     "xrfdc/xrfdc.c",
                     "xrfdc/xrfdc_ap.c",
                     "xrfdc/xrfdc_clock.c",
                     "xrfdc/xrfdc_dp.c",
                     "xrfdc/xrfdc_g.c",
                     "xrfdc/xrfdc_intr.c",
                     "xrfdc/xrfdc_mb.c",
                     "xrfdc/xrfdc_mixer.c",
                     "xrfdc/xrfdc_mts.c",
                     "xrfdc/xrfdc_sinit.c",
                     "pymetal/metal/sys.c"],
                    include_dirs=['pymetal','xrfdc'])
          ])
