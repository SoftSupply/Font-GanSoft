# Font-GanSoft

![logo](.editoricon.png)

## The GanSoft iconic font and CSS framework

---------------------------------------

See the [changelog](CHANGELOG.md) for changes.

We intend for this icon pack to be used with [GanSoft](https://www.softsupply.com/), but it’s by no means limited to it. Use them wherever you see fit, personal or commercial. They are free to use and licensed under [MIT](http://opensource.org/licenses/MIT).

## Table of contents

* [Installation](#installation)
* [Versioning](#versioning)
* [Implementing](#implementing)
* [Bugs and feature requests](#bugs-and-feature-requests)
* [Documentation](#documentation)
* [License](#license)

### Installation

Requires **Ruby 1.9.3+**, **WOFF2**, **FontForge** with Python scripting.

#### On Mac

```sh
brew tap bramstein/webfonttools
brew update
brew install woff2

brew install fontforge --with-python
brew install eot-utils
gem install fontcustom
```

#### On Linux

```sh
sudo apt-get install zlib1g-dev fontforge
git clone https://github.com/bramstein/sfnt2woff-zopfli.git sfnt2woff-zopfli && cd sfnt2woff-zopfli && make && mv sfnt2woff-zopfli /usr/local/bin/sfnt2woff
git clone --recursive https://github.com/google/woff2.git && cd woff2 && make clean all && sudo mv woff2_compress /usr/local/bin/ && sudo mv woff2_decompress /usr/local/bin/
gem install fontcustom
```

#### On Windows

```cmd
1. Install fontforge:  http://fontforge.github.io/en-US/downloads/windows-dl/
2. Add the installation path to your System PATH variable (%programfiles(x86)%\FontForgeBuilds\bin)
3. Open up a new command prompt and test it. `fontforge -help`
4. gem install fontcustom
```

### Versioning

Font GanSoft will be maintained under the Semantic Versioning guidelines as much as possible. Releases will be numbered with the following format:

`<major>.<minor>.<patch>`

Edit [manifest.json](builder\manifest.json)

And constructed with the following guidelines:

* Breaking backward compatibility bumps the major (and resets the minor and patch)
* New additions, including new icons, without breaking backward compatibility bumps the minor (and resets the patch)
* Bug fixes, changes to brand logos, and misc changes bumps the patch

For more information on SemVer, please visit [http://semver.org](http://semver.org).

### Building

    $python .\builder\generate.py

### Implementing

#### Add the library to your project

    $bower install font-gansoft --save

### Bugs and feature requests

Have a bug or a feature request? Please first search for existing and closed issues. If your problem or idea is not addressed yet, [please open a new issue](issues/new).

### Documentation

No more documentation required for now.

### License

Code released under [The MIT License](LICENSE)