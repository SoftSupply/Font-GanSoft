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
  template_path = os.path.join(BUILDER_PATH, 'templates', 'cheatsheet.html')
  icon_row_path = os.path.join(BUILDER_PATH, 'templates', '_icon-row.html')

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

def generate_composer_json(data):
  print "Generate composer.json"

  composer_template_path = os.path.join(BUILDER_PATH, 'templates', 'composer.json')

  f = open(composer_template_path, 'r')
  template_composer = f.read()
  f.close()

  template_composer = template_composer.replace("{{name}}", data["name"].lower())
  template_composer = template_composer.replace("{{repo}}", data["repo"].lower())
  template_composer = template_composer.replace("{{version}}", data["version"])
  template_composer = template_composer.replace("{{repo}}", data["repo"].lower())
  template_composer = template_composer.replace("{{license}}", ", ".join(data["license"]))
  template_composer = template_composer.replace("{{keywords}}", ", ".join(data["keywords"]))
  template_composer = template_composer.replace("{{homepage}}", data["homepage"])
  template_composer = template_composer.replace("{{description}}", data["description"])

  composer_file_path = os.path.join(ROOT_PATH, 'composer.json')
  f = open(composer_file_path, 'w')
  f.write(template_composer)
  f.close()


def generate_bower_json(data):
  print "Generate bower.json"

  bower_template_path = os.path.join(BUILDER_PATH, 'templates', 'bower.json')

  f = open(bower_template_path, 'r')
  template_bower = f.read()
  f.close()

  template_bower = template_bower.replace("{{name}}", data["name"].lower())
  template_bower = template_bower.replace("{{repo}}", data["repo"].lower())
  template_bower = template_bower.replace("{{version}}", data["version"])
  template_bower = template_bower.replace("{{license}}", ", ".join(data["license"]))
  template_bower = template_bower.replace("{{keywords}}", ", ".join(data["keywords"]))
  template_bower = template_bower.replace("{{homepage}}", data["homepage"])
  template_bower = template_bower.replace("{{description}}", data["description"])

  bower_file_path = os.path.join(ROOT_PATH, 'bower.json')
  f = open(bower_file_path, 'w')
  f.write(template_bower)
  f.close()


def get_build_data():
  build_data_path = os.path.join(BUILDER_PATH, 'manifest.json')
  f = open(build_data_path, 'r')
  data = json.loads(f.read())
  f.close()
  return data


if __name__ == "__main__":
  main()
