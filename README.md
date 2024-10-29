# pyrfdc

more python-y interface to the xrfdc crap from Xilinx

this one gets rid of the bull$#!+ assumption that you're
accessing the registers via AXI

goal is to allow it to work via *any* access method.
it's kinda dumb to do this via Python but we're
well into the dumb stage at this point

## low level crap

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

# RFDC parameters

You want to pass the RFdc parameters to PyRFDC by passing the
XCI file built in the firmware. We use the XCI rather than the HWH
because it won't be in the HWH if it's not in the block diagram.
But the XCI is just a JSON version of the stuff in the HWH
anyway.

# Building

You need to build the stuff in libunivrfdc first on the target
you want to run it on.