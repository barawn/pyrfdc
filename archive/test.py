import _pyrfdc
from pyrfdc_config import get_pyconfig
theConfig = get_pyconfig("rfdc_parameters.xml")
def read(addr):
    print("read address", addr)
    return 0

def write(addr, value, mask):
    print("write address", addr, "value", value, "mask", mask)

dev = _pyrfdc.Device(read, write)
dev.configure(theConfig)
dev.mts_init(True, 0, pll=[1,2,3,4])
