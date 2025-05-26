# libunivrfdc

This is a Universal (hence univ) version of the XRFdc driver.

Xilinx's XRFdc driver links to libmetal, which assumes you're
going to use the Bog Standard AXI Interface, so it's memory
mapped, and you just use atomic functions, etc. etc.

But this is nuts - there are plenty of reasons to access
the RFdc registers via other access methods. So here we
enable that by creating an incredibly dummy metal library.

The libunivrfdc dummy metal library abuses the metal_io_region
pointer to store a read and write function. The read function
just takes a void pointer and an address and returns a value,
the write function takes a void pointer, address, value, and __mask__
and returns nothing.

I don't know if the mask is important for XRFdc, but XRFdc
occasionally does a Write16 instead of Write32, so we need
to avoid certain cases.

The magic is in metal_io_set_device: you pass it a void pointer,
and a read and write function. The read/write functions will
receive the void pointer as the first argument.

The void pointer is used to store whatever you need, you don't
have to use it if you don't want to.

# tl;dr

You need to call ``metal_io_set_device`` in this library
and pass it a read and write function. Signatures are:
```
typedef uint32_t (*read_function_t)(void *dev, uint32_t addr);
typedef void (*write_function_t)(void *dev, uint32_t addr, uint32_t value, uint32_t mask);
```

and then the ``metal_io_set_device`` is:
```
void metal_io_set_device( void * dev,
			  read_function_t read_function,
			  write_function_t write_function);
```
After that you can get the ``metal_io_region`` by just calling
```
io = metal_io_region(NULL, 0)
```
and then just initialize a blank XRFdc structure and set its ``io`` pointer to that.
