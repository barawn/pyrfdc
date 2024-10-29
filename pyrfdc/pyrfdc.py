# This is the CTypes PyRFDC module.

import ctypes
from pyrfdc_ctypes import *
import inspect
import json
import os

class Dummy:
    def __init__(self):
        pass

    def read(self, addr):
        print("read", addr)
        return 0

    def write(self, addr, value, mask):
        print("write", addr, value, mask)        

def is_callable_with(f, *args, **kwargs):
    try:
        rv = inspect.getcallargs(f, *args, **kwargs)
        return True
    except TypeError:
        return False

class PyRFDC:
    # blatantly stolen from config.py in Pynq's xrfdc
    # Even though we use the JSON, it's the same b/c
    # the model parameters section of the XCI is identical
    # to the HWH's parameters
    _DAC_ADP = [
        ('BlockAvailable', 'C_DAC_Slice{}{}_Enable', 'int'),
        ('InvSyncEnable', 'C_DAC_Invsinc_Ctrl{}{}', 'int'),
        ('MixMode', 'C_DAC_Mixer_Mode{}{}', 'int'),
        ('DecoderMode', 'C_DAC_Decoder_Mode{}{}', 'int')
    ]
    _DAC_DDP = [
        ('MixerInputDataType', 'C_DAC_Data_Type{}{}', 'int'),
        ('DataWidth', 'C_DAC_Data_Width{}{}', 'int'),
        ('InterpolationMode', 'C_DAC_Interpolation_Mode{}{}', 'int'),
        ('MixerType', 'C_DAC_Mixer_Type{}{}', 'int')
    ]
    _ADC_ADP = [
        ('BlockAvailable', 'C_ADC_Slice{}{}_Enable', 'int'),
        ('MixMode', 'C_ADC_Mixer_Mode{}{}', 'int')
    ]    
    _ADC_DDP = [
        ('MixerInputDataType', 'C_ADC_Data_Type{}{}', 'int'),
        ('DataWidth', 'C_ADC_Data_Width{}{}', 'int'),
        ('DecimationMode', 'C_ADC_Decimation_Mode{}{}', 'int'),
        ('MixerType', 'C_ADC_Mixer_Type{}{}', 'int')
    ]
    _DAC_Tile = [
        ('Enable', 'C_DAC{}_Enable', 'int'),
        ('PLLEnable', 'C_DAC{}_PLL_Enable', 'int'),
        ('SamplingRate', 'C_DAC{}_Sampling_Rate', 'double'),
        ('RefClkFreq', 'C_DAC{}_Refclk_Freq', 'double'),
        ('FabClkFreq', 'C_DAC{}_Fabric_Freq', 'double'),
        ('FeedbackDiv', 'C_DAC{}_FBDIV', 'int'),
        ('OutputDiv', 'C_DAC{}_OutDiv', 'int'),
        ('RefClkDiv', 'C_DAC{}_Refclk_Div', 'int'),
        ('MultibandConfig', 'C_DAC{}_Band', 'int'),
        ('MaxSampleRate', 'C_DAC{}_Fs_Max', 'double'),
        ('NumSlices', 'C_DAC{}_Slices', 'int')
    ]
    _ADC_Tile = [
        ('Enable', 'C_ADC{}_Enable', 'int'),
        ('PLLEnable', 'C_ADC{}_PLL_Enable', 'int'),
        ('SamplingRate', 'C_ADC{}_Sampling_Rate', 'double'),
        ('RefClkFreq', 'C_ADC{}_Refclk_Freq', 'double'),
        ('FabClkFreq', 'C_ADC{}_Fabric_Freq', 'double'),
        ('FeedbackDiv', 'C_ADC{}_FBDIV', 'int'),
        ('OutputDiv', 'C_ADC{}_OutDiv', 'int'),
        ('RefClkDiv', 'C_ADC{}_Refclk_Div', 'int'),
        ('MultibandConfig', 'C_ADC{}_Band', 'int'),
        ('MaxSampleRate', 'C_ADC{}_Fs_Max', 'double'),
        ('NumSlices', 'C_ADC{}_Slices', 'int')
    ]
    _Config = [
        ('ADCType', 'C_High_Speed_ADC', 'int'),
        ('ADCSysRefSource', 'C_Sysref_Source', 'int'),
        ('DACSysRefSource', 'C_Sysref_Source', 'int'),
        ('IPType', 'C_IP_Type', 'int'),
        ('SiRevision', 'C_Silicon_Revision', 'int')
    ]
    _bool_dict = {
        'true': 1,
        'false': 0
    }
    
    # dev here is expected to have a dev.read/dev.write function
    # dev.write REALLY SHOULD take a mask option!! but we sleaze
    # it here!
    def __init__(self, dev, xciFile, univrfdcPath="libunivrfdc.so"):
        self.dev = dev
        self.read = self.dev.read
        self.write = self.dev.write
        self.rfdc = XRFdc()
        self.rfdcConfig = XRFdc_Config()
        self.mtsDacConfigPtr = ctypes.POINTER(XRFdc_MultiConverter_Sync_Config)
        self.mtsAdcConfigPtr = ctypes.POINTER(XRFdc_MultiConverter_Sync_Config)
        self.xciFile = xciFile
        
        ctypes.cdll.LoadLibrary(univrfdcPath)
        self.lib = ctypes.CDLL("libunivrfdc.so")

        # set up the return crap here
        self.lib.metal_io_region.restype = ctypes.POINTER(metal_io_region)
        
        def readFunc(unk, addr):
            return self.read(addr)        
        self.readCallback = read_function_t(readFunc)
        if is_callable_with(dev.write, 0, 0, 0):
            def writeFunc(unk, addr, value, mask):
                return self.write(addr, value, mask)
            self.writeCallback = write_function_t(writeFunc)
        else:
            def writeFunc(unk, addr, value, mask):
                return self.write(addr, value)
            self.writeCallback = write_function_t(writeFunc)
        
        self.lib.metal_io_set_device( None,
                                      self.readCallback,
                                      self.writeCallback)
        # the device here is dummy
        mdev = metal_device()
        io = self.lib.metal_io_region(ctypes.pointer(mdev), 0)
        if io:
            self.rfdc.io = io
        else:
            raise IOError("metal_io_region")


    # this is SIMILAR TO but NOT THE SAME
    # as PYNQ's crap since they get it from the HWH and we get it from
    # the XCI, which is JSON
    def configure(self):
        def _to_value(val, dtype):
            if dtype == 'int':
                if val in self._bool_dict:
                    return self._bool_dict[val]
                return int(val, 0)
            elif dtype == 'double':
                return float(val)
            else:
                raise ValueError("%s is not int or double" % dtype)
            
        def _set_configs(obj, params, config, *args):
            # params here is the model_parameters element
            # to access its value, we need to access first value in
            # list and then 'value' element in dict
            for c in config:
                setattr(obj, c[0], _to_value(params[c[1].format(*args)][0]['value'], c[2]))

        # try opening the XCI file
        modelParams = None
        try:
            if not os.path.isfile(self.xciFile):
                raise ValueError("%s is not a file" % self.xciFile)
            with open(self.xciFile, "r") as f:
                data = json.load(f)
                modelParams = data['ip_inst']['parameters']['model_parameters']
        except Exception as e:
            raise ValueError("%s was not parseable") from e
        # modelParams is now ok 
        _set_configs(self.rfdcConfig,
                     modelParams,
                     self._Config)
        for i in range(4):
            _set_configs(self.rfdcConfig.DACTile_Config[i],
                         modelParams,
                         self._DAC_Tile,
                         i)
            _set_configs(self.rfdcConfig.ADCTile_Config[i],
                         modelParams,
                         self._ADC_Tile,
                         i)
            for j in range(4):
                _set_configs(self.rfdcConfig.DACTile_Config[i].DACBlock_Analog_Config[j],
                             modelParams,
                             self._DAC_ADP, i, j)
                _set_configs(self.rfdcConfig.DACTile_Config[i].DACBlock_Digital_Config[j],
                             modelParams,
                             self._DAC_DDP, i, j)
                _set_configs(self.rfdcConfig.ADCTile_Config[i].ADCBlock_Analog_Config[j],
                             modelParams,
                             self._ADC_ADP, i, j)
                _set_configs(self.rfdcConfig.ADCTile_Config[i].ADCBlock_Digital_Config[j],
                             modelParams,
                             self._ADC_DDP, i, j)
        res = self.lib.XRFdc_CfgInitialize(ctypes.pointer(self.rfdc),
                                           ctypes.pointer(self.rfdcConfig))
        return res
        
