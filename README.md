p3drender
=========

A script for rendering P3D files (unbinarized) directly using [armake](https://github.com/KoffeinFlummi/armake) for PAA conversion, [py3d](https://github.com/KoffeinFlummi/py3d) for model loading and Blender for rendering. Includes presets for various types of inventory icons.


## Installation

```bash
# python3 setup.py install
```


## Usage

```
p3drender

Usage:
    p3drender [options] <p3dfile> <outfile>
    p3drender (-h | --help)
    p3drender (-v | --version)

Options:
    -p, --preset <preset>   Use a preset for rendering. Options are:
                                weapon (orthographic side view, 1024x512)
                                item (front-left perspective, 512x512) 
                                (Overwrites other options)
    -c, --camera <xyz>      Camera position in form x,y,z [default: 0,-5,0]
    -r, --resolution <res>  Output resolution in form x,y [default: 512,512]
    -t, --translate <xyz>   Translation to apply to object [default: 0,0,0]
    -o, --orthographic      Set camera to orthographic instead of perspective
    -g, --gui               Don't run Blender in background mode, so you can
                                make manual adjustments.
    -h, --help              Show usage information and exit.
    -v, --version           Print the version number and exit.
```

At the moment the defaults aren't really usable yet, so at the moment you'll usually want to use the -g flag.
