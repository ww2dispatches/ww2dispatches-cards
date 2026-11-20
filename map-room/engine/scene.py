"""The Map Room: film quality table, rendered piece by piece (the compositor slides them).
Modes: plate, platepad, block, mask, rake, rakemask, cam, campad.
  python3 scene.py <mode> '<json>' <RX> <RY> <samples> <out.png>
  block/mask json: {"face": "face.png", "x": table x, "y": table y, "rot": degrees}
  rake/rakemask json: {"angle": degrees the pole points (0 = east, 90 = north), "x": head x, "y": head y}
Env: MAPROOM_MAP, the view's map image (plate modes and every sprite, which carry the table for their shadows).
Sprites render on the padded frame (room past every edge, same pixel scale); the rake gets more room for its long pole.
platepad is the shadow base for every sprite."""
import bpy, bmesh, math, sys, json, os
from mathutils import Vector, Matrix
a = sys.argv[1:]
MODE = a[0]; ARG = json.loads(a[1]) if len(a) > 1 and a[1].startswith('{') else {}
RX, RY = int(a[2]) if len(a) > 2 else 1080, int(a[3]) if len(a) > 3 else 1920
SMP = int(a[4]) if len(a) > 4 else 128
OUT = a[5] if len(a) > 5 else 'out.png'
MAP = os.environ.get('MAPROOM_MAP', 'map.png')
PADX, PADY = (1000, 1000) if MODE in ('rake', 'rakemask') else (270, 240)   # comp reads PADX/PADY from the render size
PADDED = MODE in ('platepad', 'block', 'mask', 'rake', 'rakemask', 'campad')
if MODE == 'campad': PADX, PADY = 270, 240
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; col = sc.collection
def link(o): col.objects.link(o); return o
def mesh_obj(name, verts, faces):
    m = bpy.data.meshes.new(name); m.from_pydata(verts, [], faces); m.update(); return link(bpy.data.objects.new(name, m))
def smooth(o):
    for p in o.data.polygons: p.use_smooth = True
def bevel(o, w=0.015, seg=3):
    b = o.modifiers.new('bev', 'BEVEL'); b.width = w; b.segments = seg; b.limit_method = 'ANGLE'; b.angle_limit = math.radians(40)
    smooth(o); o.modifiers.new('wn', 'WEIGHTED_NORMAL')
def lathe(name, prof, seg=48):
    verts, faces = [], []
    for r, z in prof:
        for i in range(seg): t = 2 * math.pi * i / seg; verts.append((r * math.cos(t), r * math.sin(t), z))
    n = len(prof)
    for j in range(n - 1):
        for i in range(seg):
            p = j * seg + i; q = j * seg + (i + 1) % seg; faces.append((p, q, q + seg, p + seg))
    faces.append(tuple(reversed(range(seg)))); faces.append(tuple(range((n - 1) * seg, n * seg)))
    o = mesh_obj(name, verts, faces); smooth(o); return o
def box(name, sx, sy, sz, loc):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts: v.co = Vector((v.co.x * sx, v.co.y * sy, (v.co.z + 0.5) * sz))
    m = bpy.data.meshes.new(name); bm.to_mesh(m); bm.free(); o = link(bpy.data.objects.new(name, m)); o.location = loc; return o
def cyl(name, r, h, seg=32): return lathe(name, [(r, 0), (r, h)], seg)
def principled(name):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; return m, nt, nt.nodes['Principled BSDF']
def wood(name, c1, c2, scale=1.0, rough=0.32, coat=0.55):
    m, nt, p = principled(name); N = nt.nodes; L = nt.links
    tc = N.new('ShaderNodeTexCoord'); mp = N.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (9 * scale, 0.5 * scale, 4 * scale); mp.inputs['Rotation'].default_value = (0.05, 0.03, 0.12)
    wv = N.new('ShaderNodeTexWave'); wv.wave_type = 'BANDS'; wv.inputs['Scale'].default_value = 1.6; wv.inputs['Distortion'].default_value = 2.2; wv.inputs['Detail'].default_value = 3; wv.inputs['Detail Scale'].default_value = 1.6
    fine = N.new('ShaderNodeTexNoise'); fine.inputs['Scale'].default_value = 60; fine.inputs['Detail'].default_value = 3
    mpf = N.new('ShaderNodeMapping'); mpf.inputs['Scale'].default_value = (0.25 * scale, 14 * scale, 14 * scale)
    ramp = N.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].color = c1 + (1,); ramp.color_ramp.elements[1].color = c2 + (1,); ramp.color_ramp.elements[0].position = 0.25; ramp.color_ramp.elements[1].position = 0.8
    mixf = N.new('ShaderNodeMix'); mixf.data_type = 'RGBA'; mixf.blend_type = 'MULTIPLY'; mixf.inputs[0].default_value = 0.14
    L.new(tc.outputs['Object'], mp.inputs['Vector']); L.new(mp.outputs['Vector'], wv.inputs['Vector']); L.new(wv.outputs['Fac'], ramp.inputs['Fac'])
    L.new(tc.outputs['Object'], mpf.inputs['Vector']); L.new(mpf.outputs['Vector'], fine.inputs['Vector'])
    L.new(ramp.outputs['Color'], mixf.inputs[6]); L.new(fine.outputs['Color'], mixf.inputs[7]); L.new(mixf.outputs[2], p.inputs['Base Color'])
    bp = N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.03; L.new(wv.outputs['Fac'], bp.inputs['Height']); L.new(bp.outputs['Normal'], p.inputs['Normal'])
    p.inputs['Roughness'].default_value = rough; p.inputs['Coat Weight'].default_value = coat; p.inputs['Coat Roughness'].default_value = 0.12
    return m
def flat(name, c, rough=0.5, metal=0.0):
    m, nt, p = principled(name); p.inputs['Base Color'].default_value = c + (1,); p.inputs['Roughness'].default_value = rough; p.inputs['Metallic'].default_value = metal; return m
def img_mat(path, rough=0.62, coat=0.04):
    m, nt, p = principled('img'); t = nt.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(path); t.interpolation = 'Cubic'
    nt.links.new(t.outputs['Color'], p.inputs['Base Color']); p.inputs['Roughness'].default_value = rough; p.inputs['Coat Weight'].default_value = coat; return m
M = {'walnut': wood('walnut', (0.12, 0.062, 0.03), (0.07, 0.036, 0.018)), 'maple': wood('maple', (0.80, 0.63, 0.42), (0.62, 0.45, 0.27)),
     'rim': wood('rim', (0.11, 0.055, 0.028), (0.06, 0.03, 0.015), 0.5), 'brass': flat('brass', (0.83, 0.62, 0.25), 0.28, 1.0),
     'floor': flat('floor', (0.02, 0.018, 0.015), 0.9)}
def mat(o, m): o.data.materials.append(M[m] if isinstance(m, str) else m); return o
def group(name, loc, parts, rotz=0):
    e = link(bpy.data.objects.new(name, None)); e.location = loc; e.rotation_euler = (0, 0, rotz)
    for p in parts: p.parent = e
    return e
def face_plane(name, w, h, img):
    m = bpy.data.meshes.new(name); m.from_pydata([(-w / 2, -h / 2, 0), (w / 2, -h / 2, 0), (w / 2, h / 2, 0), (-w / 2, h / 2, 0)], [], [(0, 1, 2, 3)])
    uv = m.uv_layers.new()
    for i, c in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]): uv.data[i].uv = c
    o = link(bpy.data.objects.new(name, m)); o.data.materials.append(img_mat(img)); return o

# ---------- table ----------
TW, TH = 14.0, 14.4
mp = face_plane('map', TW, TH, MAP)
mm = mp.data.materials[0]; p = mm.node_tree.nodes['Principled BSDF']; p.inputs['Roughness'].default_value = 0.3; p.inputs['Coat Weight'].default_value = 1.0; p.inputs['Coat Roughness'].default_value = 0.04
TABLE = [mp]
for nm, sx, sy, loc in [('rimN', TW + 1.2, 0.6, (0, TH / 2 + 0.3, -0.25)), ('rimS', TW + 1.2, 0.6, (0, -TH / 2 - 0.3, -0.25)),
                        ('rimE', 0.6, TH, (TW / 2 + 0.3, 0, -0.25)), ('rimW', 0.6, TH, (-TW / 2 - 0.3, 0, -0.25))]:
    r = box(nm, sx, sy, 0.38, loc); bevel(r, 0.05, 4); mat(r, 'rim'); TABLE.append(r)
fl = box('floor', 80, 80, 0.1, (0, 0, -3.5)); mat(fl, 'floor'); TABLE.append(fl)

# ---------- pieces ----------
BS = float(os.environ.get("MAPROOM_BS", 1.35))   # as day.py
def make_block(face, loc, rot):
    b = box('blk', BS, BS, 0.36, (0, 0, 0)); bevel(b, 0.045, 4); mat(b, 'walnut')
    f = face_plane('bf', BS * 0.89, BS * 0.89, face); f.location = (0, 0, 0.3608)
    g = group('blk', (loc[0], loc[1], 0), [b, f], math.radians(rot)); return g, [b, f]
def make_rake(head_xy, angle):
    # the head sits against the block; the pole runs away at `angle` and up toward an unseen hand
    L = 14.0; up = math.radians(9)
    pole = cyl('pole', 0.035, L, 24); pole.rotation_euler = (0, math.radians(90) - up, 0); pole.location = (0.05, 0, 0.11); mat(pole, 'maple')
    fer = cyl('fer', 0.043, 0.18, 24); fer.rotation_euler = (0, math.radians(90) - up, 0); fer.location = (0.03, 0, 0.108); mat(fer, 'brass')
    head = box('head', 0.1, 1.2, 0.24, (0, 0, 0.0)); bevel(head, 0.02, 3); mat(head, 'walnut')
    g = group('rake', (head_xy[0], head_xy[1], 0.004), [pole, fer, head], math.radians(angle)); return g, [pole, fer, head]

subject = []
if MODE in ('block', 'mask'):
    g, subject = make_block(ARG['face'], (ARG['x'], ARG['y']), ARG.get('rot', 0))
elif MODE in ('rake', 'rakemask'):
    g, subject = make_rake((ARG['x'], ARG['y']), ARG['angle'])
if MODE.endswith('mask'):
    for o in TABLE: o.is_holdout = True
    sc.render.film_transparent = True

# ---------- light, camera ----------
def light(name, kind, loc, energy, size, color, rot=(0, 0, 0)):
    l = bpy.data.lights.new(name, kind); l.energy = energy; l.color = color
    if kind == 'AREA': l.size = size
    else: l.shadow_soft_size = size
    o = link(bpy.data.objects.new(name, l)); o.location = loc; o.rotation_euler = rot; return o, l
k, kl = light('lamp', 'SPOT', (-1.5, -12.5, 15.0), 30000, 1.5, (1.0, 0.84, 0.62), (math.radians(38), math.radians(-12), 0))
kl.spot_size = math.radians(55); kl.spot_blend = 1.0
light('key', 'AREA', (-6.0, -11.0, 9.0), 500, 3.0, (1.0, 0.88, 0.72), (math.radians(52), math.radians(-30), 0))
light('fill', 'AREA', (9.0, -12, 6), 80, 6, (0.72, 0.8, 1.0), (math.radians(62), math.radians(36), 0))
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs[0].default_value = (0.010, 0.008, 0.006, 1)
if PADDED: RX, RY = RX + 2 * PADX, RY + 2 * PADY  # same lens, taller sensor: identical pixel scale, wider view
cam = bpy.data.cameras.new('cam'); cam.lens = 30; cam.sensor_fit = 'VERTICAL'; cam.sensor_height = 24 * RY / (RY - 2 * PADY if PADDED else RY)
co = link(bpy.data.objects.new('cam', cam)); co.location = (1.5, -12.0, 13.2)
tgt = link(bpy.data.objects.new('tgt', None)); tgt.location = (1.5, -1.7, 0)
c = co.constraints.new('TRACK_TO'); c.target = tgt; c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'
cam.dof.use_dof = True; cam.dof.aperture_fstop = 11; cam.dof.focus_object = tgt; sc.camera = co
sc.render.resolution_x = RX; sc.render.resolution_y = RY; sc.render.resolution_percentage = 100
bpy.context.view_layer.update()

if MODE in ('cam', 'campad'):
    dg = bpy.context.evaluated_depsgraph_get()
    Pm = co.calc_matrix_camera(dg, x=RX, y=RY) @ co.matrix_world.inverted()
    json.dump({'P': [list(r) for r in Pm], 'RX': RX, 'RY': RY, 'PADX': PADX if PADDED else 0, 'PADY': PADY if PADDED else 0}, open(OUT, 'w')); print('CAM', OUT); sys.exit(0)

# crop to the subject so sprite renders are quick
if subject:
    from bpy_extras.object_utils import world_to_camera_view
    pts = []
    for o in subject:
        for v in o.bound_box: pts.append(world_to_camera_view(sc, co, o.matrix_world @ Vector(v)))
    pad = 0.06
    x0 = max(0, min(p.x for p in pts) - pad); x1 = min(1, max(p.x for p in pts) + pad)
    y0 = max(0, min(p.y for p in pts) - pad * 0.6); y1 = min(1, max(p.y for p in pts) + pad * 0.6)
    sc.render.use_border = True; sc.render.use_crop_to_border = False
    sc.render.border_min_x, sc.render.border_max_x, sc.render.border_min_y, sc.render.border_max_y = x0, x1, y0, y1
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = SMP; sc.cycles.use_adaptive_sampling = True; sc.cycles.adaptive_threshold = 0.01
sc.cycles.use_denoising = True; sc.cycles.seed = 3
sc.render.filepath = OUT; sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_mode = 'RGBA'; sc.render.image_settings.color_depth = '16'
sc.view_settings.view_transform = 'Standard'
bpy.ops.render.render(write_still=True); print('RENDERED', OUT)
