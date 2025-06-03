# this originated from ctypesgen on xrfdc.h, but cleaned up
from ctypes import Structure, c_int, c_uint, c_byte, c_ubyte, c_short, c_ushort, c_double, c_float, c_char, c_void_p, c_ulong, CFUNCTYPE, POINTER

metal_phys_addr_t = c_uint
u64 = c_ulong
u32 = c_uint
u16 = c_ushort
u8 = c_ubyte
s32 = c_int
s16 = c_short
s8 = c_byte

# fakey ctypes stuff
# As of ctypes 1.0, ctypes does not support custom error-checking
# functions on callbacks, nor does it support custom datatypes on
# callbacks, so we must ensure that all callbacks return
# primitive datatypes.
#
# Non-primitive return values wrapped with UNCHECKED won't be
# typechecked, and will be converted to ctypes.c_void_p.
def UNCHECKED(type):
    if hasattr(type, "_type_") and isinstance(type._type_, str) and type._type_ != "P":
        return type
    else:
        return c_void_p

# fakey libmetal stuff

read_function_t = CFUNCTYPE(UNCHECKED(u32), POINTER(None), u32)
write_function_t = CFUNCTYPE(UNCHECKED(None), POINTER(None), u32, u32, u32)

class metal_io_region(Structure):
    _fields_ = [
        ('read_function', read_function_t),
        ('write_function', write_function_t),
        ('dev', POINTER(None)),
    ]

class metal_device(Structure):
    _fields_ = [
        ('name', c_char*int(16)),
    ]
        
# xrfdc stuff

# doesn't really matter
XRFdc_StatusHandler = CFUNCTYPE(UNCHECKED(None), POINTER(None), u32, u32, u32, u32)

class XRFdc_PLL_Settings(Structure):
    _pack_ = 1
    _fields_ = [
        ('Enabled', u32),
        ('RefClkFreq', c_double),
        ('SampleRate', c_double),
        ('RefClkDivider', u32),
        ('FeedbackDivider', u32),
        ('OutputDivider', u32),
        ('FractionalMode', u32),
        ('FractionalData', u64),
        ('FractWidth', u32),
    ]

class XRFdc_Tile_Clock_Settings(Structure):
    _pack_ = 1
    _fields_ = [
        ('SourceType', u8),
        ('SourceTile', u8),
        ('PLLEnable', u32),
        ('RefClkFreq', c_double),
        ('SampleRate', c_double),
        ('DivisionFactor', u8),
        ('DistributedClock', u8),
        ('Delay', u8),
    ]        
    
class XRFdc_Distribution_Info(Structure):
    _pack_ = 1
    _fields_ = [
        ('MaxDelay', u8),
        ('MinDelay', u8),
        ('IsDelayBalanced', u8),
        ('Source', u8),
        ('UpperBound', u8),
        ('LowerBound', u8),
        ('ClkSettings', (XRFdc_Tile_Clock_Settings * int(4)) * int(2)),
    ]

class XRFdc_Distribution_Settings(Structure):
    _pack_ = 1
    _fields_ = [
        ('SourceType', u32),
        ('SourceTileId', u32),
        ('EdgeTileIds', u32 * int(2)),
        ('EdgeTypes', u32 * int(2)),
        ('DistRefClkFreq', c_double),
        ('DistributedClock', u32),
        ('SampleRates', (c_double * int(4)) * int(2)),
        ('ShutdownMode', u32),
        ('Info', XRFdc_Distribution_Info),
    ]

class XRFdc_Distribution_System_Settings(Structure):
    _pack_ = 1
    _fields_ = [ ('Distributions', XRFdc_Distribution_Settings * int(8) )]

class XRFdc_MTS_DTC_Settings(Structure):
    _pack_ = 1
    _fields_ = [
        ('RefTile', u32),
        ('IsPLL', u32),
        ('Target', c_int * int(4)),
        ('Scan_Mode', c_int),
        ('DTC_Code', c_int * int(4)),
        ('Num_Windows', c_int * int(4)),
        ('Max_Gap', c_int * int(4)),
        ('Min_Gap', c_int * int(4)),
        ('Max_Overlap', c_int * int(4)),
    ]

class XRFdc_MultiConverter_Sync_Config(Structure):
    _pack_ = 1
    _fields_ = [
        ('RefTile', u32),
        ('Tiles', u32),
        ('Target_Latency', c_int),
        ('Offset', c_int*int(4)),
        ('Latency', c_int*int(4)),
        ('Marker_Delay', c_int),
        ('SysRef_Enable', c_int),
        ('DTC_Set_PLL', XRFdc_MTS_DTC_Settings),
        ('DTC_Set_T1', XRFdc_MTS_DTC_Settings)
    ]

class XRFdc_MTS_Marker(Structure):
    _pack_ = 1
    _fields_ = [
        ('Count', u32 * int(4)),
        ('Loc', u32 * int(4)),
    ]

class XRFdc_Signal_Detector_Settings(Structure):
    _pack_ = 1
    _fields_ = [
        ('Mode', u8),
        ('TimeConstant', u8),
        ('Flush', u8),
        ('EnableIntegrator', u8),
        ('Threshold', u16),
        ('ThreshOnTriggerCnt', u16),
        ('ThreshOffTriggerCnt', u16),
        ('HysteresisEnable', u8),
    ]

class XRFdc_QMC_Settings(Structure):
    _pack_ = 1
    _fields_ = [
        ('EnablePhase', u32),
        ('EnableGain', u32),
        ('GainCorrectionFactor', c_double),
        ('PhaseCorrectionFactor', c_double),
        ('OffsetCorrectionFactor', s32),
        ('EventSource', u32),
    ]

class XRFdc_CoarseDelay_Settings(Structure):
    _pack_ = 1
    _fields_ = [
        ('CoarseDelay', u32),
        ('EventSource', u32),
    ]

class XRFdc_Mixer_Settings(Structure):
    _pack_ = 1
    _fields_ = [
        ('Freq', c_double),
        ('PhaseOffset', c_double),
        ('EventSource', u32),
        ('CoarseMixFreq', u32),
        ('MixerMode', u32),
        ('FineMixerScale', u8),
        ('MixerType', u8),
    ]

class XRFdc_Threshold_Settings(Structure):
    _pack_ = 1
    _fields_ = [
        ('UpdateThreshold', u32),
        ('ThresholdMode', u32 * int(2)),
        ('ThresholdAvgVal', u32 * int(2)),
        ('ThresholdUnderVal', u32 * int(2)),
        ('ThresholdOverVal', u32 * int(2)),
    ]

class XRFdc_Calibration_Coefficients(Structure):
    _pack_ = 1
    _fields_ = [
        ('Coeff0', u32),
        ('Coeff1', u32),
        ('Coeff2', u32),
        ('Coeff3', u32),
        ('Coeff4', u32),
        ('Coeff5', u32),
        ('Coeff6', u32),
        ('Coeff7', u32),
    ]

class XRFdc_Pwr_Mode_Settings(Structure):
    _pack_ = 1
    _fields_ = [
        ('DisableIPControl', u32),
        ('PwrMode', u32),
    ]

class XRFdc_DSA_Settings(Structure):
    _pack_ = 1
    _fields_ = [
        ('DisableRTS', u32),
        ('Attenuation', c_float),
    ]

class XRFdc_Cal_Freeze_Settings(Structure):
    _pack_ = 1
    _fields_ = [
        ('CalFrozen', u32),
        ('DisableFreezePin', u32),
        ('FreezeCalibration', u32),
    ]

class XRFdc_TileStatus(Structure):
    _pack_ = 1
    _fields_ = [
        ('IsEnabled', u32),
        ('TileState', u32),
        ('BlockStatusMask', u8),
        ('PowerUpState', u32),
        ('PLLState', u32),
    ]

class XRFdc_IPStatus(Structure):
    _pack_ = 1
    _fields_ = [
        ('DACTileStatus', XRFdc_TileStatus * int(4)),
        ('ADCTileStatus', XRFdc_TileStatus * int(4)),
        ('State', u32),
    ]

class XRFdc_BlockStatus(Structure):
    _pack_ = 1
    _fields_ = [
        ('SamplingFreq', c_double),
        ('AnalogDataPathStatus', u32),
        ('DigitalDataPathStatus', u32),
        ('DataPathClocksStatus', u8),
        ('IsFIFOFlagsEnabled', u8),
        ('IsFIFOFlagsAsserted', u8),
    ]

class XRFdc_DACBlock_AnalogDataPath_Config(Structure):
    _pack_ = 1
    _fields_ = [
        ('BlockAvailable', u32),
        ('InvSyncEnable', u32),
        ('MixMode', u32),
        ('DecoderMode', u32),
    ]

class XRFdc_DACBlock_DigitalDataPath_Config(Structure):
    _pack_ = 1
    _fields_ = [
        ('MixerInputDataType', u32),
        ('DataWidth', u32),
        ('InterpolationMode', u32),
        ('FifoEnable', u32),
        ('AdderEnable', u32),
        ('MixerType', u32),
        ('NCOFreq', c_double),
    ]

class XRFdc_ADCBlock_AnalogDataPath_Config(Structure):
    _pack_ = 1
    _fields_ = [
        ('BlockAvailable', u32),
        ('MixMode', u32),
    ]

class XRFdc_ADCBlock_DigitalDataPath_Config(Structure):
    _pack_ = 1
    _fields_ = [
        ('MixerInputDataType', u32),
        ('DataWidth', u32),
        ('DecimationMode', u32),
        ('FifoEnable', u32),
        ('MixerType', u32),
        ('NCOFreq', c_double),
    ]

class XRFdc_DACTile_Config(Structure):
    _pack_ = 1
    _fields_ = [
        ('Enable', u32),
        ('PLLEnable', u32),
        ('SamplingRate', c_double),
        ('RefClkFreq', c_double),
        ('FabClkFreq', c_double),
        ('FeedbackDiv', u32),
        ('OutputDiv', u32),
        ('RefClkDiv', u32),
        ('MultibandConfig', u32),
        ('MaxSampleRate', c_double),
        ('NumSlices', u32),
        ('LinkCoupling', u32),
        ('DACBlock_Analog_Config', XRFdc_DACBlock_AnalogDataPath_Config * int(4)),
        ('DACBlock_Digital_Config', XRFdc_DACBlock_DigitalDataPath_Config * int(4)),
    ]

class XRFdc_ADCTile_Config(Structure):
    _pack_ = 1
    _fields_ = [
        ('Enable', u32),
        ('PLLEnable', u32),
        ('SamplingRate', c_double),
        ('RefClkFreq', c_double),
        ('FabClkFreq', c_double),
        ('FeedbackDiv', u32),
        ('OutputDiv', u32),
        ('RefClkDiv', u32),
        ('MultibandConfig', u32),
        ('MaxSampleRate', c_double),
        ('NumSlices', u32),
        ('ADCBlock_Analog_Config', XRFdc_ADCBlock_AnalogDataPath_Config * int(4)),
        ('ADCBlock_Digital_Config', XRFdc_ADCBlock_DigitalDataPath_Config * int(4)),
    ]

class XRFdc_Config(Structure):
    _pack_ = 1
    _fields_ = [
        ('DeviceId', u32),
        ('BaseAddr', metal_phys_addr_t),
        ('ADCType', u32),
        ('MasterADCTile', u32),
        ('MasterDACTile', u32),
        ('ADCSysRefSource', u32),
        ('DACSysRefSource', u32),
        ('IPType', u32),
        ('SiRevision', u32),
        ('DACTile_Config', XRFdc_DACTile_Config * int(4)),
        ('ADCTile_Config', XRFdc_ADCTile_Config * int(4)),
    ]
    
class XRFdc_DACBlock_AnalogDataPath(Structure):
    _pack_ = 1
    _fields_ = [
        ('Enabled', u32),
        ('MixedMode', u32),
        ('TerminationVoltage', c_double),
        ('OutputCurrent', c_double),
        ('InverseSincFilterEnable', u32),
        ('DecoderMode', u32),
        ('FuncHandler', POINTER(None)),
        ('NyquistZone', u32),
        ('AnalogPathEnabled', u8),
        ('AnalogPathAvailable', u8),
        ('QMC_Settings', XRFdc_QMC_Settings),
        ('CoarseDelay_Settings', XRFdc_CoarseDelay_Settings),
    ]

class XRFdc_DACBlock_DigitalDataPath(Structure):
    _pack_ = 1
    _fields_ = [
        ('MixerInputDataType', u32),
        ('DataWidth', u32),
        ('ConnectedIData', c_int),
        ('ConnectedQData', c_int),
        ('InterpolationFactor', u32),
        ('DigitalPathEnabled', u8),
        ('DigitalPathAvailable', u8),
        ('Mixer_Settings', XRFdc_Mixer_Settings),
    ]

class XRFdc_ADCBlock_AnalogDataPath(Structure):
    _pack_ = 1
    _fields_ = [
        ('Enabled', u32),
        ('QMC_Settings', XRFdc_QMC_Settings),
        ('CoarseDelay_Settings', XRFdc_CoarseDelay_Settings),
        ('Threshold_Settings', XRFdc_Threshold_Settings),
        ('NyquistZone', u32),
        ('CalibrationMode', u8),
        ('AnalogPathEnabled', u8),
        ('AnalogPathAvailable', u8),
    ]

class XRFdc_ADCBlock_DigitalDataPath(Structure):
    _pack_ = 1
    _fields_ = [
        ('MixerInputDataType', u32),
        ('DataWidth', u32),
        ('DecimationFactor', u32),
        ('ConnectedIData', c_int),
        ('ConnectedQData', c_int),
        ('DigitalPathEnabled', u8),
        ('DigitalPathAvailable', u8),
        ('Mixer_Settings', XRFdc_Mixer_Settings),
    ]

class XRFdc_ADC_Tile(Structure):
    _pack_ = 1
    _fields_ = [
        ('TileBaseAddr', u32),
        ('NumOfADCBlocks', u32),
        ('PLL_Settings', XRFdc_PLL_Settings),
        ('MultibandConfig', u8),
        ('ADCBlock_Analog_Datapath', XRFdc_ADCBlock_AnalogDataPath * int(4)),
        ('ADCBlock_Digital_Datapath', XRFdc_ADCBlock_DigitalDataPath * int(4)),
    ]

class XRFdc_DAC_Tile(Structure):
    _pack_ = 1
    _fields_ = _fields_ = [
        ('TileBaseAddr', u32),
        ('NumOfDACBlocks', u32),
        ('PLL_Settings', XRFdc_PLL_Settings),
        ('MultibandConfig', u8),
        ('DACBlock_Analog_Datapath', XRFdc_DACBlock_AnalogDataPath * int(4)),
        ('DACBlock_Digital_Datapath', XRFdc_DACBlock_DigitalDataPath * int(4)),
    ]
    
class XRFdc(Structure):
    _pack_ = 1
    _fields_ = [
        ('RFdc_Config', XRFdc_Config),
        ('IsReady', u32),
        ('ADC4GSPS', u32),
        ('BaseAddr', metal_phys_addr_t),
        ('io', POINTER(metal_io_region)),
        ('device', POINTER(metal_device)),
        ('DAC_Tile', XRFdc_DAC_Tile * int(4)),
        ('ADC_Tile', XRFdc_ADC_Tile * int(4)),
        ('StatusHandler', XRFdc_StatusHandler),
        ('CallBackRef', POINTER(None)),
        ('UpdateMixerScale', u8),
    ]

