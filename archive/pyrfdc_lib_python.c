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
#include "pymetal/metal/sys.h"

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

// these are __convenience__ functions
uint32_t _pyrfdc_read(void *dev, uint32_t address) {
  PyObject *arglist;
  PyObject *result;
  unsigned long rv;
  _pyrfdc_Device *self = (_pyrfdc_Device *) dev;
  
  if (!self->read_callback) {
    fprintf(stderr, "_pyrfdc_read: read callback wasn't set up");
    return 0xFFFFFFFF;
  }
  arglist = Py_BuildValue("(I)", address);
  result = PyObject_CallObject(self->read_callback,
			       arglist);
  Py_DECREF(arglist);
  if (result == NULL) {
    fprintf(stderr, "_pyrfdc_read: read function threw an exception!");
    PyErr_Clear();
    return 0xFFFFFFFF;
  }
  rv = PyLong_AsUnsignedLong(result);
  if (PyErr_Occurred()) {
    fprintf(stderr, "_pyrfdc_read: casting result threw an exception!");
    PyErr_Clear();
    return 0xFFFFFFFF;
  }
  Py_DECREF(result);
  return rv;
}

// these are __convenience__ functions
void _pyrfdc_write(void *dev,
		   uint32_t address,
		   uint32_t value,
		   uint32_t mask) {
  PyObject *arglist;
  PyObject *result;
  _pyrfdc_Device *self = (_pyrfdc_Device *) dev;
  
  if (!self->write_callback) {
    fprintf(stderr, "_pyrfdc_write: read callback wasn't set up");
    return;
  }
  arglist = Py_BuildValue("(III)", address, value, mask);
  result = PyObject_CallObject(self->write_callback,
			       arglist);
  Py_DECREF(arglist);
  if (result == NULL) {
    fprintf(stderr, "_pyrfdc_write: write function threw an exception!");
    PyErr_Clear();
    return;
  }
  // we literally don't care about the result
  Py_DECREF(result);
  return;
}


static PyObject *
_pyrfdc_Device_configure( _pyrfdc_Device *self, PyObject *arg) {
  if (PyDict_Check(arg)) {
    XRFdc_Config cfg;
    u32 res;
    Py_xrfdc_config_fill(arg, &cfg);
    res = XRFdc_CfgInitialize(&self->dev, &cfg);
    // uh i dunno
    if (res != 0)
      printf("got an error %d\n", res);
  } else {
    PyErr_SetString(PyExc_TypeError, "a dictionary is required");
    return NULL;
  }
  Py_RETURN_NONE;
}

// initialize MTS
// it may shock you to find out that the PYNQ calls are wrong:
// they rely on clock distribution not being used.
// Also they don't allow for previously-determined PLL/T1
// codes to be used, so we allow for that.
//
// ok it doesn't shock me
static PyObject *
_pyrfdc_Device_mts_init( _pyrfdc_Device *self,
			 PyObject *args,
			 PyObject *kwds) {
  static char *kwlist[] = { "initAdc", "reftile", "pll", "t1", NULL };
  int adcNotDac;
  int pll[4];
  int t1[4];
  int *pllPointer;
  int *t1Pointer;
  unsigned int reftile=0;
  PyObject *tmp;
  
  // the T1 and PLL codes are per-tile.
  // you're actually setting the "Target" component of the
  // XRFdc_MTS_DTC_Settings for both DTC_Set_PLL and DTC_Set_T1
  // this means we need 4 of 'em and they're all ints.
  // all kwd arguments must be optional so there must be a
  // | before $ somewhere
  if (!PyArg_ParseTupleAndKeywords(args, kwds,
				   "pI|$(iiii)(iiii)",
				   kwlist,
				   &adcNotDac,
				   &reftile,
				   &pll[0],
				   &pll[1],
				   &pll[2],
				   &pll[3],
				   &t1[0],
				   &t1[1],
				   &t1[2],
				   &t1[3]))
    return NULL;
  // stupidest thing ever
  // we have to check whether or not we were passed
  // stuff b/c PyArg_ParseTupleAndKeywords unpacked
  // the tuple.
  // it's more useful that way, but we need to add
  // the check
  // if no keywords, they're both NULL
  if (kwds == NULL || !PyDict_Check(kwds)) {
    pllPointer = NULL;
    t1Pointer = NULL;
  } else {
    // now check both pll and t1 separately
    tmp = PyUnicode_FromString("pll");
    if (PyDict_Contains(kwds, tmp)) {
      pllPointer = pll;
    } else {
      pllPointer = NULL;
    }
    Py_XDECREF(tmp);
    tmp = PyUnicode_FromString("t1");
    if (PyDict_Contains(kwds, tmp)) {      
      t1Pointer = t1;
    } else {
      t1Pointer = NULL;
    }
    Py_XDECREF(tmp);
  }
  // figure out which configuration to run
  if (adcNotDac) {    
    XRFdc_MultiConverter_Init(&(self->mts_adc_config),
			     pllPointer,
			     t1Pointer,
			     reftile);
  } else {
    XRFdc_MultiConverter_Init(&(self->mts_dac_config),
			     pllPointer,
			     t1Pointer,
			     reftile);
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
  printf("XRFdc functions are callable\n");
  Py_RETURN_NONE;
}

static PyMemberDef _pyrfdc_Device_members[] = {
  {"read", T_OBJECT_EX, offsetof(_pyrfdc_Device, read_callback), 0, "Read function"},
  {"write", T_OBJECT_EX, offsetof(_pyrfdc_Device, write_callback), 0, "Write function"},
  { NULL } /* sentinel */
};

// ALL device methods must be of type PyCFunction because that's
// how PyMethodDef is defined. They'll be recast to their proper types
// base on the methods.
static PyMethodDef _pyrfdc_Device_methods[] = {
  { "configure", (PyCFunction) _pyrfdc_Device_configure, METH_O,
    "load XRFdc configuration" },
  { "mts_init", (PyCFunction) _pyrfdc_Device_mts_init, METH_VARARGS | METH_KEYWORDS,
    "initialize Multi-Tile Sync" },
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
    self->read_callback = NULL;
    self->write_callback = NULL;
  }
  return (PyObject *) self;
}

static int _pyrfdc_Device_init( _pyrfdc_Device *self,
				PyObject *args,
				PyObject *kwds) {
  // I need a callable read function and a callable write
  // function. We ONLY CHECK if they are callables.
  // We DO NOT CHECK argument stuff, because that's
  // why we're the _pyrfdc and not pyrfdc!
  // pyrfdc checks this via
  // try
  //    inspect.signature(read_fn).bind(0)
  //    return true
  // except TypeError:
  //    return false
  // and with bind(0,1,2) on write_fn (the 0/1/2 isn't important).
  // and IF AND ONLY IF that passes, then it passes those as
  // positional args here.
  PyObject *read_function = NULL;
  PyObject *write_function = NULL;
  PyObject *tmp;
  printf("unpacking tuple\n");
  if (!PyArg_UnpackTuple(args, "init", 2, 2,
			 &read_function,
			 &write_function))
    return -1;  
  printf("checking callables\n");
  // because UnpackTuple's min/max were 2/2,
  // we don't need to check if they're null
  if (!PyCallable_Check(read_function)) {
    PyErr_SetString(PyExc_TypeError, "read function must be callable");
    return -1;
  }
  if (!PyCallable_Check(write_function)) {
    PyErr_SetString(PyExc_TypeError, "write function must be callable");
    return -1;
  }
  printf("assigning callables\n");
  // the syntax here is covered in the documentation
  // section 2.1 of Extending and Embedding the Python Interpreter
  // you need to decref only after reassigning in case of weirdo
  // recursion.
  tmp = self->read_callback;
  Py_INCREF(read_function);
  self->read_callback = read_function;
  Py_XDECREF(tmp);

  tmp = self->write_callback;
  Py_INCREF(write_function);
  self->write_callback = write_function;
  Py_XDECREF(tmp);
  
  printf("metal_io_set_device-ing\n");
  // I should maybe name this pymetal or something
  metal_io_set_device( self, _pyrfdc_read, _pyrfdc_write );
  // none o' this crap matters
  self->dev.io = metal_io_region(NULL, 0);

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
