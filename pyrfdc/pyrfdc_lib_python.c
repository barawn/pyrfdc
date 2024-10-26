/* thank god I wrote this stuff before for ocpci */

#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/types.h>
#include <stdint.h>
#include <Python.h>
#include <structmember.h>

#include "xrfdc/xrfdc.h"
#include "py_xrfdc_config.h"
// not running bare metal: but CfgInitialize calls:
//if (InstancePtr->io == NULL) {
//                metal_log(METAL_LOG_ERROR, "\n nstancePtr->io not allocated in %s\r\n", __func__);
//                Status = XRFDC_FAILURE;
//                goto RETURN_PATH;
//        }
// We need to implement metal_log, and then we can also use InstancePtr->io to hold
// our read/write callbacks when they get passed to configure. We'll drop them
// as members now that we know stuff works. Remember we need to do
// Py_XDECREF(self->read_callback)
// Py_XINCREF(new_callback)
// before we assign it.
// So we'll be redefining (struct metal_io_region) as holding 2 callable PyObjects

// This stuff is for the INTERNAL module (named _pyrfdc).
// The EXTERNAL module is named pyrfdc. It's pure python
// and massages stuff. This is *minimal*.
typedef struct {
  PyObject_HEAD
  XRFdc dev;
  XRFdc_MultiConverter_Sync_Config mts_adc_config;
  XRFdc_MultiConverter_Sync_Config mts_dac_config;  
  PyObject *read_callback;
  PyObject *write_callback;
} _pyrfdc_Device;

static PyObject *
_pyrfdc_Device_configure( _pyrfdc_Device *self, PyObject *arg) {
  if (PyDict_Check(arg)) {
    XRFdc_Config *cfg;
    u32 res;
    Py_xrfdc_config_fill(arg, &cfg);
    res = XRFdc_CfgInitialize(self->dev, &cfg);
  } else {
    PyErr_SetString(PyExc_TypeError, "a dictionary is required");
    return NULL;
  }
  Py_RETURN_NONE;
}

static PyObject *
_pyrfdc_Device_test( _pyrfdc_Device *self ) {
  if (!PyCallable_Check(self->read_callback)) {
    PyErr_SetString(PyExc_TypeError, "read is not callable");
    return NULL;
  }
  if (!PyCallable_Check(self->write_callback)) {
    PyErr_SetString(PyExc_TypeError, "write is not callable");
    return NULL;
  }
  printf("I guess I'm OK?\n");
  Py_RETURN_NONE;
}

static PyMemberDef _pyrfdc_Device_members[] = {
  {"read", T_OBJECT_EX, offsetof(_pyrfdc_Device, read_callback), 0, "Read function"},
  {"write", T_OBJECT_EX, offsetof(_pyrfdc_Device, write_callback), 0, "Write function"},
  { NULL } /* sentinel */
};

static PyMethodDef _pyrfdc_Device_methods[] = {
  { "configure", (PyCFunction) _pyrfdc_Device_configure, METH_O,
    "load XRFdc configuration" },
  { "test", (PyCFunction) _pyrfdc_Device_test, METH_NOARGS,
    "test if we're ready" },
  { NULL } /* sentinel */
};

static void
_pyrfdc_Device_dealloc(_pyrfdc_Device *self) {
  // hell if I know, do something maybe??
  Py_XDECREF(self->read_callback);
  Py_XDECREF(self->write_callback);
  Py_TYPE(self)->tp_free((PyObject *) self);
}

static PyObject *
_pyrfdc_Device_new( PyTypeObject *type, PyObject *args, PyObject *kwds) {
  _pyrfdc_Device *self;
  self = (_pyrfdc_Device *) type->tp_alloc(type, 0);
  if (self != NULL) {
    self->read_callback = Py_None;
    self->write_callback = Py_None;
  }
  return (PyObject *) self;
}

static int _pyrfdc_Device_init( _pyrfdc_Device *self,
				PyObject *args,
				PyObject *kwds) {
  // uh whatever
  // we'll figure this shit out later
  return 0;
}

static PyTypeObject _pyrfdc_DeviceType = {
  .ob_base = PyVarObject_HEAD_INIT(NULL, 0)
  .tp_name = "_pyrfdc.Device",
  .tp_doc = PyDoc_STR("Internal Python XRFdc device"),
  .tp_basicsize = sizeof(_pyrfdc_Device),
  .tp_itemsize = 0,
  .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
  .tp_init = (initproc) _pyrfdc_Device_init,
  .tp_new = _pyrfdc_Device_new,
  .tp_dealloc = (destructor) _pyrfdc_Device_dealloc,
  .tp_methods = _pyrfdc_Device_methods,
  .tp_members = _pyrfdc_Device_members,
};

static PyMethodDef module_methods[] = {
  {NULL} /* sentinel */
};

#ifndef PyMODINIT_FUNC
#define PyMODINIT_FUNC void
#endif

static struct PyModuleDef _pyrfdc_module =
  {
    PyModuleDef_HEAD_INIT,
    "_pyrfdc",
    "Internal pyrfdc module",
    -1,
    module_methods
  };

/* note this takes TWO DAMN UNDERSCORES */
PyMODINIT_FUNC
PyInit__pyrfdc(void) {
  PyObject *m;
  if (PyType_Ready(&_pyrfdc_DeviceType) < 0)
    return NULL;
  m = PyModule_Create(&_pyrfdc_module);
  if (m == NULL)
    return NULL;

  Py_INCREF(&_pyrfdc_DeviceType);
  PyModule_AddObject(m, "Device", (PyObject *) &_pyrfdc_DeviceType);
  return m;
}
