# pyrfdc

Python interface to the XRFdc functions from Xilinx.

Xilinx's library for interfacing with the RF data converter is extremely
opaque, and in addition, it goes through libmetal, which only has standard
implementations for either bare metal, or through direct-memory access
methods on Linux.

But the RFdc's interface is just AXI4. You could access it via any number
of methods. You don't have to do it from the PL - you just need register
reads and writes.

So instead of having xrfdc link against libmetal, we create a fake
libmetal which just has "read" and "write" functions, which xrfdc
then calls. This is "libunivrfdc." You need to build that library
first.

Then, inside Python, we do things similar to PYNQ except we just use
ctypes and clean things up a bit.

## Python usage

You need a Python object that can read/write registers from the RFdc's
address space. Those methods must be called ``read`` and ``write``.
Read takes an address, write takes an address and a value (in that order).
Read returns the value read, write returns nothing. You also need
path to the built version of ``libunivrfdc.so`` and the RFdc
parameter file from the project (see below).

Let's call the Python object that has the read/write functions
``dev``. Then you do:

```
>>> rfdc = PyRFDC(dev, 'rfdc_parameters.pkl', 'libunivrfdc/libunivrfdc.so')
>>> rfdc.configure()
0
>>> rfdc.MultiConverter_Init(rfdc.ConverterType.ADC)
0
>>> rfdc.MultiConverter_Init(rfdc.ConverterType.DAC)
0
>>> rfdc.MultiConverter_Sync(rfdc.ConverterType.ADC)
metal_log<2>:
DTC Scan T1
metal_log<3>:Target 64, DTC Code 5, Diff 59, Min 59
metal_log<3>:Target 64, DTC Code 45, Diff 19, Min 19
metal_log<3>:Target 64, DTC Code 103, Diff 39, Min 19
metal_log<3>:RefTile (0): DTC Code Target 64, Picked 45
metal_log<2>:ADC0: 000000000001113222000000000000000000000000000*000000000000000000#000000001132220000000000000000000000000000000000000000000000000
metal_log<3>:Count_W 8, loc_W 1
metal_log<2>:SysRef period in terms of ADC T1s = 384
0
```

Note that by default in libunivrfdc, metal_log just prints things
out. Maybe it would make sense to have a callback so that logs like
this can be filtered/printed out/etc.

# RFDC parameters

You create the parameter file for the RFDC from the IP core's XCI file
using the ``make_paramfile.py`` script in ``utils/``. All that script
does is extract the model_parameters entry and pickle it: it's still
overly verbose, but smaller than the XCI is.

## Low level information.

xrfdc wraps register access only with

* XRFdc_ReadReg
* XRFdc_ReadReg16
* XRFdc_WriteReg
* XRFdc_WriteReg16

These are macros which wrap
* XRFdc_In32
* XRFdc_In16
* XRFdc_Out32
* XRFdc_Out16

which are __again__ macros defined as

* metal_io_read32
* metal_io_read16
* metal_io_write32
* metal_io_write16

metal_io_write16 turn into

* metal_io_write((_io), (_ofs), (_val), memory_order_seq_cst, 2)

which just turns into atomic_store_explicit.

These will be replaced with read/write functions.

The other metal functions we need to supply are

* metal_log (whatever, printf)
* metal_allocate_memory (uh... whatever)
* metal_io_init (again whatever)
* metal_sleep_usec (usleep)
* metal_phys_addr_t => uint32_t
* struct metal_io_region (whatever)
* struct metal_device (whatever)
* - metal_device_open
* - metal_linux_get_device_property
    - XRFDC_COMPATIBLE_PROPERTY ("compatible") = xlnx,usp-rf-data-converter-
    - XRFDC_CONFIG_DATA_PROPERTY ("param-list")
      - The way PYNQ sleazes this is by converting the hwh config
        into an XRFdc_Config * via populate_config and ffi.
	We can actually probably sleaze it the same way.
* - metal_device_open
* - metal_device_close
* - metal_register_generic_device

# Building

You need to build the stuff in libunivrfdc first on the target
you want to run it on.