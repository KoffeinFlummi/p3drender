#!/usr/bin/python3

def build_render_script(target, options):
    template = """
import bpy
import mathutils
import bmesh
import math
import functools

nan = 0.0 #don't ask...

{}

def create_material(path):
    mat = bpy.data.materials.new("blub")
    mat.roughness = 0.8
    mat.specular_intensity = 0.02

    mat.use_nodes = True
    tex = mat.node_tree.nodes.new('ShaderNodeTexImage')
    try:
        tex.image = bpy.data.images.load(path)
    except Exception as e:
        print(e)
        pass

    bsdf = mat.node_tree.nodes["Principled BSDF"]
    mat.node_tree.links.new(bsdf.inputs['Base Color'], tex.outputs['Color'])

    return mat

def create_mesh(verts, faces, uvs, normals, sharp_edges):
    me = bpy.data.meshes.new("P3DMesh")
    ob = bpy.data.objects.new("P3D", me)
    ob.show_name = True

    scn = bpy.context.scene
    scn.collection.objects.link(ob)

    me.from_pydata(verts, [], faces)
    me.update()

    for f in me.polygons:
        f.use_smooth = True

    for e in me.edges:
        vi = tuple(e.vertices)
        e.use_edge_sharp = vi in sharp_edges or vi[::-1] in sharp_edges
    ob.modifiers.new(name="Edge Split", type="EDGE_SPLIT")

    bm = bmesh.new()
    bm.from_mesh(me)

    uv_layer = bm.loops.layers.uv.verify()

    for f, uvs in zip(bm.faces, UVS):
        for l, uv in zip(f.loops, uvs):
            l[uv_layer].uv = (uv[0], 1 - uv[1])

    bm.to_mesh(me)
    bm.free()

    return ob

def main():
    bpy.data.objects.remove(bpy.data.objects["Cube"], do_unlink=True)
    bpy.data.objects.remove(bpy.data.objects["Light"], do_unlink=True)

    ob = create_mesh(VERTS, FACES, UVS, NORMALS, SHARP_EDGES)
    me = ob.data

    # Transform object
    ROTATION[0] += 90
    ob.rotation_euler = [math.radians(r % 360) for r in ROTATION]

    bbox_center = 0.125 * sum((mathutils.Vector(b) for b in ob.bound_box), mathutils.Vector())
    x,y,z = bbox_center
    bbox_center = mathutils.Vector((x,z,y))

    ob.location = mathutils.Vector(TRANSLATION)
    if not NOCENTER:
        ob.location -= bbox_center

    # Apply materials
    materials = [create_material(x) for x in TEXTURES]

    for m in materials:
        me.materials.append(m)

    for f, i in zip(me.polygons, MATI):
        f.material_index = i

    # Prepare scene
    lamp_data = bpy.data.lights.new(name="New Lamp", type="SUN")
    lamp_data.energy = 5
    lamp_object = bpy.data.objects.new(name="New Lamp", object_data=lamp_data)
    bpy.context.scene.collection.objects.link(lamp_object)

    # Prepare camera
    camera = bpy.context.scene.camera
    camera.location = CAMERA_LOCATION
    if CAMERA_ORTHO:
        bpy.data.cameras["Camera"].type = "ORTHO"

    camera.rotation_euler = (math.radians(90) + CAMERA_PITCH, 0, -CAMERA_YAW)

    bpy.context.scene.render.film_transparent = True
    bpy.context.scene.render.image_settings.color_mode = 'RGBA'
    bpy.context.scene.render.resolution_x = RESOLUTION[0]
    bpy.context.scene.render.resolution_y = RESOLUTION[1]
    bpy.context.scene.render.resolution_percentage = 100
    bpy.context.scene.render.filepath = "{}"
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
"""

    return template.format("\n".join(["{} = {}".format(k, str(v)) for k,v in options.items()]), target)
