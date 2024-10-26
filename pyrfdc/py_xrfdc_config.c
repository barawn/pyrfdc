/* this is the shittiest garbage I've ever written */
#include <Python.h>
#include "xrfdc.h"



int Py_xrfdc_config_asint(PyObject *dict,
			  char *key);

double Py_xrfdc_config_asdouble(PyObject *dict,
				char *key);

int Py_xrfdc_config_asbool(PyObject *dict,
			   char *key);

// THESE HAVE ALL BEEN CHECKED
// THEY COMPILE, WHICH MEANS THE OBJECT EXISTS IN THE STRUCT
// AND THE STRINGS ALL HAVE BEEN CHECKED TO EXIST IN THE XML
// I DO ABSOLUTELY ZERO FUCKING CHECKING HERE
void Py_xrfdc_config_fill(PyObject *dict,
			  XRFdc_Config *cfg) {
  // dummy crap
  cfg->BaseAddr = 0;
#define PYCFG(t) cfg->t
#define PYDI(n, str) PYCFG( n ) = Py_xrfdc_config_asint( dict , str)
#define PYDD(n, str) PYCFG( n ) = Py_xrfdc_config_asdouble( dict , str)
#define PYDB(n, str) PYCFG( n ) = Py_xrfdc_config_asbool( dict , str )

  PYDI( ADCType , "C_High_Speed_ADC");
  PYDI( ADCSysRefSource , "C_Sysref_Source");
  PYDI( DACSysRefSource , "C_Sysref_Source");
  PYDI( IPType , "C_IP_Type" );
  PYDI( SiRevision , "C_Silicon_Revision");

#define PYTILE( type, n ) \
  PYDI( type##Tile_Config[n].Enable , "C_"#type #n"_Enable"); \
  PYDB( type##Tile_Config[n].PLLEnable, "C_"#type #n"_PLL_Enable"); \
  PYDD( type##Tile_Config[n].SamplingRate, "C_"#type #n"_Sampling_Rate"); \
  PYDD( type##Tile_Config[n].RefClkFreq, "C_"#type #n"_Refclk_Freq"); \
  PYDD( type##Tile_Config[n].FabClkFreq, "C_"#type #n"_Fabric_Freq"); \
  PYDI( type##Tile_Config[n].FeedbackDiv, "C_"#type #n"_FBDIV"); \
  PYDI( type##Tile_Config[n].OutputDiv, "C_"#type #n"_OutDiv"); \
  PYDI( type##Tile_Config[n].RefClkDiv, "C_"#type #n"_Refclk_Div"); \
  PYDI( type##Tile_Config[n].MultibandConfig, "C_"#type #n"_Band"); \
  PYDD( type##Tile_Config[n].MaxSampleRate, "C_"#type #n"_Fs_Max"); \
  PYDI( type##Tile_Config[n].NumSlices, "C_"#type #n"_Slices")

  /* so painful */
#define DADP(n,j, name) DACTile_Config[ n ].DACBlock_Analog_Config[ j ].name
#define DDDP(n,j, name) DACTile_Config[ n ].DACBlock_Digital_Config[ j ].name
#define AADP(n,j, name) ADCTile_Config[ n ].ADCBlock_Analog_Config[ j ].name
#define ADDP(n,j, name) ADCTile_Config[ n ].ADCBlock_Digital_Config[ j ].name

  /* OH MY DEAR GOD SOMEONE EFFED UP AND MISSPELLED THE INVERSE SINC FILTER */
  /* AND THEY JUST LEFT IT */
#define DACBLOCK( i , j ) \
  PYDB( DADP( i, j, BlockAvailable ), "C_DAC_Slice" #i #j "_Enable");	\
  PYDB( DADP( i, j, InvSyncEnable ), "C_DAC_Invsinc_Ctrl" #i #j );	\
  PYDI( DADP( i, j, MixMode ), "C_DAC_Mixer_Mode" #i #j );		\
  PYDI( DADP( i, j, DecoderMode ), "C_DAC_Decoder_Mode" #i #j );		\
  PYDI( DDDP( i, j, MixerInputDataType ), "C_DAC_Data_Type" #i #j );	\
  PYDI( DDDP( i, j, DataWidth ), "C_DAC_Data_Width" #i #j );		\
  PYDI( DDDP( i, j, InterpolationMode ), "C_DAC_Interpolation_Mode" #i #j ); \
  PYDI( DDDP( i, j, MixerType ), "C_DAC_Mixer_Type" #i #j )
  
#define ADCBLOCK( i , j ) \
  PYDB( AADP( i, j, BlockAvailable ), "C_ADC_Slice" #i #j "_Enable");	\
  PYDI( AADP( i, j, MixMode ), "C_ADC_Mixer_Mode" #i #j );		\
  PYDI( ADDP( i, j, MixerInputDataType ), "C_ADC_Data_Type" #i #j );	\
  PYDI( ADDP( i, j, DataWidth ), "C_ADC_Data_Width" #i #j );		\
  PYDI( ADDP( i, j, DecimationMode ), "C_ADC_Decimation_Mode" #i #j );	\
  PYDI( ADDP( i, j, MixerType ), "C_ADC_Mixer_Type" #i #j )  

  /* four tiles, and four blocks under each */
  PYTILE(DAC, 0);
  DACBLOCK(0, 0);
  DACBLOCK(0, 1);
  DACBLOCK(0, 2);
  DACBLOCK(0, 3);
  PYTILE(ADC, 0);
  ADCBLOCK(0, 0);
  ADCBLOCK(0, 1);
  ADCBLOCK(0, 2);
  ADCBLOCK(0, 3);
  
  PYTILE(DAC, 1);
  DACBLOCK(1, 0);
  DACBLOCK(1, 1);
  DACBLOCK(1, 2);
  DACBLOCK(1, 3);
  PYTILE(ADC, 1);
  ADCBLOCK(1, 0);
  ADCBLOCK(1, 1);
  ADCBLOCK(1, 2);
  ADCBLOCK(1, 3);

  PYTILE(DAC, 2);
  DACBLOCK(2, 0);
  DACBLOCK(2, 1);
  DACBLOCK(2, 2);
  DACBLOCK(2, 3);
  PYTILE(ADC, 2);
  ADCBLOCK(2, 0);
  ADCBLOCK(2, 1);
  ADCBLOCK(2, 2);
  ADCBLOCK(2, 3);

  PYTILE(DAC, 3);
  DACBLOCK(3, 0);
  DACBLOCK(3, 1);
  DACBLOCK(3, 2);
  DACBLOCK(3, 3);
  PYTILE(ADC, 3);
  ADCBLOCK(3, 0);
  ADCBLOCK(3, 1);
  ADCBLOCK(3, 2);
  ADCBLOCK(3, 3);
}

int Py_xrfdc_config_asint(PyObject *dict,
			  char *key) {
  PyObject *py_k;
  PyObject *py_v;
  py_k = PyBytes_FromString(key);
  py_v = PyDict_GetItem(dict, py_k);
  Py_DECREF(py_k);
  return atoi(PyBytes_AsString(py_v));
}
			  
double Py_xrfdc_config_asdouble(PyObject *dict,
			        char *key) {
  PyObject *py_k;
  PyObject *py_v;
  py_k = PyBytes_FromString(key);
  py_v = PyDict_GetItem(dict, py_k);
  Py_DECREF(py_k);
  return atof(PyBytes_AsString(py_v));
}
    
int Py_xrfdc_config_asbool(PyObject *dict,
			   char *key) {
  PyObject *py_k;
  PyObject *py_v;
  py_k = PyBytes_FromString(key);
  py_v = PyDict_GetItem(dict, py_k);
  Py_DECREF(py_k);
  return (PyBytes_AsString(py_v)[0] == 't') ? 1 : 0;
}

