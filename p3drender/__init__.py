#!/usr/bin/env python3

"""p3drender

A script for rendering P3D files

https://github.com/KoffeinFlummi/p3drender
"""


import os
import math
import tempfile
import subprocess

import py3d

from .renderscript import build_render_script

def is_windows():
    return os.name == 'nt'

def get_tempfile(suffix):
    while True:
        filename = "{}{}".format(next(tempfile._get_candidate_names()), suffix)
        name = os.path.join(tempfile.gettempdir(), filename)
        if not os.path.exists(name):
            return name

def path_platform(path):
    if is_windows():
        return path

    return path.replace("\\", "/")

def path_insensitive(path):
    return _path_insensitive(path) or path


def _path_insensitive(path):
    if path == '' or os.path.exists(path):
        return path

    base = os.path.basename(path)
    dirname = os.path.dirname(path)

    suffix = ''
    if not base:
        if len(dirname) < len(path):
            suffix = path[:len(path) - len(dirname)]
        base = os.path.basename(dirname)
        dirname = os.path.dirname(dirname)

    if not os.path.exists(dirname):
        dirname = _path_insensitive(dirname)
        if not dirname:
            return

    try:
        files = os.listdir(dirname)
    except OSError:
        return

    baselow = base.lower()
    try:
        basefinal = next(fl for fl in files if fl.lower() == baselow)
    except StopIteration:
        return

    if basefinal:
        return os.path.join(dirname, basefinal) + suffix
    else:
        return

def find_file(p3dfile, path):
    path = path_platform(path)
    p3dfile = os.path.dirname(os.path.abspath(p3dfile))

    while os.sep in p3dfile[1:]:
        if "$PBOPREFIX$" in os.listdir(p3dfile):
            with open(os.path.join(p3dfile, "$PBOPREFIX$")) as f:
                prefix = f.read().strip()
            prefix = path_platform(prefix)
            if prefix == path[:len(prefix)]:
                return path_insensitive(os.path.join(p3dfile, path[len(prefix)+1:]))
        if os.path.exists(path_insensitive(os.path.join(p3dfile, path))):
            return path_insensitive(os.path.join(p3dfile, path))
        p3dfile = os.path.dirname(p3dfile)

    raise FileNotFoundError("Failed to find {}".format(path))


def convert_texture(p3dfile, paa, args):
    if paa == "" or paa[0] == "#":
        return ""

    path = find_file(p3dfile, paa)
    result = get_tempfile(".png")
    if args["--converter"] == "imagetopaa":
        subprocess.call(["imagetopaa", path, result])
    else:
        subprocess.call(["armake", "paa2img", path, result])
    return result

def render(p3dfile, outfile, args):
    print("Loading P3D ...")
    with open(p3dfile, "rb") as f:
        p3d = py3d.P3D(f)

    lod = p3d.lods[0]

    # Remove proxies
    for k,v in lod.selections.items():
        if "proxy:" not in k:
            continue
        for p,w in v.points.items():
            if w == 0:
                continue
            p.coords = (0,0,0)

    textures = list(set([x.texture for x in lod.faces]))
    points = [x.coords for x in lod.points]
    faces = [tuple(y.point_index for y in x.vertices) for x in lod.faces]
    normals = [tuple(y.normal.coords for y in x.vertices) for x in lod.faces]
    uvs = [tuple(y.uv for y in x.vertices) for x in lod.faces]
    mati = [textures.index(x.texture) for x in lod.faces]

    print("Converting textures ...")
    textures = [convert_texture(p3dfile, x, args) for x in textures]

    distance = float(args["--distance"]) * -1
    pitch = math.radians(float(args["--pitch"]))
    yaw = math.radians(float(args["--yaw"]))

    camera_location = (math.sin(yaw) * math.cos(pitch), math.cos(yaw) * math.cos(pitch), math.sin(pitch))
    camera_location = tuple(x * distance for x in camera_location)

    print("Building script ...")
    script = build_render_script(outfile, {
            "TEXTURES": textures,
            "VERTS": points,
            "FACES": faces,
            "NORMALS": normals,
            "SHARP_EDGES": lod.sharp_edges,
            "UVS": uvs,
            "MATI": mati,
            "CAMERA_LOCATION": camera_location,
            "CAMERA_YAW": yaw,
            "CAMERA_PITCH": pitch,
            "TRANSLATION": tuple(float(x) for x in args["--translate"].split(",")),
            "CAMERA_ORTHO": args["--orthographic"],
            "RESOLUTION": tuple(int(x) for x in args["--resolution"].split(","))
        })

    scriptfile = get_tempfile(".py")
    with open(scriptfile, "w") as f:
        f.write(script)

    print("Running Blender ...")
    if args["--gui"]:
        subprocess.call(["blender", "-P", scriptfile])
    else:
        subprocess.call(["blender", "-b", "-P", scriptfile])

    os.remove(scriptfile)
    for t in textures:
        if t == "" or t[0] == "#":
            continue
        os.remove(t)

def run(args):
    render(args["<p3dfile>"], args["<outfile>"], args)
    return 0
