/*
 * Wrap the libmetal crap.
 * Most of the garbage is silly-land.
 * Python-wise we require a read function and a write function.
 * Both are assumed to be 32 bit.
 * Read takes 1 parameter (address)
 * Write takes up to 3 parameters (address, data, mask)
 * where mask is a *16-bit* write disable.
 */


