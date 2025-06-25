#include <stdio.h>
#include <stdarg.h>
#include "sys.h"

// UPDATE 11/7/24 PSA:
// Inspection of the RFdc HDL shows that there is literally
// zero point to the 16-bit read/writes, because there
// is no capability whatsoever in the IP to do anything
// with it: Bus2IP_BE (the byte-enables, which would
// be used for 16-bit writes) are connected to absolutely
// nothing.

// I don't even actually know if the 16-bit reads only
// return 16 bits - the function's defined to read
// a u64.

// I'm actually pretty sure that there are just wacko
// amounts of bugs in Xilinx's code all over the place.
// For instance, I'm pretty sure that xrfdc_intr's
// XRFdc_IntrEnable just absolutely blows away the
// AXI timeout interrupt because it uses a 16-bit
// write and metal_io_write16 casts it to a short.

struct metal_device dummy_device;
struct metal_io_region this_region = { NULL, NULL, NULL };
FILE *this_stream = NULL;

// these LITERALLY NEVER GET CALLED. EVER.
int metal_device_open(const char *bus_name,
		      const char *dev_name,
		      struct metal_device **device) {
  *device = &dummy_device;
  strncpy(dummy_device.name, dev_name, 15);
  return 0;
}

void metal_log( int verbosity,
		const char *format,
		...) {
  va_list args;
  va_start( args, format );
  fprintf(this_stream, "metal_log<%d>:", verbosity);
  vfprintf(this_stream, format, args);
}

void metal_device_close(struct metal_device *device) {
  if (this_stream != stdout) fclose(this_stream);
}

struct metal_io_region *metal_io_region(struct metal_device *dev,
					unsigned int index) {
  if (this_region.read_function != NULL &&
      this_region.write_function != NULL)
    return &this_region;
  else
    return NULL;
}

void metal_io_write16( struct metal_io_region *io,
		       unsigned long offset,
		       uint16_t value ) {
  if (io->write_function != NULL) {
    // literally just ignore the fact that it's a write16.
    // stupid xilinx.
    io->write_function(io->dev, offset, value, 0);
  }
}
void metal_io_write32( struct metal_io_region *io,
		       unsigned long offset,
		       uint32_t value ) {
  if (io->write_function != NULL) {
    io->write_function(io->dev, offset, value, 0);
  }
}
// again just ignore the fact that it's supposedly 16 bit
uint16_t metal_io_read16( struct metal_io_region *io,
			  unsigned long offset ) {
  if (io->read_function != NULL) {
    return io->read_function(io->dev, offset) & 0xFFFF;
  }
  return 0xFFFF;
}
uint32_t metal_io_read32( struct metal_io_region *io,
			  unsigned long offset ) {
  if (io->read_function != NULL) {
    return io->read_function(io->dev, offset);
  }
  return 0xFFFFFFFF;
}

void metal_io_set_device( void * dev,
			  read_function_t read_function,
			  write_function_t write_function) {
  this_region.dev = dev;
  this_region.read_function = read_function;
  this_region.write_function = write_function;
  this_stream = stdout;
}

// my hacky function to allow printing logs to a filedes
// so stupid but whatever
void metal_io_set_log( int fd ) {
  if (this_stream != stdout) fclose(this_stream);
  if (fd < 0) {
    this_stream = stdout;
  } else {
    this_stream = fdopen(dup(fd), "a+");
  }
}

int metal_linux_get_device_property(struct metal_device *dev,
				    const char *property_name,
				    void *output,
				    int len) {
  return 0;
}
