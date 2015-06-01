# Installation {: .doctitle}
Installation of PyMdown.

---

## Overview
PyMdown can be downloaded and installed via `python setup.py build` and `python setup.py install`,after which a command line utility (pymdown) will be made available.  You can also use [Pyinstaller][pyinstaller] to build a binary as well; the procedure for this is outlined [below](#build).  You can also just run it directly if you have the necessary [requirements](#requirements) installed.

## Requirements
In order for PyMdown to work, there are a couple of prerequisites.  If installing via the `python setup.py install` method, required dependencies should get installed automatically.


| Name | Required |Details |
|------|----------|--------|
| [Python Markdown 2.6.0+][py_md] | Yes |Python Markdown must be installed as it is the Markdown parser that is being used. |
| [PyMdown Extensions](https://github.com/facelessuser/pymdown-extensions) | Yes | Extensions for PyMdown. |
| [PyYaml 3.10+][pyyaml] | Yes | Older versions may work, but I am arbitrarily specifying 3.10 as the earliest I am aware of that works. |
| [Pygments 2.0.1+ (optional)][pygments] | No | If Pygments Syntax highlighting is desired, Pygments must be installed.  This can be omitted, and code blocks (if using the CodeHilite extension) will be formatter for use with JavaScript code highlighters. |
| [PyMdown Styles](https://github.com/facelessuser/pymdown-styles) | No | Optional package that adds a couple of custom Pygments styles. This is not required, but is a great example if you want to create your own style package. |
| [PyMdown Lexers](https://github.com/facelessuser/pymdown-lexers) | No | Optional package that adds a couple of non-standard lexers, but nothing of substantial interest. This is a great example for adding your own custom lexers. |

## Installation
You can download PyMdown and run it as a script bundle, or build and copy the binary in your path.  To install the traditional way, run `python setup.py build` and `python setup.py install`.  You should be able to access PyMdown from the command line via `pymdown` or `pymdownX.X` where `X.X` is your python version.  PyMdown on the first run will unpack user files to `~\.PyMdown` on Windows, `~/.PyMdown` on OSX and `~/.config/PyMdown` on Linux.

## Build
If building, you will need to download the latest PyInstaller from [Github](https://github.com/pyinstaller/pyinstaller).  Just unzip the content into the root of the PyMdown project and ensure the main folder is named `pyinstaller`.  Then, from PyMdown's root directory, run `python build -c`.  The binary should be created in the `dist` folder.  This is regularly tested on Windows 7 and OSX 10.10.  Linux may require some playing around if it doesn't work out of the box.

!!! note "Note"
    In the future, I do plan on allowing this run from an installed Pyinstaller opposed to a version copied into the project, but currently I don't support it mainly because on Windows I build with a portable Python (WinPython), and I haven't spent any time yet to get it running proper without having it copied in the project.

[py_md]: https://pythonhosted.org/Markdown/
[pygments]: http://pygments.org/
[pyinstaller]: http://www.pyinstaller.org/
[pyyaml]: http://pyyaml.org/
