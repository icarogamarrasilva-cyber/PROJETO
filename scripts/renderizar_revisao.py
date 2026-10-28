from pathlib import Path
import bpy,json,math
from mathutils import Vector
R=Path(__file__).resolve().parents[1]/'revisao_02';g=json.loads((R/'modelo_3d/projeto_geometria.json').read_text())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def mat(n,c):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);return m
white=mat('Reboco claro',(.86,.83,.75));frame=mat('Aluminio grafite',(.06,.09,.1));glass=mat('Vidro',(.27,.55,.65));wood=mat('Madeira',(.45,.24,.1));concrete=mat('Laje / concreto',(.6,.6,.58));grass=mat('Jardim permeavel',(.35,.5,.23));patio=mat('Patio impermeabilizado',(.73,.71,.65));accent=mat('Painel comercial',(.26,.32,.33))
col={}
for n in ['Terreno','Terreo','Superior','Cobertura','Mobiliario','Escada']:
 c=bpy.data.collections.new(n);bpy.context.scene.collection.children.link(c);col[n]=c
active='Terreno'
def box(n,x,y,z,w,d,h,m=white):
 if min(w,d,h)<=.0001:return
 bpy.ops.mesh.primitive_cube_add(size=1,location=(x+w/2,y+d/2,z+h/2));o=bpy.context.object;o.name=n;o.dimensions=(w,d,h);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m)
 for c in list(o.users_collection):c.objects.unlink(o)
 col[active].objects.link(o);return o
box('Terreno 20x50',0,0,-.25,20,50,.2,grass)
box('Patio frontal',0,0,-.05,20,12,.05,concrete);box('Rota residencial',0,12,-.05,2,30,.05,concrete)
for i,(x,w) in enumerate([(2,3.6),(6.8,2.4),(9.2,2.4),(11.6,2.4),(14,2.4),(16.4,2.4)]):
 for dx in [0,w]:box('Demarcacao vaga',x+dx,5.8,.005,.035,5,.015,white)
box('Passeio frontal',2,10.8,0,18,1.2,.03,white)
active='Terreo';box('Laje terreo',2,12,-.15,16,30,.15,concrete)
# Intermediate slab with actual opening for two-flight staircase at x7..13,y37..41.5.
box('Laje superior principal',2,12,4.0,16,25,.2,concrete);box('Laje superior fundo',2,41.5,4.0,16,.5,.2,concrete)
box('Laje superior oeste',2,37,4.0,5,4.5,.2,concrete);box('Laje superior leste',13,37,4.0,5,4.5,.2,concrete)
for wall in g['walls']:
 x=wall['x'];y=wall['y'];z=wall['z'];h=wall['height'];L=wall['length'];axis=wall['axis'];name=wall['name'];t=wall['thickness'];active='Superior' if z>0 else 'Terreo'
 def block(s,b,w,hh,ma=white,label='alvenaria'):
  return box(name+'_'+label,x+s if axis=='X' else x,y if axis=='X' else y+s,z+b,w if axis=='X' else t,t if axis=='X' else w,hh,ma)
 at=0
 for s,w,b,hh,k,code in sorted(wall['openings']):
  block(at,0,s-at,h);block(s,0,w,b);block(s,b+hh,w,h-b-hh)
  if k in ['J','P']:
   for ss in [s,s+w-.05]:block(ss,b,.05,hh,frame,'batente')
   for bb in [b,b+hh-.05]:block(s,bb,w,.05,frame,'travessa')
  if k=='J':
   block(s+w/2-.025,b,.05,hh,frame,'montante')
   if axis=='X':box(name+'_vidro',x+s+.05,y+.06,z+b+.05,w-.1,.025,hh-.1,glass)
   else:box(name+'_vidro',x+.06,y+s+.05,z+b+.05,.025,w-.1,hh-.1,glass)
   if b>0:block(s-.04,b-.035,w+.08,.035,concrete,'peitoril')
  elif k=='P':
   if code=='P1':
    box(name+'_folha_dupla1',x+s,y,z,.04,w/2,hh-.04,wood);box(name+'_folha_dupla2',x+s+w,y,z,.04,w/2,hh-.04,wood);at=s+w;continue
   flip=(axis=='Y' and ((name in ['Acesso quartos','Corredor'] and x<10) or (name=='Cozinha patio banho' and x>10))) or (axis=='X' and name=='WC frente')
   if axis=='Y':box(name+'_folha_'+code,x-w if flip else x,y+s,z,w,.04,hh-.04,wood)
   else:box(name+'_folha_'+code,x+s,y-w if flip else y,z,.04,w,hh-.04,wood)
  at=s+w
 block(at,0,L-at,h)
active='Superior'
for px,py,pw,ph in g['patios']:box('Piso patio descoberto',px,py,4.2,pw,ph,.025,patio)
# Simplified furniture in each unit, visible in cutaway.
active='Mobiliario'
for x,y in [(2,12),(11,12),(2,24),(11,24)]:
 mirror=x==11
 def fx(u,w=0):return x+u if not mirror else x+7-u-w
 for v,w in [(4.5,1.38),(8.5,.88)]:
  box('Cama',fx(.5,w),y+v,4.2,w,1.88,.42,wood);box('Colchao',fx(.5,w),y+v,4.62,w,1.88,.15,white)
 box('Sofa',fx(.35,2),y+.4,4.2,2,.85,.7,accent)
 box('Mesa jantar',fx(3.8,1.2),y+.6,4.9,1.2,1.2,.06,wood)
 box('Bancada cozinha',fx(6.3,.6),y+4.2,4.2,.6,1.8,.9,white)
 box('Box banho',fx(5.9,1),y+10.7,4.2,1,1.15,.06,glass)
active='Escada';e=4.2/24
for i in range(11):
 box('Degrau lance1',7.2,37.2+i*.28,0,1.2,.28,(i+1)*e,concrete)
 box('Degrau lance2',9.6,37.2+(10-i)*.28,2.1,1.2,.28,(i+1)*e,concrete)
box('Patamar',7.2,40.28,1.95,3.6,1.2,.15,concrete)
for x in [7.15,8.45,9.55,10.85]:
 for i in range(0,11,2):
  z=(i+1)*e if x<9 else 2.1+(11-i)*e
  box('Montante guarda corpo',x,37.2+i*.28,z,.04,.04,1.1,frame)
# Actual roof has holes for the open-air patios. Grid cells remove patio rectangles.
active='Cobertura'
xs=sorted({2,18,*[v for p in g['patios'] for v in [p[0],p[0]+p[2]]]});ys=sorted({12,42,*[v for p in g['patios'] for v in [p[1],p[1]+p[3]]]})
for a,b in zip(xs,xs[1:]):
 for c,d in zip(ys,ys[1:]):
  if any(px<(a+b)/2<px+pw and py<(c+d)/2<py+ph for px,py,pw,ph in g['patios']):continue
  box('Cobertura com patios',a,c,7.05,b-a,d-c,.15,concrete)
for x,y,w,d in [(2,12,16,.15),(2,41.85,16,.15),(2,12,.15,30),(17.85,12,.15,30)]:box('Platibanda',x,y,7.2,w,d,.9)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.world.color=(.8,.8,.8)
scene.render.resolution_x=1800;scene.render.resolution_y=1300;scene.render.resolution_percentage=100
bpy.ops.object.camera_add(location=(43,-38,37));camera=bpy.context.object;camera.rotation_euler=(Vector((10,26,2.5))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=56;scene.camera=camera
bpy.ops.wm.save_as_mainfile(filepath=str(R/'modelo_3d/projeto_Icaro.blend'))
bpy.ops.wm.obj_export(filepath=str(R/'modelo_3d/projeto_Icaro.obj'))
scene.render.filepath=str(R/'previas/perspectiva_revisada.png');bpy.ops.render.render(write_still=True)
col['Cobertura'].hide_render=True
# Cutaway removes upper wall tops only in view, preserving complete model in saved file.
for o in col['Superior'].objects:
 if o.type=='MESH':
  zs=[(o.matrix_world@v.co).z for v in o.data.vertices]
  if min(zs)>=5.1:
   o.hide_render=True;continue
  for v in o.data.vertices:
   world=o.matrix_world@v.co
   if world.z>5.1:
    world.z=5.1;v.co=o.matrix_world.inverted()@world
camera.location=(40,-15,53);camera.rotation_euler=(Vector((10,27,1))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=48
scene.render.filepath=str(R/'previas/axon_superior.png');bpy.ops.render.render(write_still=True)
print('VISTAS_GERADAS')
