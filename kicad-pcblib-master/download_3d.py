#!/usr/bin/python

import io
import os
import re
import sys
import zipfile

try:
    import urllib.request
except ImportError:
    import urllib2
    urlopen = urllib2.urlopen
else:
    urlopen = urllib.request.urlopen


URL="http://smisioto.no-ip.org/elettronica/kicad/kicad-en.htm"
URLBASE="http://smisioto.no-ip.org"
OUTDIR="3d"

def print_no_newline (s):
    """Print s without a newline. Cross Python2/3 compatible."""
    sys.stdout.write (s)
    sys.stdout.flush ()

def copyfile (dest, src):
    while True:
        block = src.read (1024)
        dest.write (block)
        if len (block) < 1024:
            break

def makepath (path):
    path_components = path.split ('/')
    incremental_paths = [path_components[:i] for i in range (1, len (path_components))]
    for i in incremental_paths:
        i = os.path.join (*i)
        if not os.path.isdir (i):
            os.mkdir (i)

# First, download the index page and extract the list of packages
packages = []
f = urlopen (URL)
for line in f:
    line = line.decode ("utf8").strip ()
    if 'href="/kicad_libs/packages3d/' not in line:
        continue
    package_url_match = re.match (r'<A href="([^"]+)"', line)
    packages.append (URLBASE + package_url_match.group (1))
f.close ()

# Now, grab each one
extracted_license = False   # only extract the license once
for url in packages:

    name_m = re.search (r'(3d_.+.zip)', url)
    if name_m is None:
        name = url
    else:
        name = name_m.group (1)
    print_no_newline ("Downloading %s..." % name)
    sys.stdout.flush ()

    f = urlopen (url)
    data = f.read ()
    f.close ()

    virtfile = io.BytesIO (data)
    zf = zipfile.ZipFile (virtfile)

    # Manually extract, as we change the paths a bit
    count = 0
    for filename in zf.namelist ():
        if filename == "walter/license.txt" and not extracted_license:
            extracted_license = True
            destfn = os.path.join (OUTDIR, "license.txt")
            makepath (destfn)
            with zf.open (filename) as fsrc, open (destfn, 'wb') as fdest:
                copyfile (fdest, fsrc)
        elif filename.endswith (".wrl") or filename.endswith (".wings"):
            count += 1
            destfn = os.path.join (OUTDIR, filename.replace ("walter/", ""))
            makepath (destfn)
            with zf.open (filename) as fsrc, open (destfn, 'wb') as fdest:
                copyfile (fdest, fsrc)

    zf.close ()

    print ("%d models" % count)
