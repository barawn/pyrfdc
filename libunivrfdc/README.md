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
just takes a void pointer and n address and returns a value,
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

