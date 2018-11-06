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

def create_texture(texturepath):
    tex = bpy.data.textures.new(texturepath, type = 'IMAGE')
    try:
        tex.image = bpy.data.images.load(texturepath)
    except:
        pass
    return tex

def create_material(texture):
    mat = bpy.data.materials.new("blub")
    mat.specular_hardness = 200
    mat.specular_intensity = 0.02

    mtex = mat.texture_slots.add()
    mtex.texture = texture
    mtex.texture_coords = 'UV'
    mtex.use_map_color_diffuse = True
    mtex.use_map_color_emission = True
    mtex.emission_color_factor = 0.5
    mtex.use_map_density = True
    mtex.mapping = 'FLAT'
    return mat

def create_mesh(verts, faces, uvs, normals, sharp_edges):
    me = bpy.data.meshes.new("P3DMesh")
    ob = bpy.data.objects.new("P3D", me)
    ob.show_name = True

    scn = bpy.context.scene
    scn.objects.link(ob)
    scn.objects.active = ob
    ob.select = True

    me.from_pydata(verts, [], faces)
    me.update()

    #me.normals_split_custom_set(functools.reduce(lambda x,y: x+y, normals))
    #me.use_auto_smooth = True

    for f in me.polygons:
        f.use_smooth = True

    for e in me.edges:
        vi = tuple(e.vertices)
        e.use_edge_sharp = vi in sharp_edges or vi[::-1] in sharp_edges
    ob.modifiers.new(name="Edge Split", type="EDGE_SPLIT")

    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(me)

    uv_layer = bm.loops.layers.uv.verify()
    bm.faces.layers.tex.verify()

    for f, uvs in zip(bm.faces, UVS):
        for l, uv in zip(f.loops, uvs):
            l[uv_layer].uv = (uv[0], 1 - uv[1])

    bmesh.update_edit_mesh(me)
    bpy.ops.object.mode_set(mode='OBJECT')

    return ob

def main():
    bpy.data.objects.remove(bpy.data.objects["Cube"], True)
    bpy.data.objects.remove(bpy.data.objects["Lamp"], True)

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
    textures = [create_texture(x) for x in TEXTURES]
    materials = [create_material(x) for x in textures]

    for m in materials:
        me.materials.append(m)

    for f, i in zip(me.polygons, MATI):
        f.material_index = i

    # Prepare scene
    lamp_data = bpy.data.lamps.new(name="New Lamp", type="HEMI")
    lamp_data.energy = 5
    lamp_object = bpy.data.objects.new(name="New Lamp", object_data=lamp_data)
    bpy.context.scene.objects.link(lamp_object)

    lamp_object.select = True
    bpy.context.scene.objects.active = lamp_object

    # Prepare camera
    camera = bpy.context.scene.camera
    camera.location = CAMERA_LOCATION
    if CAMERA_ORTHO:
        bpy.data.cameras["Camera"].type = "ORTHO"

    camera.rotation_euler = (math.radians(90) + CAMERA_PITCH, 0, -CAMERA_YAW)


    bpy.context.scene.render.alpha_mode = "TRANSPARENT"
    bpy.context.scene.render.resolution_x = RESOLUTION[0]
    bpy.context.scene.render.resolution_y = RESOLUTION[1]
    bpy.context.scene.render.resolution_percentage = 100
    bpy.context.scene.render.filepath = "{}"
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
"""

    return template.format("\n".join(["{} = {}".format(k, str(v)) for k,v in options.items()]), target)
