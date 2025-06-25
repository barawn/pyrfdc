/* EVERYTHING GOES IN HERE! */
#ifndef METAL_SYS_H
#define METAL_SYS_H

#include <stdint.h>
#include <unistd.h>
#include <string.h>

#define METAL_IRQ_HANDLED 0

typedef uint32_t metal_phys_addr_t;
typedef uint32_t __u32;
typedef uint16_t __u16;
typedef uint8_t __u8;
typedef int32_t __s32;
typedef int16_t __s16;
typedef int8_t __s8;
typedef uint64_t __u64;
typedef int64_t __s64;

typedef uint32_t (*read_function_t)(void *dev, uint32_t addr);
typedef void (*write_function_t)(void *dev, uint32_t addr, uint32_t value, uint32_t mask);

// I might actually use this for something.
// Who knows.
struct metal_io_region {
  read_function_t read_function;
  write_function_t write_function;
  // opaque pointer to hold le stuff
  void *dev;
};

#define metal_device_io_region metal_io_region

struct metal_device {
  char name[16];
};
  
#define METAL_LOG_ERROR 0
#define METAL_LOG_WARNING 1
#define METAL_LOG_INFO 2
#define METAL_LOG_DEBUG 3

#define metal_sleep_usec usleep

// these LITERALLY NEVER GET CALLED. EVER.
int metal_device_open(const char *bus_name,
		      const char *dev_name,
		      struct metal_device **device);

void metal_device_close(struct metal_device *device);

struct metal_io_region *metal_device_io_region( struct metal_device *dev,
						unsigned int index );

int metal_linux_get_device_property(struct metal_device *dev,
				    const char *property_name,
				    void *output,
				    int len);

// these might
void metal_log( int verbosity,
		const char *format,
		...);

void metal_io_write16( struct metal_io_region *io,
		       unsigned long offset,
		       uint16_t value );
void metal_io_write32( struct metal_io_region *io,
		     unsigned long offset,
		     uint32_t value );
uint16_t metal_io_read16( struct metal_io_region *io,
			  unsigned long offset );
uint32_t metal_io_read32( struct metal_io_region *io,
			unsigned long offset );

void metal_io_set_device( void *dev,
			  read_function_t read_function,
			  write_function_t write_function);

void metal_io_set_log( int fd );

#endif
