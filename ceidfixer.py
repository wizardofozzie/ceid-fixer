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

# TODO fix
RE_TAGGED_DATA = re.compile(r"(?P<starttag><(?P<tagname>[a-zA-Z0-9])[^>]*>)(?P<data>.*)(?P<endtag></?[a-zA-Z0-9]>)")


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
    d = {
        0: '0or1', 1: '0or1', 2: '2',
        3: '3', 4: '4or5', 5: '4or5',
        }
    assert RE_KLASS.match(namefield), \
        "Name field must be a string of format:\t '(klass) Name'"
    return d.get(int(namefield[1:2]), "6")


def get_exposed_from_styleurl(stylestr):
    """Retrieve structure's exposed status from icon placemark styleUrl"""
    assert RE_STYLEURL.match(stylestr), "Style string must be of format:\t '#foo_bar'"
    if RE_STYLEURL_EXPOSED.match(stylestr): 
        return "exposed"
    elif RE_STYLEURL_UNEXPOSED.match(stylestr):
        return "unexposed"
    # else:
    #     # TODO: parse HTML
    #     return "other"


def get_var_from_description(cdata, varname):
    """Extract structure variable (eg name, exposed) from CDATA (description) in point placemark"""
    VARS = [
        "name", "crater field", "class", "region", "country",
        "diameter", "position", "age", "drilled", "exposed"
        ]
    assert cdata.startswith('CDATA'), "Not a CDATA field"
    assert varname.lower() in VARS, \
        "varname {} needs to be in {}".format(varname, ", ".join(VARS))

    # TODO: finish code for this
    # strip html tags
    cdata = re.sub(
        r'(<b>)|(</b>)|(</B>)|(<B>)|(<HTML>)|(<BODY>)',
        '', cdata, 0, re.I
    )
    # make <br> => <BR> and <p> => <P>
    cdata = re.sub(r'<br>', r'<BR>', cdata)
    cdata = re.sub(r'<p>', r'<P>', cdata)
    # split at html <br>/<p> into list
    l = [x for x in re.split('(<BR>)|(<P>)', cdata, re.I) if x is not None]


    # ['Name: Liverpool',
    #  '<br>',
    #  'Class: 1<BR>Crater Field: -<BR>Region: Northern Territory<BR>Country: Australia (Australia)<BR>Diameter: 2 km<BR>Position:
    # -12.3959, 134.0474<BR>Age: Neoproterozoic?<BR>Drilled?: N<BR>Exposed?: ',
    #  '<p>',
    #  'Description:<BR>Simple structure in flat-lying Paleoproterozoic and Neoproterozoic sandstones in a swampy flood plain of th


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

