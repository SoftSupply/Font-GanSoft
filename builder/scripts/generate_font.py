import fontforge
import os
import md5
import subprocess
import tempfile
import json
import copy
import datetime

SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
INPUT_SVG_DIR = os.path.join(SCRIPT_PATH, '..', '..', 'src')
OUTPUT_FONT_DIR = os.path.join(SCRIPT_PATH, '..', '..', 'fonts')
MANIFEST_PATH = os.path.join(SCRIPT_PATH, '..', 'manifest.json')
BUILD_DATA_PATH = os.path.join(SCRIPT_PATH, '..', 'build_data.json')
AUTO_WIDTH = True
KERNING = 15

cp = 0xf100
m = md5.new()

f = fontforge.font()
f.encoding = 'UnicodeFull'
f.design_size = 16
f.em = 512
f.ascent = 448
f.descent = 64

build_file = open(BUILD_DATA_PATH, 'r')
build_data = json.loads(build_file.read())
build_file.close()
print "Load build data, Icons: %s" % (len(build_data['icons']))


if os.path.isfile(MANIFEST_PATH):
    manifest_file = open(MANIFEST_PATH, 'r')
    manifest_data = json.loads(manifest_file.read())
    manifest_file.close()
    print "Load manifest data, Icons: %s" % (len(manifest_data['icons']))
else:
    manifest_data = copy.deepcopy(build_data)

manifest_data['icons'] = []
now = datetime.datetime.now()

font_name = manifest_data['name']
font_version = manifest_data['version']
font_author = manifest_data['author'] + ' ' + str(now.year)
m.update(font_name + ';')
m.update(font_version + ';')
m.update(font_author  + ';')
m.update(manifest_data['prefix'] + ';')

for dirname, dirnames, filenames in os.walk(INPUT_SVG_DIR):
  for filename in filenames:
    name, ext = os.path.splitext(filename)
    filePath = os.path.join(dirname, filename)
    size = os.path.getsize(filePath)

    if ext in ['.svg', '.eps']:

      # see if this file is already in the manifest
      chr_code = None
      for icon in build_data['icons']:
        if icon['name'] == name:
          chr_code = icon['code']
          break

      if chr_code is None:
        # this is a new src icon
        print 'New Icon: \n - %s' % (name)

        while True:
          chr_code = '0x%x' % (cp)
          already_exists = False
          for icon in build_data['icons']:
            if icon.get('code') == chr_code:
              already_exists = True
              cp += 1
              chr_code = '0x%x' % (cp)
              continue
          if not already_exists:
            break

      #print ' - %s' % chr_code
      manifest_data['icons'].append({
        'name': name,
        'code': chr_code
      })    

      if ext in ['.svg']:
        # hack removal of <switch> </switch> tags
        svgfile = open(filePath, 'r+')
        tmpsvgfile = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
        svgtext = svgfile.read()
        svgfile.seek(0)

        # replace the <switch> </switch> tags with 'nothing'
        svgtext = svgtext.replace('<switch>', '')
        svgtext = svgtext.replace('</switch>', '')

        tmpsvgfile.file.write(svgtext)

        svgfile.close()
        tmpsvgfile.file.close()

        filePath = tmpsvgfile.name
        # end hack

      m.update(name + str(size) + ';')
      glyph = f.createChar(int(chr_code, 16))
      glyph.importOutlines(filePath)

      # if we created a temporary file, let's clean it up
      if tmpsvgfile:
        os.unlink(tmpsvgfile.name)

      # set glyph size explicitly or automatically depending on autowidth
      if AUTO_WIDTH:
        glyph.left_side_bearing = glyph.right_side_bearing = 0
        glyph.round()

    # resize glyphs if autowidth is enabled
    if AUTO_WIDTH:
      f.autoWidth(0, 0, 512)

  fontfile = '%s/font-gansoft' % (OUTPUT_FONT_DIR)

build_hash = m.hexdigest()

if build_hash == manifest_data.get('build_hash'):
  print "Source files unchanged, did not rebuild fonts"

else:
  manifest_data['build_hash'] = build_hash

  f.fontname = font_name
  f.familyname = font_name
  f.fullname = font_name
  f.version = font_version
  f.copyright = font_author
  f.generate(fontfile + '.ttf')
  f.generate(fontfile + '.svg')

  # Fix SVG header for webkit
  # from:
  # https://github.com/fontello/font-builder/blob/master/bin/fontconvert.py
  svgfile = open(fontfile + '.svg', 'r+')
  svgtext = svgfile.read()
  svgfile.seek(0)
  svgfile.write(svgtext.replace('''<svg>''', '''<svg xmlns="http://www.w3.org/2000/svg">'''))
  svgfile.close()
  
  print "" 
  scriptPath = os.path.dirname(os.path.realpath(__file__))
  try:
    subprocess.Popen([scriptPath + '/sfnt2woff', fontfile + '.ttf'], stdout=subprocess.PIPE)
  except OSError:
    # If the local version of sfnt2woff fails (i.e., on Linux), try to use the
    # global version.  This allows us to avoid forcing OS X users to compile
    # sfnt2woff from source, simplifying install.
    try: 
      subprocess.call(['sfnt2woff', fontfile + '.ttf']) 
    except OSError: 
      subprocess.call('ttf2woff ' + fontfile + '.ttf ' + fontfile + '.woff', shell=True) 

  # eotlitetool.py script to generate IE7-compatible .eot fonts
  subprocess.call('python ' + scriptPath + '/eotlitetool.py ' + fontfile + '.ttf -o ' + fontfile + '.eot', shell=True)
  if os.path.isfile(fontfile + '.eot'): 
    os.remove(fontfile + '.eot') 
  os.rename(fontfile + '.eotlite', fontfile + '.eot') 

  # Hint the TTF file
  subprocess.call('ttfautohint -s -f -n ' + fontfile + '.ttf ' + fontfile + '-hinted.ttf > /dev/null 2>&1 && mv ' + fontfile + '-hinted.ttf ' + fontfile + '.ttf', shell=True)

  manifest_data['icons'] = sorted(manifest_data['icons'], key=lambda k: k['name'])
  build_data['icons'] = sorted(build_data['icons'], key=lambda k: k['name'])

  print "Save Manifest, Icons: %s" % (len(manifest_data['icons']))
  f = open(MANIFEST_PATH, 'w')
  f.write(json.dumps(manifest_data, indent=2, separators=(',', ': ')))
  f.close()

