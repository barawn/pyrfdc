#ifndef PY_XRFDC_CONFIG_H
#define PY_XRFDC_CONFIG_H

#include <Python.h>
#include "xrfdc/xrfdc.h"

void Py_xrfdc_config_fill(PyObject *dict,
			  XRFdc_Config *cfg);


#endif
