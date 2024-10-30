# This is the CTypes PyRFDC module.

from .pyrfdc_ctypes import *

import ctypes
import inspect
import pickle
import os
from enum import Enum

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
    class ConverterType(str, Enum):
        ADC = 'ADC'
        DAC = 'DAC'
        def __str__(self) -> str:
            return self.value

    # these are the values passable to CustomStartUp
    class RFdcState(int, Enum):
        XRFDC_STATE_OFF = 0x0
        XRFDC_STATE_SHUTDOWN = 0x1
        XRFDC_STATE_PWRUP = 0x3
        XRFDC_STATE_CLK_DET = 0x6
        XRFDC_STATE_CAL = 0xB
        XRFDC_STATE_FULL = 0xF
        def __index__(self) -> int:
            return self.value
        
    # blatantly stolen from config.py in Pynq's xrfdc
    # the paramFile is a pickled extract of the model_parameters
    # portion of the XCI file, which is equivalent to the
    # params in the XML HWH file
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

    VALID_TILE_IDS = [ 0, 1, 2, 3 ]
    VALID_BLOCK_IDS = [ 0, 1, 2, 3 ]
    
    # dev here is expected to have a dev.read/dev.write function
    # dev.write REALLY SHOULD take a mask option!! but we sleaze
    # it here!
    def __init__(self, dev, paramFile, univrfdcPath="libunivrfdc.so"):
        self.dev = dev
        self.read = self.dev.read
        self.write = self.dev.write
        self.rfdc = XRFdc()
        self.rfdcConfig = XRFdc_Config()
        self.mtsDacConfig = XRFdc_MultiConverter_Sync_Config()
        self.mtsAdcConfig = XRFdc_MultiConverter_Sync_Config()
        self.paramFile = paramFile
        
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

        # try opening the paramFile
        modelParams = None
        try:
            if not os.path.isfile(self.paramFile):
                raise ValueError("%s is not a file" % self.xciFile)
            with open(self.paramFile, "rb") as f:
                modelParams = pickle.load(f)
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
        if res:
            raise IOError("XRFdc_CfgInitialize returned %d" % res)

        return 0

    # initialize MTS of a given type (ADC or DAC)
    def MultiConverter_Init(self, type, refTile=0, pllCodes=None, t1Codes=None):
        if type == self.ConverterType.ADC:
            cfgPtr = ctypes.pointer(self.mtsAdcConfig)
        elif type == self.ConverterType.DAC:
            cfgPtr = ctypes.pointer(self.mtsDacConfig)
        else:
            raise ValueError("type must be one of %s" % [e.value for e in self.ConverterType])

        # create types
        vtype = ctypes.uint*4
        ptype = ctypes.POINTER(ptype)
        if pllCodes:
            if len(pllCodes) != 4:
                raise TypeError("pllCodes must have 4 elements")
            pllVec = vtype()
            for i in range(4):
                pllVec[i] = pllCodes[i]
            pllP = ptype(pllVec)
        else:
            # pass null pointer
            pllP = ptype()
        if t1Codes:
            if len(t1Codes) != 4:
                raise TypeError("t1Codes must have 4 elements")
            t1Vec = vtype()
            for i in range(4):
                t1Vec[i] = t1Codes[i]
            t1P = ptype(t1Vec)
        else:
            t1P = ptype()

        res = self.lib.XRFdc_MultiConverter_Init(cfgPtr, pllP, t1P, refTile)
        return res
    
    def CustomStartUp(self, type, tile_id, startState, endState):
        def checkState(val, name):            
            if int(val) not in [e.value for e in self.RFdcState]:
                raise ValueError("%s must be %s or one of %s" % (name, self.RFdcState.__name__, [e.value for e in self.RFdcState]))
            return int(val)

        typeInt = self._converterTypeAsInt(type)

        if tile_id not in self.VALID_TILE_IDS and tile_id != -1:
            raise ValueError("tile_id must be one of %s or -1" % self.VALID_TILE_IDS)
        
        startInt = checkState(startState, "startState")
        endInt = checkState(endState, "endState")

        res = self.lib.XRFdc_CustomStartUp(ctypes.pointer(self.rfdc),
                                           typeInt,
                                           tile_id,
                                           startInt,
                                           endInt)
        return res

    def MultiConverter_Sync(self, type):
        typeInt = self._converterTypeAsInt(type)
        if typeInt == 0:
            cfgPtr = ctypes.pointer(self.mtsAdcConfig)
        else:
            cfgPtr = ctypes.pointer(self.mtsDacConfig)

        return self.lib.XRFdc_MultiConverter_Sync(ctypes.pointer(self.rfdc),
                                                  typeInt,
                                                  cfgPtr)

    # this is needed for some multi-device situations!!
    def MTS_Sysref_Config(self, enable):
        if not int(enable) in [0, 1]:
            raise ValueError("enable must evaluate to 0 or 1")
        return self.lib.XRFdc_MTS_Sysref_Config(ctypes.pointer(self.rfdc),
                                                ctypes.pointer(self.mtsAdcConfig),
                                                ctypes.pointer(self.mtsDacConfig),
                                                int(enable))

    # if this is used you have to handle sysref differently!!
    def GetCoarseDelaySettings(self, type, tile_id, block_id):
        typeInt = self._converterTypeAsInt(type)
        (tile, block) = self._checkTileAndBlock(tile_id, block_id)

        settings = XRFdc_CoarseDelay_Settings()
        res = self.lib.XRFdc_GetCoarseDelaySettings(self.rfdc,
                                                    typeInt,
                                                    tile,
                                                    block,
                                                    ctypes.pointer(settings))
        if res:
            raise ValueError("XRFdc_GetCoarseDelaySettings returned %d" % res)
        return settings

    # if this is used you have to handle sysref differently!!
    def SetCoarseDelaySettings(self, type, tile_id, block_id, settings):
        typeInt = self._converterTypeAsInt(type)
        (tile, block) = self._checkTileAndBlock(tile_id, block_id)
        settingsPtr = self._checkSettingsTypePtr(settings, XRFdc_CoarseDelay_Settings)

        return self.lib.XRFdc_SetCoarseDelaySettings(self.rfdc,
                                            typeInt,
                                            tile,
                                            block,
                                            settingsPtr);

    def SetDSA(self, tile_id, block_id, settings):
        (tile, block) = self._checkTileAndBlock(tile_id, block_id)
        settingsPtr = self._checkSettingsTypePtr(settings, XRFdc_DSA_Settings)

        return self.lib.XRFdc_SetDSA(self.rfdc,
                                     tile,
                                     block,
                                     settingsPtr)

    def GetDSA(self, tile_id, block_id):
        (tile, block) = self._checkTileAndBlock(tile_id, block_id)
        settings = XRFdc_DSA_Settings()
        res = self.lib.XRFdc_GetDSA(self.rfdc,
                                    tile,
                                    block,
                                    ctypes.pointer(settings))
        if res:
            raise ValueError("XRFdc_GetDSA returned %d" % res)
        return settings

    @classmethod
    def _checkSettingsTypePtr(cls, settings, settingsType):
        if type(settings) != settingsType:
            raise ValueError("settings must be of type %s" % settingsType.__name__)
        return ctypes.pointer(settings)
                             
    @classmethod
    def _checkTileAndBlock(cls, tile, block):
        if int(tile_id) not in cls.VALID_TILE_IDS:
            raise ValueError("tile_id must be one of %s" % self.VALID_TILE_IDS)
        if int(block_id) not in cls.VALID_BLOCK_IDS:
            raise ValueError("block_id must be one of %s" % self.VALID_BLOCK_IDS)
        return (int(tile), int(block))
        
    @classmethod
    def _converterTypeAsInt(cls, type):
        if type == cls.ConverterType.ADC:
            return 0
        elif type == cls.ConverterType.DAC:
            return 1
        else:
            raise ValueError("type must be %s or one of %s" % (cls.ConverterType.__name__, [e.value for e in cls.ConverterType]))
        
