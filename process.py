#! python2
from fastkml import kml
from ceidfixer import *

from pprint import pprint as pp
import os, sys

#docfile = os.path.join(os.path.split(__file__)[0], "doc.kml")[8:] # "/var/mobile/Containers/Shared/AppGroup/AA78F2EC-3EE8-40F4-A318-8A9AB1BCB5FF/Pythonista3/Documents/ceid-fixer/doc.kml"
docfile = os.path.join(os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))), 'doc.kml')

with open(docfile, 'r') as fo:
    doc = fo.read()

k = kml.KML()

k.from_string(doc)

features = list(k.features())
f2 = get_feat_list(features)
root = f2[0]                                 # ceid root folder
f3 = continents = get_feat_list(root)        # continent folders

# setup list of structure folders for each continent [structure1, structure2...]
AU, AF, AN, AS, EU, SA, NA = [get_feat_list(x) for x in continents]

# eg Acraman
acraman = AU[1]
acraman_placemarks = get_feat_list(acraman)
pm1, pm2 = acraman_placemarks

# # placemark functions
# # pm1.address       pm1.description   pm1.from_element  pm1.isopen        pm1.phoneNumber   pm1.targetId
# # pm1.append_style  pm1.end           pm1.from_string   pm1.link          pm1.snippet       pm1.timeStamp
# # pm1.author        pm1.etree_element pm1.geometry      pm1.name          pm1.styleUrl      pm1.to_string
# # pm1.begin         pm1.extended_data pm1.id            pm1.ns            pm1.styles        pm1.visibility
#
# # cycle through each Australian structure
for structure in AU:
    # get namefield for class extraction,
    # ie "(0) Acraman, " => class 0or1
    vars = get_fldr_vars(structure)
    name, klass, exposed = [vars[x] for x in ("name", "klass", "exposed")]
    pms = get_feat_list(structure)    # get placemarks for the structure

    pm_icon, pm_poly = "", ""
    # check placemark is icon or polygon
    for pm in pms:
        if get_placemark_type(pm) == "icon":
            print pm.name

        
