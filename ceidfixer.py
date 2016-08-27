#! python2
from fastkml import kml
import re


RE_STYLEURL = re.compile("^#\w+")
RE_STYLEURL_EXPOSED = re.compile(r'^#.*?(?<!un)exposed.+')
RE_STYLEURL_UNEXPOSED = re.compile("^#.*?exposed.+")
RE_KLASS = re.compile("^\([0-5]\) .+")
RE_HTML_OPEN = re.compile(r"<[a-z0-9 ]{1,12}>", re.I)
RE_HTML_CLOSE = re.compile(r"</[a-z0-9 ]{1,12}>", re.I)
RE_CDATA_FIELD = re.compile(r'((<B>)?(crater field|class|region|country|diameter|position|age|drilled|exposed|references)(:|: )</B> *?)(?P<data>[A-Z0-9-]{1}[a-z0-9]*)(<br>)?', re.I)


def get_fldr_vars(kfldr):
    """Parse fastkml structure fldr for: structure name, class and exposed"""
    assert isinstance(kfldr, kml.Folder)
    namefield = kfldr.name
    # extract class ranking from top-level FLDR>Name field
    klass = get_class_val(namefield)
    # find FLDR>Placemark which is for our icon
    for pm in get_feat_list(kfldr):
        if str(get_placemark_type(pm)) == 'point':
            exposed = get_exposed_from_styleurl(pm.styleUrl)
            name = pm.name
    return dict(name=name, exposed=exposed, klass=klass)


def get_class_val(namefield):
    """Get structure's class (ranking) from FOLDER's name value"""
    d = {0: '0or1', 1: '0or1', 2: '2', 3: '3', 4: '4or5', 5: '4or5',}
    assert RE_KLASS.match(namefield), "Name field must be a string of format:\t '(klass) Name'"
    return d.get(int(namefield[1:2]), "6")


def get_exposed_from_styleurl(stylestr):
    """Retrieve structure's exposed status from icon placemark styleUrl"""
    assert RE_STYLEURL.match(stylestr), "Style string must be of format:\t '#foo_bar'"
    # if not RE_STYLEURL_EXPOSED.match(stylestr) or not RE_STYLEURL_UNEXPOSED.match(stylestr):
    #     raise Exception("Weird incoming naming convention")
    if RE_STYLEURL_EXPOSED.match(stylestr): 
        return "exposed"
    elif RE_STYLEURL_UNEXPOSED.match(stylestr):
        return "unexposed"
    else:
        # TODO: parse HTML
        return "other"


def get_var_from_description(cdata, varname):
    """Extract structure variable (eg name, exposed) from CDATA (description) in point placemark"""
    
    # TODO: finish code for this
    VARS = ["name", "crater field", "class", "region", "country",
            "diameter", "position", "age", "drilled", "exposed"]
    assert varname.lower() in VARS, \
        "varname {} needs to be in {}".format(varname, ", ".join(VARS))
    assert cdata.startswith('CDATA'), "Not a CDATA field"
    l = [x for x in re.split(r':|: | (</B>)? ?', cdata) if x is not None]

    # make a list of html tags
    #TAGS_OPEN, TAGS_CLOSE = re.findall(RE_HTML_OPEN, cdata), re.findall(RE_HTML_CLOSE, cdata)
    #TAGS_ALL = TAGS_OPEN + TAGS_CLOSE
    
    #test_str = u"<B>Name:</B> TheName"
    # partition at ": "
    
    
    if varname.lower() in cdata.lower(): 
        # get html tags in cdata

        # find position of varname... assume "varname: </B>"
        posn = cdata.lower().find(varname.lower()) + len(varname+": ")
        # 

def get_placemark_type(pm):
    """Determine whether fastkml Placemark object is for KML icon or polygon"""
    if not hasattr(pm, 'geometry'):
        pass     # add to error list
    is_type = lambda p, pmtype: str(p.geometry).lower().startswith(pmtype)
    # check if placemark is an icon/point or polygon/linestring or other
    if is_type(pm, 'point'):
        return "point"
    elif is_type(pm, 'linestring'):
        return "polygon"
    else:
        return "other"


def create_styleurl(pm, **kwargs):
    """Takes a placemark object and returns styleUrl with updated naming conventions"""
    assert isinstance(pm, (kml.Placemark, kml.Folder)), "Not a fastkml placemark/folder"
    klass = kwargs.get("klass") #or get_class_val(pm)
    if get_placemark_type(pm) == "point":
        exposed = kwargs.get("exposed") or get_exposed_from_styleurl(pm.styleUrl)
        return "#style_pm_{}_class{}".format(exposed, klass)
    elif get_placemark_type(pm) == "polygon":
        return "#class{}".format(klass)
    else:
        return "#error"


# def replace_styleurls(kfldr):
#     """Rename FLDR>Placemark>styleUrl fields where kfldr is fastkml folder object"""
#     assert isinstance(kfldr, (fastkml.kml.Folder, kml.Folder)), "Must be fastkml structure folder object"
#     vars = get_fldr_vars(kfldr)
#     # get placemarks in kfldr
#     pms = get_feat_list(kfldr)
#     for pm in pms:
#         if get_placemark_type(pm) == 'icon':
#             newstyle_str = create_styleurl(pm, **vars)
#             pm.styleUrl = newstyle_str
#         elif get_placemark_type(pm) == 'polygon':
#             newstyle_str = create_styleurl(pm, **vars)
#             pm.styleUrl = newstyle_str        # TODO: setattr for styleUrl



# fastkml functions

def get_feat_list(struct, names=False):
    """Return a list of features in a fastkml object"""
    if isinstance(struct, list): 
        if len(struct) == 1 and isinstance(struct[0], kml.Document):
            return get_feat_list(struct[0], names)
    assert isinstance(struct, (kml.Document, kml.Folder, kml.Placemark)), \
        "Object must be fastkml feature! Not type {}!".format(str(type(struct)))
    fl = list(struct.features())
    namel = [x.name for x in fl]
    dictcomp = {k:v for k,v in zip(namel, fl)}
    return fl if not names else dictcomp

get_features = get_feat_list



