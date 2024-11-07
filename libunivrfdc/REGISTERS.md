# Register Map

This is the decoded map of the RFDC's registers
pulled from xrfdc_hw.h. There may be additional
registers hidden somewhere, who knows!

There are also some additional details pulled
from the generated HDL from the IP core.

These details are for a Gen1/3 8x8 RFSoC, so this
might not be true for other ones. But some of it
I'm pretty sure is common.

Xilinx's RFDC IP _exposes_ an AXI interface,
but in truth (like all the hard IP!) it's
actually a DRP interface, and there's internally
an AXI-to-DRP translation.

The address decoding inside is __exceptionally__
weird, however. The addresses start off as
18-bit byte addresses, meaning they need an
address space of 262,144 bytes (0x00000-0x3FFFF).
The AXI bus is 32 bits. The internal DRP
(again, like all DRP interfaces inside Xilinx FPGAs!)
is 16 bits.

The top 5 bits ([17:13]) are decoded into 18 chip selects,
meaning there are several holes in the register space.
One of those 18 (chip select 2) is also not used.

These are not the only holes, however! Except for the DRPs
(which take up 8 total chip selects thanks to the 4
DAC and 4 ADC tiles), the remaining chip selects
do not decode their entire register space. In fact,
they only decode a small portion of it!

This actually means it's very possible to
compress/re-expand the register space if you need to.
The following table describes ONLY the address spaces
accessed as of Vivado 2022.2 for a Gen1/3 8x8
RFdc. 

Global register map (C/S = control/status):

| Name/Usage | Chip Select | Address Space |
| Global C/S | 0 | 0x00000 - 0x00107 |
| DAC0 C/S | 2 | 0x04000-0x04323 |
| DAC0 DRP | 3 | 0x06000-0x07FFF |
| DAC1 C/S | 4 | 0x08000-0x08323 |
| DAC1 DRP | 5 | 0x0A000-0x0BFFF |
| DAC2 C/S | 6 | 0x0C000-0x0C323 |
| DAC2 DRP | 7 | 0x0E000-0x0FFFF |
| DAC3 C/S | 8 | 0x10000-0x10323 |
| DAC3 DRP | 9 | 0x12000-0x13FFF |
| ADC0 C/S | 10| 0x14000-0x14323 |
| ADC0 DRP | 11| 0x16000-0x17FFF |
| ADC1 C/S | 12| 0x18000-0x18323 |
| ADC1 DRP | 13| 0x1A000-0x1BFFF |
| ADC2 C/S | 14| 0x1C000-0x1C323 |
| ADC2 DRP | 15| 0x1E000-0x1FFFF |
| ADC3 C/S | 16| 0x20000-0x20323 |
| ADC3 DRP | 17| 0x22000-0x23FFF |

As you can see it would be trivial to compress the address space
by at least half with the current address mapping - each chip select
has an address space of 8192 bytes, so the DRP spaces could be aligned
to 8 chip selects with a simple lookup, and the C/S spaces could
be merged into the remaining 8 chip selects trivially. This
expansion/compression could be done by simple lookup tables on the
top 6 bits and minor bit twiddling in the driver.

## Driver Register Stuff

The driver mainly works with offsets to a base address, which maps
pretty well with the whole idea of chip-selects. 

Any time you see XRFDC_BLOCK_BASE, you're dealing with a DRP
access. Those are calculated with XRFDC_BLOCK_BASE(Type, Tile, Block).
Type/Tile just determine the base address due to the goofy mapping:
(XRFDC_ADC_TILE, 0) just gives you 0x16000, for instance, and
(XRFDC_DAC_TILE, 0) just gives you 0x06000. The "block" portion
hints that internally the DRP groups things in 1024-address blocks,
since it just adds (block * 0x400).

## Interesting Notes!

The XRFdc driver uses 16-bit writes/reads. These are utterly pointless.
The partial write signals generated from the AXI bus translation (Bus2IP_BE)
are totally and completely ignored.

This means that any time a 16-bit write is performed, it's actually interpreted
as a 32-bit write anyway. The DRP accesses are simply a 16-bit access expanded into a
32-bit space. The upper data bits are not connected to them in any way. This is why
you will __never__ see anything other than a 32-bit aligned address access.

I seriously don't understand this. Stuff like XRFdc_IntrEnable will just eff
up, because the ReadReg16/WriteReg16 will just blow away the timeout enable
that's at bit 31.