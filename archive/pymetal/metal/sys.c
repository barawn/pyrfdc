#include <stdio.h>
#include <stdarg.h>
#include "sys.h"

struct metal_device dummy_device;
struct metal_io_region this_region = { NULL, NULL, NULL };

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
  printf("metal_log<%d>:", verbosity);
  vprintf(format, args);
}

void metal_device_close(struct metal_device *device) {
  
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
    uint32_t mask;
    // if we're 32-bit aligned, mask the upper word
    // else mask the lower word
    mask = ((offset & 0x2)==0) ? 0x2 : 0x1;
    io->write_function(io->dev, offset, value, mask);
  }
}
void metal_io_write32( struct metal_io_region *io,
		       unsigned long offset,
		       uint32_t value ) {
  if (io->write_function != NULL) {
    io->write_function(io->dev, offset, value, 0);
  }
}
uint16_t metal_io_read16( struct metal_io_region *io,
			  unsigned long offset ) {
  if (io->read_function != NULL) {
    uint32_t tmp;
    uint16_t res;
    tmp = io->read_function(io->dev, offset);
    if (offset & 0x2) res = (tmp & 0xFFFF0000)>>16;
    else res = (tmp & 0xFFFF);
    return res;
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
}

int metal_linux_get_device_property(struct metal_device *dev,
				    const char *property_name,
				    void *output,
				    int len) {
  return 0;
}
