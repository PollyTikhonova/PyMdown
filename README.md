# Mdown
Mdown is CLI tool to convert or even batch convert markdown files to HTML. It can also accept a file stream.  It was inspired by https://github.com/revolunet/sublimetext-markdown-preview.

# Status
This is in an **Beta** state.  Because of the **Beta** state, things are in flux and are subject to change without warning.

# Features
- Python 2 and 3 compatible (but executables built with Python 2 using Pyinstaller)
- Should run on OSX, Windows, and Linux
- Receive multiple files or file patterns to process
- Receive input file stream for conversion
- Configurable options file to tweak Python's Markdown package behavior
- Uses Pygments for syntax highighlighting
- Repo includes in `extras` a simple Sublime Text plugin to stream your files to mdown
- Preview option to open output in a browser intead
- Optionally all the default Markdown extensions, plus these optional mdownx extensions:
    - **absolutepath**: Converts local file paths from relative to absolute for things like links, images, etc.  This is automatically done on all previews.  It can be configured to run all the time outside of previews in the settings file, and it can take a hardcoded path `absolutepath(base_path=/my/path)` or a dynamic path `absolutepath(base_path=${BASE_PATH})` that can take the base_path fed in on the command line or calculated from the source files path.  If you set this in the settings file, keep in mind the settings file overrides preview's settings.
    - **b64**: Base64 encode local image files. If can be enabled and configured in the settings file and can take a hardcoded path `b64(base_path=/my/path)` or it can take a dynamic base_path `b64(base_path=${BASE_PATH})` fed in on the command line or calculated from the source files path.
    - **insert**: Add <ins>test</ins> tags by using `^^test^^`. Can be enabled in the settings file.
    - **delete**: Add <del>test</del> tags by using `~~test~~`. Can be enabled in the settings file.
    - **magiclink**: Search for and convert http or ftp links to actual HTML links for lazy link creation. Can be enabled in the settings file.
    - **tasklist**: This adds support for github style tasklists.  Can be enabled in the settings.
    - **githubemoji**: This adds emojis.  Assets link to github's emoji icons.  Can be enabled in the settings.
    - **critic**: Cannot be set in the settings file. It is configured automatically, and its behaviour can only be modifid via the command line.  In its current form, it can output in HTML a highlighted critic form to make it more readable.  If you select `--accept` or `--reject`, it will strip out the critic marks by accepting the changes or discarding them.
    - **headeranchor**: Insert github style header anchor on left side of h1-h6 tags.
    - **progressbar**: Support for adding progress bars.
    - **mdownx**: currently loads insert, delete, b64, tasklist, githubemoji, and magiclink.
    - **github**: Adds a number of the above mentioned extensions to give a Github Flavored Markdown feel.

# Styles and Configuration

## Syntax Highlighting with Pygments
Syntax highlighting can be done in fenced blocks when enabling the `codehilite` extension.  Its styles etc. can be configured in the settings file as well. Here is an example:

```javascript
    "extensions": [
        "extra",
        "toc",
        "codehilite(guess_lang=False,pygments_style=tomorrownighteighties)"
    ]
```

Notice the syntax style is set with the `pygments_style` key.

# Add More CSS and JS Files
Add them to the provided settings:

```javascript
    // Select your CSS for you output html
    // or you can have it all contained in your HTML template
    //
    // Can be an array of stylesheets or "default"
    // "default" can also be an entry in the array.
    // If it points to a physical file, it will be included.
    "css_style_sheets": ["default"],

    // Load up js scripts
    //
    // Can be an array of scripts.
    // If it points to a physical file, it will be included.
    "js_scripts": [],
```

## Change the HTML Template
This can be done here:

```javascript
    // Your HTML template
    "html_template": "default",
```

# Command Line

```
usage: mdown [-h] [--version] [--licenses] [--quiet] [--preview]
             [--plain-html] [--title TITLE] [--accept | --reject]
             [--critic-dump] [--no-critic] [--output OUTPUT] [--batch]
             [--settings SETTINGS] [--encoding ENCODING] [--basepath BASEPATH]
             [markdown [markdown ...]]

Markdown generator

positional arguments:
  markdown              Markdown file(s) or file pattern(s).

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --licenses            Display licenses.
  --quiet, -q           No messages on stdout.
  --preview, -p         Output to preview (temp file). --output will be
                        ignored.
  --plain-html, -P      Strip out CSS, style, ids, etc. Just show tags.
  --title TITLE         Title for HTML.
  --accept, -a          Accept propossed critic marks when using in normal
                        processing and --critic-dump processing
  --reject, -r          Reject propossed critic marks when using in normal
                        processing and --critic-dump processing
  --critic-dump         Process critic marks, dumps file(s), and exits.
  --no-critic           Turn off critic feature completely
  --output OUTPUT, -o OUTPUT
                        Output file. Ignored in batch mode.
  --batch, -b           Batch mode output.
  --settings SETTINGS, -s SETTINGS
                        Load the settings file from an alternate location.
  --encoding ENCODING, -e ENCODING
                        Encoding for input.
  --basepath BASEPATH   The basepath location mdown should use.
```

# Sublime Plugin
Generally I recommend https://github.com/revolunet/sublimetext-markdown-preview.  But I wrote this program and this sublime plugin to gain certain control I didn't already have.  If for whatever reason you want to use this plugin, this is how you set it up.

Just drop the extra folder in your Sublime `Packages` folder and name to something sane like `mdown`.  It currently provides only 4 commands that are accessible from the command palette:

```javascript
    //////////////////////////////////
    // Mdown
    //////////////////////////////////

    // Preview the current mardown view in your browser
    {
        "caption": "Mdown: Preview Markdown",
        "command": "mdown_preview"
    },

    // Preview the current markdown source in a special
    // mode that highlights critc syntax in a easier to
    // read way.
    {
        "caption": "Mdown: Preview Critic",
        "command": "mdown_critic_preview"
    },

    // Strip out critic markup in your current view
    // favoring the suggested changes
    {
        "caption": "Mdown: Critic Strip Markdown (accept)",
        "command": "mdown_critic_strip"
    },

    // Strip out the critic markup in your current view
    // rejecting the suggested changes
    {
        "caption": "Mdown: Critic Strip Markdown (reject)",
        "command": "mdown_critic_strip",
        "args": {"reject": true}
    }
```


# Credits
- Uses a slightly modified https://pypi.python.org/pypi/Markdown
- Uses the development branch of Pygments for Python 3 supporthttp://pygments.org/
- Borrowed and modified default CSS file from https://github.com/revolunet/sublimetext-markdown-preview.  Also, the original inspiration for this project.
- Includes Tomorrow Themes for Pygment from https://github.com/MozMorris/tomorrow-pygments

# Build
- Download or clone Pyinstaller main branch (latest release won't work; the dev branch is needed) from github into the mdown project folder https://github.com/pyinstaller/pyinstaller
- Using Python 2 run `python build.py -c`
- Binary will be in the `mdown/dist` folder

# TODO
- [ ] Maybe add some builtin syntax for critic, mark, and kbd tags.  It isn't decided how many of these I will or will not add.  Support would be added via an extension.
- [ ] Maybe add an extension for embedding content
- ...stuff I havn't yet thought of...

# License
MIT license.

Copyright (c) 2014 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

#3rd Party Licenses

## Markdown
Copyright 2007, 2008 The Python Markdown Project (v. 1.7 and later)
Copyright 2004, 2005, 2006 Yuri Takhteyev (v. 0.2-1.6b)
Copyright 2004 Manfred Stienstra (the original version)

All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

*   Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.
*   Redistributions in binary form must reproduce the above copyright
    notice, this list of conditions and the following disclaimer in the
    documentation and/or other materials provided with the distribution.
*   Neither the name of the <organization> nor the
    names of its contributors may be used to endorse or promote products
    derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE PYTHON MARKDOWN PROJECT ''AS IS'' AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL ANY CONTRIBUTORS TO THE PYTHON MARKDOWN PROJECT
BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.

# Pygments
Copyright (c) 2006-2013 by the respective authors (see AUTHORS file).
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

* Redistributions of source code must retain the above copyright
  notice, this list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright
  notice, this list of conditions and the following disclaimer in the
  documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Markdown Preview
The MIT License (MIT)
Copyright © 2014 Julien Bouquillon, revolunet <julien@revolunet.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
