#!/usr/bin/env python3.8
# pod-dl.py
# Pass xml url and download all podcast episodes to current directory.
# Doesn't handle errors well or label non-mp3 files correctly.
# TODO: Create XML file for adding local copy to podcast apps.
#       Check output_dir before writting.

"""
Copyright (c) 2018-2021, William Blair <wablair@gmail.com>

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
"""

import argparse
import xml.etree.ElementTree as ET
import requests
import unicodedata
import re
import os
import io

parser = argparse.ArgumentParser(description='Download podcasts from rss ' +
  'feed.')
parser.add_argument('url')
parser.add_argument('-p', '--prefix')
parser.add_argument('-o', '--output_dir')
args = parser.parse_args()
feed_url = args.url
output_dir = None
prefix = None
if args.output_dir:
    output_dir = args.output_dir
if args.prefix:
    prefix = args.prefix

# slugify() from django.utils.text
"""
Copyright (c) Django Software Foundation and individual contributors.
All rights reserved.

Redistribution and use in source and binary forms, with or without modification
, are permitted provided that the following conditions are met:

    1. Redistributions of source code must retain the above copyright notice,
       this list of conditions and the following disclaimer.

    2. Redistributions in binary form must reproduce the above copyright
       notice, this list of conditions and the following disclaimer in the
       documentation and/or other materials provided with the distribution.

    3. Neither the name of Django nor the names of its contributors may be used
       to endorse or promote products derived from this software without
       specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
def slugify(value, allow_unicode=False):
    """
    Convert to ASCII if 'allow_unicode' is False. Convert spaces to hyphens.
    Remove characters that aren't alphanumerics, underscores, or hyphens.
    Convert to lowercase. Also strip leading and trailing whitespace.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii',
          'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    return (re.sub(r'[-\s]+', '-', value))

r = requests.get(feed_url)
xml_file_like = io.BytesIO(r.content)
tree = ET.parse(xml_file_like)
root = tree.getroot()
files = []
for child in root:
    for child2 in child:
        if child2.tag == 'item':
            filename = None
            url = None
            for child3 in child2:
                if child3.tag == 'title':
                    filename = "{}.mp3".format(slugify(child3.text))
                if child3.tag == 'enclosure':
                    url = child3.attrib['url']

                if filename and url and [url, filename] not in files:
                    files.append([url, filename])

count = 1

files.reverse()

for file in files:
    url = file[0]
    filename = file[1]
    if os.path.isfile(filename):
        continue
    if prefix:
        filename = "{}{:03d}_{}".format(prefix, count, filename)
    if output_dir:
        filename = "{}{}".format(output_dir, filename)
    print("Getting {} from {}".format(filename, url))
    try:
        r = requests.get(url, stream=True)
        r.raise_for_status()
        with open(filename, 'wb') as handle:
            for block in r.iter_content(1024):
                handle.write(block)
        count = count + 1
    except:
        print("Could not get {}".format(url))
        continue
