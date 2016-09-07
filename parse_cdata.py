import bs4
from bs4 import BeautifulSoup

with open("cdata.html", "r") as fo:
    html_doc = fo.read()

soup = BeautifulSoup(html_doc, "html.parser")

# strip html tags
pieces = [x for x in soup.stripped_strings]


titles = [t.rstrip(": ") for t in pieces if pieces.index(t) % 2 == 0]
data = [d for d in pieces if pieces.index(d) % 2 == 1]

# keys for dict comp (everything except "exposed")
KEYZ = (
    "name", "crater field", "region", "country", "drilled?", 
    "age", "position", "diameter", "references", "description"
    )

dcomp = {k: v for k, v in zip(titles, data) if k.lower().rstrip(":") in KEYZ}

# check "exposed" has a value
if len(pieces) % 2 != 0:
    ei = pieces.index("Exposed?:")
    dcomp.update({
        "exposed": pieces[ei+1] if pieces[ei+1].lower() in ("y", "n") else "?"
    })
