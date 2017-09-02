from subprocess import call
import os
import json


BUILDER_PATH = os.path.dirname(os.path.abspath(__file__))
ROOT_PATH = os.path.join(BUILDER_PATH, '..')
FONTS_FOLDER_PATH = os.path.join(ROOT_PATH, 'fonts')
CSS_FOLDER_PATH = os.path.join(ROOT_PATH, 'css')
SCSS_FOLDER_PATH = os.path.join(ROOT_PATH, 'scss')
LESS_FOLDER_PATH = os.path.join(ROOT_PATH, 'less')


def main():
  generate_font_files()

  data = get_build_data()

  rename_svg_glyph_names(data)
  generate_scss(data)
  generate_less(data)
  generate_cheatsheet(data)
  generate_component_json(data)
  generate_composer_json(data)
  generate_bower_json(data)


def generate_font_files():
  print "Generate Fonts"
  cmd = "fontforge -script %s/scripts/generate_font.py" % (BUILDER_PATH)
  call(cmd, shell=True)


def rename_svg_glyph_names(data):
  # hacky and slow (but safe) way to rename glyph-name attributes
  svg_path = os.path.join(FONTS_FOLDER_PATH, 'font-gansoft.svg')
  svg_file = open(svg_path, 'r+')
  svg_text = svg_file.read()
  svg_file.seek(0)

  for icon in data['icons']:
    # uniF2CA
    org_name = 'uni%s' % (icon['code'].replace('0x', '').upper())
    gs_name = 'gs-%s' % (icon['name'])
    svg_text = svg_text.replace(org_name, gs_name)

  svg_file.write(svg_text)
  svg_file.close()


def generate_less(data):
  print "Generate LESS"
  font_name = data['name']
  font_version = data['version']
  css_prefix = data['prefix']
  variables_file_path = os.path.join(LESS_FOLDER_PATH, '_font-gansoft-variables.less')
  icons_file_path = os.path.join(LESS_FOLDER_PATH, '_font-gansoft-icons.less')

  d = []
  d.append('@font-gansoft-font-path: "../fonts";')
  d.append('@font-gansoft-font-family: "%s";' % (font_name) )
  d.append('@font-gansoft-version: "%s";' % (font_version) )
  d.append('@font-gansoft-prefix: %s;' % (css_prefix) )
  d.append('')
  for icon in data['icons']:
    chr_code = icon['code'].replace('0x', '\\')
    d.append('@font-gansoft-var-%s: "%s";' % (icon['name'], chr_code) )
  f = open(variables_file_path, 'w')
  f.write( '\n'.join(d) )
  f.close()

  d = []
  group = [ '.%s' % (data['name'].lower()) ]
  for icon in data['icons']:
    group.append('.@{font-gansoft-prefix}%s:before' % (icon['name']) )

  d.append( ',\n'.join(group) )

  d.append('{')
  d.append('  &:extend(.gs);')
  d.append('}')

  for icon in data['icons']:
    chr_code = icon['code'].replace('0x', '\\')
    d.append('.@{font-gansoft-prefix}%s:before { content: @font-gansoft-var-%s; }' % (icon['name'], icon['name']) )

  f = open(icons_file_path, 'w')
  f.write( '\n'.join(d) )
  f.close()


def generate_scss(data):
  print "Generate SCSS"
  font_name = data['name']
  font_version = data['version']
  css_prefix = data['prefix']
  variables_file_path = os.path.join(SCSS_FOLDER_PATH, '_font-gansoft-variables.scss')
  icons_file_path = os.path.join(SCSS_FOLDER_PATH, '_font-gansoft-icons.scss')

  d = []
  d.append('$font-gansoft-font-path: "../fonts" !default;')
  d.append('$font-gansoft-font-family: "%s" !default;' % (font_name) )
  d.append('$font-gansoft-version: "%s" !default;' % (font_version) )
  d.append('$font-gansoft-prefix: %s !default;' % (css_prefix) )
  d.append('')
  for icon in data['icons']:
    chr_code = icon['code'].replace('0x', '\\')
    d.append('$font-gansoft-var-%s: "%s";' % (icon['name'], chr_code) )
  f = open(variables_file_path, 'w')
  f.write( '\n'.join(d) )
  f.close()

  d = []
  group = [ '.%s' % (data['name'].lower()) ]
  for icon in data['icons']:
    group.append('.#{$font-gansoft-prefix}%s:before' % (icon['name']) )

  d.append( ',\n'.join(group) )

  d.append('{')
  d.append('  @extend .gs;')
  d.append('}')

  for icon in data['icons']:
    chr_code = icon['code'].replace('0x', '\\')
    d.append('.#{$font-gansoft-prefix}%s:before { content: $font-gansoft-var-%s; }' % (icon['name'], icon['name']) )

  f = open(icons_file_path, 'w')
  f.write( '\n'.join(d) )
  f.close()

  generate_css_from_scss(data)


def generate_css_from_scss(data):
  print "Generate CSS From SCSS"

  scss_file_path = os.path.join(SCSS_FOLDER_PATH, 'font-gansoft.scss')
  css_file_path = os.path.join(CSS_FOLDER_PATH, 'font-gansoft.css')
  css_min_file_path = os.path.join(CSS_FOLDER_PATH, 'font-gansoft.min.css')

  cmd = "sass %s %s --style compact" % (scss_file_path, css_file_path)
  call(cmd, shell=True)

  print "Generate Minified CSS From SCSS"
  cmd = "sass %s %s --style compressed" % (scss_file_path, css_min_file_path)
  call(cmd, shell=True)


def generate_cheatsheet(data):
  print "Generate Cheatsheet"

  cheatsheet_file_path = os.path.join(ROOT_PATH, 'cheatsheet.html')
  template_path = os.path.join(BUILDER_PATH, 'cheatsheet', 'template.html')
  icon_row_path = os.path.join(BUILDER_PATH, 'cheatsheet', 'icon-row.html')

  f = open(template_path, 'r')
  template_html = f.read()
  f.close()

  f = open(icon_row_path, 'r')
  icon_row_template = f.read()
  f.close()

  content = []

  for icon in data['icons']:
    css_code = icon['code'].replace('0x', '\\')
    escaped_html_code = icon['code'].replace('0x', '&amp;#x') + ';'
    html_code = icon['code'].replace('0x', '&#x') + ';'
    item_row = icon_row_template

    item_row = item_row.replace('{{name}}', icon['name'])
    item_row = item_row.replace('{{prefix}}', data['prefix'])
    item_row = item_row.replace('{{css_code}}', css_code)
    item_row = item_row.replace('{{escaped_html_code}}', escaped_html_code)
    item_row = item_row.replace('{{html_code}}', html_code)

    content.append(item_row)

  template_html = template_html.replace("{{font_name}}", data["name"])
  template_html = template_html.replace("{{font_version}}", data["version"])
  template_html = template_html.replace("{{icon_count}}", str(len(data["icons"])) )
  template_html = template_html.replace("{{content}}", '\n'.join(content) )

  f = open(cheatsheet_file_path, 'w')
  f.write(template_html)
  f.close()


def generate_component_json(data):
  print "Generate component.json"
  d = {
    "name": data['name'],
    "repo": "softsupply/font-gansoft",
    "description": "The GanSoft iconic font and CSS framework",
    "version": data['version'],
    "keywords": ["font", "gansoft", "fontgansoft", "icon", "font", "bootstrap"],
    "dependencies": {},
    "development": {},
    "license": "MIT",
    "styles": [
      "css/font-%s.css" % (data['name'].lower())
    ],
    "fonts": [
      "fonts/font-%s.eot" % (data['name'].lower()),
      "fonts/font-%s.svg" % (data['name'].lower()),
      "fonts/font-%s.ttf" % (data['name'].lower()),
      "fonts/font-%s.woff" % (data['name'].lower())
    ]
  }
  txt = json.dumps(d, indent=4, separators=(',', ': '))

  component_file_path = os.path.join(ROOT_PATH, 'component.json')
  f = open(component_file_path, 'w')
  f.write(txt)
  f.close()


def generate_composer_json(data):
  print "Generate composer.json"
  d = {
    "name": "softsupply/font-gansoft",
    "description": "The GanSoft iconic font and CSS framework",
    "keywords": ["font", "gansoft", "fontgansoft", "icon", "font", "bootstrap"],
    "homepage": "https://www.softsupply.com/",
    "authors": [
      {
        "name": "Enner Perez",
        "email": "ennerperez@gmail.com",
        "role": "Developer",
        "homepage": "http://www.ennerperez.com.ve/"
      }
    ],
    "extra": {},
    "license": [ "MIT" ]
  }
  txt = json.dumps(d, indent=4, separators=(',', ': '))

  composer_file_path = os.path.join(ROOT_PATH, 'composer.json')
  f = open(composer_file_path, 'w')
  f.write(txt)
  f.close()


def generate_bower_json(data):
  print "Generate bower.json"
  d = {
    "name": data['name'],
    "version": data['version'],
    "homepage": "https://github.com/softsupply/font-gansoft",
    "authors": [
      "Enner Perez <ennerperez@gmail.com>"
    ],
    "description": "The GanSoft iconic font and CSS framework",
    "main": [
      "css/*",
      "fonts/*"
    ],
    "keywords": ["font", "gansoft", "fontgansoft", "icon", "font", "bootstrap"],
    "license": "MIT",
    "ignore": [
      "**/.*",
      "builder",
      "node_modules",
      "bower_components",
      "test",
      "tests"
    ]
  }
  txt = json.dumps(d, indent=4, separators=(',', ': '))

  bower_file_path = os.path.join(ROOT_PATH, 'bower.json')
  f = open(bower_file_path, 'w')
  f.write(txt)
  f.close()


def get_build_data():
  build_data_path = os.path.join(BUILDER_PATH, 'manifest.json')
  f = open(build_data_path, 'r')
  data = json.loads(f.read())
  f.close()
  return data


if __name__ == "__main__":
  main()
