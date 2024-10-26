# parse hwh xml to get parameters to pass to pyrfdc
import xml.etree.ElementTree as ET

# we store them as bytes so that the C guy
# can grab 'em easy
def get_pyconfig( xmlfn ):
    tree = ET.parse(xmlfn)
    root = tree.getroot()
    paramDict = {}
    for child in root.iter():
        name = child.get('NAME')
        value = child.get('VALUE')
        if name is not None:
            paramDict[bytes(name,encoding='utf-8')] = bytes(value,encoding='utf-8')
    return paramDict

                  
