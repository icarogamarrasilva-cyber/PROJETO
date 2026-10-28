from pathlib import Path
import math,json,csv,textwrap
import ezdxf
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
R=Path(__file__).resolve().parents[1]/'revisao_02'
D=ezdxf.new('R2010');D.units=6
COL={'PAREDES':('#202020',7,.42),'ESQUADRIAS':('#154e69',4,.23),'MOBILIARIO':('#666666',8,.15),'COTAS':('#624b28',2,.13),'TEXTOS':('#151515',7,.15),'TERRENO':('#3c6944',3,.25),'CORTE':('#111111',7,.55)}
for n,(_,co,w) in COL.items():D.layers.new(n,dxfattribs={'color':co,'lineweight':int(w*100)})
M=D.modelspace();drawings={};cur=None;offset=0;walls=[];shift=0;current_name=""
def start(name,off):
 global cur,offset,shift,current_name
 current_name=name
 shift=2 if name in ['terreo','superior','cobertura'] else 0
 cur=[];offset=off;drawings[name]={'items':cur,'offset':off}
def line(x,y,xx,yy,l='PAREDES'):
 cur.append(('line',x,y+shift,xx,yy+shift,l));M.add_line((x+offset,y+shift),(xx+offset,yy+shift),dxfattribs={'layer':l})
def rect(x,y,w,h,l='PAREDES'):
 for a,b,c,d in [(x,y,x+w,y),(x+w,y,x+w,y+h),(x+w,y+h,x,y+h),(x,y+h,x,y)]:line(a,b,c,d,l)
def circle(x,y,r,l='MOBILIARIO'):
 cur.append(('circle',x,y+shift,r,l));M.add_circle((x+offset,y+shift),r,dxfattribs={'layer':l})
def arc(x,y,r,a,b,l='ESQUADRIAS'):
 cur.append(('arc',x,y+shift,r,a,b,l));M.add_arc((x+offset,y+shift),r,a,b,dxfattribs={'layer':l})
def label(x,y,s,h=.18,l='TEXTOS'):
 if current_name.startswith('det_') and current_name!='det_construtivo':h=min(h,.055)
 for i,t in enumerate(s.split('\n')):
  cur.append(('text',x,y+shift-i*h*1.4,t,h,l));M.add_text(t,dxfattribs={'height':h,'insert':(x+offset,y+shift-i*h*1.4),'layer':l})
def dim(x,y,xx,yy,dist):
 dh=.055 if current_name.startswith('det_') else .20
 d=M.add_aligned_dim((x+offset,y+shift),(xx+offset,yy+shift),distance=dist,dimstyle='EZDXF',override={'dimtxt':dh,'dimasz':.13,'dimdec':2,'dimtad':1},dxfattribs={'layer':'COTAS'});d.render()
 # Print manually at exact same world scale, DXF retains native DIMENSION.
 if abs(yy-y)<.001:
  q=y+dist;line(x,y,x,q+.15,'COTAS');line(xx,yy,xx,q+.15,'COTAS');line(x,q,xx,q,'COTAS')
  for k in [x,xx]:line(k-.08,q-.08,k+.08,q+.08,'COTAS')
  label((x+xx)/2-.25,q+.12,f'{abs(xx-x):.2f}',dh,'COTAS')
 else:
  q=x-dist;line(x,y,q-.15,y,'COTAS');line(xx,yy,q-.15,yy,'COTAS');line(q,y,q,yy,'COTAS')
  for k in [y,yy]:line(q-.08,k-.08,q+.08,k+.08,'COTAS')
  label(q+.12,(y+yy)/2,f'{abs(yy-y):.2f}',dh,'COTAS')
def leaf(x,y,w,axis='X',flip=False):
 if axis=='X':
  sign=-1 if flip else 1
  line(x,y,x,y+sign*w,'ESQUADRIAS');line(x+.035,y,x+.035,y+sign*w,'ESQUADRIAS');arc(x,y,w,270 if flip else 0,360 if flip else 90)
 else:
  sign=-1 if flip else 1
  line(x,y,x+sign*w,y,'ESQUADRIAS');line(x,y+.035,x+sign*w,y+.035,'ESQUADRIAS');arc(x,y,w,90 if flip else 0,180 if flip else 90)
def wall(name,x,y,L,axis='X',z=0,H=4.00,opens=(),record=True,t=.15):
 # Opening: position, width, sill, height, type P/J/V, code.
 if record:walls.append({'name':name,'x':x,'y':y,'length':L,'axis':axis,'z':z,'height':H,'thickness':t,'openings':list(opens)})
 def p(s,v):return (x+s,y+v) if axis=='X' else (x+v,y+s)
 def seg(a,b,v):
  a1,b1=p(a,v);a2,b2=p(b,v);line(a1,b1,a2,b2)
 at=0
 for s,w,b,h,kind,code in sorted(opens):
  # All windows have actual voids in both CAD plan lines.
  for v in [0,t]:seg(at,s,v)
  for k in [s,s+w]:
   a,bb=p(k,0);c,d=p(k,t);line(a,bb,c,d,'ESQUADRIAS')
  if kind=='P':
   a,bb=p(s,t);flip=(axis=='Y' and ((name in ['Acesso quartos','Corredor'] and x<10) or (name=='Cozinha patio banho' and x>10))) or (axis=='X' and name=='WC frente');leaf(a,bb,w,axis,flip) if code!='P1' else (leaf(a,bb,w/2,axis),line(a+w,bb,a+w,bb+w/2,'ESQUADRIAS'),arc(a+w,bb,w/2,90,180))
  elif kind=='J':
   for v in [.045,.105]:
    a,bb=p(s,v);c,d=p(s+w,v);line(a,bb,c,d,'ESQUADRIAS')
   for k in [s+.05,s+w/2,s+w-.05]:
    a,bb=p(k,.02);c,d=p(k,.13);line(a,bb,c,d,'ESQUADRIAS')
  a,bb=p(s+w/2,.35);label(a,bb,code,.17)
  at=s+w
 for v in [0,t]:seg(at,L,v)
def bed(x,y,double=True):
 w=1.38 if double else .88;rect(x,y,w,1.88,'MOBILIARIO');rect(x+.05,y+1.45,w-.1,.35,'MOBILIARIO');line(x,y+.35,x+w,y+.35,'MOBILIARIO')
def toilet(x,y):
 rect(x,y,.4,.18,'MOBILIARIO');circle(x+.2,y+.40,.19);rect(x+.03,y+.18,.34,.4,'MOBILIARIO')
def sink(x,y):
 rect(x,y,.55,.45,'MOBILIARIO');circle(x+.275,y+.22,.16)
def stairs(record=True):
 rect(7,35,6,4.5);rect(7.2,35.2,1.2,3.08);rect(9.6,35.2,1.2,3.08)
 for i in range(12):
  line(7.2,35.2+i*.28,8.4,35.2+i*.28);line(9.6,35.2+i*.28,10.8,35.2+i*.28)
 rect(7.2,38.28,3.6,1.2);line(7.8,35.4,7.8,38.1,'ESQUADRIAS');line(10.2,38.1,10.2,35.4,'ESQUADRIAS')
 label(7.45,36,'SOBE',.15);label(9.8,36,'DESCE',.15)
 label(7.3,39.8,'24e = 17,50 cm / p = 28 cm',.18)
 rect(14,35,2,2);label(14.15,36.4,'ELEVADOR\nRESERVA\n2,00 x 2,00',.15)
def shell(z=0):
 upper=z>0;H=2.85 if upper else 4.00
 op=[]
 if not upper:
  for i in range(3):
   a=i*16/3+.8;op.extend([(a,1.1,0,2.7,'J','V1'),(a+1.1,1.6,0,2.7,'P','P1'),(a+2.7,1.1,0,2.7,'J','V1')])
 else:op=[(1,5,.9,1.2,'J','J3'),(10,5,.9,1.2,'J','J3')]
 wall('Frente',2,10,16,z=z,H=H,opens=op)
 wall('Fundo',2,39.85,16,z=z,H=H,opens=[(1,5,1,1.2,'J','J3'),(10,5,1,1.2,'J','J3')])
 for x in [2,17.85]:
  op=[(25,1.3,0,2.4,'P','P2')] if not upper and x==2 else []
  if upper:
   op=[(v-10,2.2,.9,1.5,'J','J1') for v in [14.5,18.5,26.5,30.5]]+[(v-10,3.6,.75,1.9,'J','J5') for v in [10.2,22.2]]
  wall('Lateral',x,10,30,'Y',z,H,op)

# SITE
start('implantacao',0)
rect(0,0,20,50,'TERRENO');rect(2,12,16,30);rect(0,0,20,12,'MOBILIARIO');label(3,29,'EDIFICAÇÃO MISTA\nPROJEÇÃO 480,00 m²',.38)
for x in [2,9,11,18]:line(x,12,x,42,'MOBILIARIO')
for x,w,n in [(2,3.6,'PCD'),(6.8,2.4,'IDOSO'),(9.2,2.4,'AP01'),(11.6,2.4,'AP02'),(14,2.4,'AP03'),(16.4,2.4,'AP04')]:rect(x,5.8,w,5,'MOBILIARIO');label(x+.15,8,n,.24)
rect(5.6,5.8,1.2,5,'ESQUADRIAS');rect(2,10.8,18,1.2,'ESQUADRIAS');label(6,3,'FAIXA DE MANOBRA: 5,80 m',.25)
line(17,0,17,4,'COTAS');label(12,.5,'ACESSO VEÍCULOS',.2)
label(.1,25,'ROTA\nLIVRE\n2,00 m',.22);label(18.2,29,'JARDIM',.2);label(3,46,'JARDIM POSTERIOR / 160 m²',.32)
label(2,-2,'RUA / TESTADA • 20,00 m',.3);label(2,44,'NORTE HIPOTÉTICO AO FUNDO',.20);line(20.8,44,20.8,49,'TERRENO');line(20.8,49,20.5,48,'TERRENO');line(20.8,49,21.1,48,'TERRENO');label(20.5,50,'N',.4)
dim(0,0,20,0,-1);dim(0,0,0,50,1.5);dim(2,12,18,12,-1);dim(18,0,18,12,-4);dim(18,42,18,50,-4)
# GROUND FLOOR
start('terreo',70);shell()
for x in [2+16/3,2+32/3]:wall('Divisoria comercial',x,10,24,'Y')
wall('Separacao setores',2,34,16)
for i in range(3):
 x=2+i*16/3;label(x+.5,23,f'LOJA {i+1:02d}\n128,00 m² brutos\nSALÃO FLEXÍVEL',.24)
 # Shop WC nominal 2.2x2.4. Door outward swing described in enlarged detail.
 wall('WC frente',x+.25,31.45,2.2,opens=[(.25,.9,0,2.1,'P','P3')]);wall('WC fundo',x+.25,33.7,2.2)
 wall('WC lado',x+.25,31.45,2.4,'Y');wall('WC lado',x+2.3,31.45,2.4,'Y')
 toilet(x+.5,33);sink(x+1.65,33.1);circle(x+1.35,32.25,.75)
 wall('WC frente',x+2.7,31.45,2.2,opens=[(.25,.9,0,2.1,'P','P3')]);wall('WC fundo',x+2.7,33.7,2.2)
 wall('WC lado',x+2.7,31.45,2.4,'Y');wall('WC lado',x+4.75,31.45,2.4,'Y')
 toilet(x+2.95,33);sink(x+4.1,33.1);label(x+2.85,30.8,'SANIT. M',.18)
 rect(x+2.8,29.5,1.7,.6,'MOBILIARIO');sink(x+3.2,29.55);label(x+2.85,30.6,'COPA',.19)
 rect(x+4.5,33.5,.3,.3,'ESQUADRIAS');label(x+2.8,34.4,'EXAUSTÃO MECÂNICA A COBERTURA',.12)
 rect(x+.6,12,1.5,.65,'MOBILIARIO');label(x+.7,13,'BALCÃO',.16)
 for yy in [17,20,26]:rect(x+.4,yy,.5,1.5,'MOBILIARIO')
 label(x+.45,30.8,'SANIT. F / ADAPTÁVEL*',.18)
 label(x+.65,9.4,'ENTRADA / VITRINE',.18)
stairs();label(3,38,'HALL RESIDENCIAL\nACESSO INDEPENDENTE',.23)
label(.1,36,'ACESSO\nRESIDENCIAL',.18)
line(0,25,20,25,'CORTE');label(.2,25.3,'A',.3);label(19,25.3,'A',.3)
line(8.8,8,8.8,42,'CORTE');label(9,41,'B',.3)
dim(2,10,18,10,-2);dim(18,10,18,34,-1.5);dim(18,34,18,40,-1.5)
for i in range(3):dim(2+i*16/3,10,2+(i+1)*16/3,10,-1)
# UPPER FLOOR: internal open-air patios (2.5x2.0m) instead of blind sanitary rooms.
start('superior',140);shell(4.2)
for x in [9,10.85]:wall('Corredor',x,10,24,'Y',4.2,2.85,[(1,.9,0,2.1,'P','P3'),(13,.9,0,2.1,'P','P3')])
for x in [2,11]:wall('Separacao unidades',x,22,7,z=4.2,H=2.85)
wall('Hall superior',2,34,16,z=4.2,H=2.85,opens=[(7,2,0,2.4,'V','VÃO')]);patios=[]
for num,(x,y) in enumerate([(2,10),(11,10),(2,22),(11,22)],1):
 mirror=x==11
 def xx(u):return x+u if not mirror else x+7-u
 def hw(n,u,v,L,op=()):
  if mirror:op=[(L-s-w,w,b,h,k,c) for s,w,b,h,k,c in op]
  wall(n,min(xx(u),xx(u+L)),y+v,L,z=4.2,H=2.85,opens=op)
 def vw(n,u,v,L,op=()):wall(n,xx(u),y+v,L,'Y',4.2,2.85,op)
 def rr(u,v,w,h):rect(min(xx(u),xx(u+w)),y+v,w,h,'MOBILIARIO')
 def tx(u,v,s,h=.16):label(min(xx(u),xx(u+2.6)),y+v,s,h)
 hw('Dormitorios',0,4,3.1);hw('Dormitorios',0,8,3.1)
 vw('Acesso quartos',3.1,4,8,[(1,.8,0,2.1,'P','P4'),(5,.8,0,2.1,'P','P4')])
 vw('Cozinha patio banho',4.25,4,8,[(.5,.9,0,2.1,'P','P3'),(3.2,.8,0,2.1,'P','P4'),(6.7,.8,0,2.1,'P','P4')])
 hw('Janela cozinha patio',4.25,6.3,2.75,[(.6,1.4,1.1,1.4,'J','J2')]);hw('Janela banho patio',4.25,10.5,2.75,[(.7,1.2,1.5,.8,'J','J4')])
 tx(.25,3.4,f'APTO {num:02d} / ESTAR-JANTAR\n72,45 m² cobertos + 11,55 m² pátio',.18)
 tx(.3,7.5,'QUARTO 1 / 12,40 m²\nMÓDULO 3,10 x 4,00',.16);tx(.3,11.5,'QUARTO 2 / 12,40 m²\nMÓDULO 3,10 x 4,00',.16)
 tx(4.4,6.1,'COZ. / SERV.\n2,75 x 2,30',.15);tx(4.4,9.6,'PÁTIO ABERTO\n2,75 x 4,20\n11,55 m²',.15);tx(4.4,11.9,'BANHO\n2,75 x 1,50',.15)
 rr(.35,.4,2,.85);rr(.4,1.6,1.1,.45);rr(3.8,.6,1.2,1.2)
 for u,v in [(3.7,.4),(3.7,1.8),(5.1,.4),(5.1,1.8)]:rr(u,v,.4,.4)
 for v,double in [(4.5,True),(8.5,False)]:bed(min(xx(.5),xx(.5+(1.38 if double else .88))),y+v,double)
 rr(2.4,4.4,.55,2);rr(2.4,8.4,.55,2)
 rr(6.3,4.2,.6,1.8);rr(4.5,4.2,.6,.6);tx(4.8,4.9,'LAV.',.12)
 bx=min(xx(4.8),xx(5.35));sink(min(xx(5.1),xx(5.65)),y+10.65);toilet(min(xx(4.6),xx(5.0)),y+11.15);rr(5.9,10.7,1.0,1.15)
 px=min(xx(4.25),xx(7));patios.append([px,y+6.3,2.75,4.2]);rect(px,y+6.3,2.75,4.2,'TERRENO')
 for q in [.2,.5,.8]:line(px+.2,y+6.3+q,px+2.5,y+6.3+q,'TERRENO')
 label(px+.15,y+7.25,'RALO / IMPERM.',.12)
 # Internal module dimension strings drawn on corresponding partitions.
 dim(min(xx(0),xx(3.1)),y+4,min(xx(0),xx(3.1))+3.1,y+4,.3)
 dim(px,y+10.5,px+2.75,y+10.5,.3)
 dim(min(xx(3.1),xx(4.25)),y+4,min(xx(3.1),xx(4.25))+1.15,y+4,.3)
 ox=min(xx(0),xx(3.1))+.4
 for va,vb in [(0,4),(4,8),(8,12)]:dim(ox,y+va,ox,y+vb,.15)
stairs();label(3,38,'HALL / CIRCULAÇÃO',.22);label(9.3,32,'CIRC.\n1,85 m\nLIVRE*',.18)
line(0,25,20,25,'CORTE');label(.2,25.3,'A',.3);label(19,25.3,'A',.3);line(8.8,8,8.8,42,'CORTE');label(9,41,'B',.3)
dim(2,10,9,10,-1);dim(9,10,11,10,-1);dim(11,10,18,10,-1);dim(2,10,18,10,-2)
for ya,yb in [(10,22),(22,34),(34,40)]:dim(18,ya,18,yb,-1.5)
# COVER
start('cobertura',210);rect(2,10,16,30)
for p in patios:rect(*p,'TERRENO');label(p[0]+.1,p[1]+1.1,'PÁTIO\nABERTO',.16)
for x in [2.15,17.65]:rect(x,10.15,.2,29.7,'ESQUADRIAS')
line(10,10.2,10,39.8,'ESQUADRIAS');label(3,38,'COBERTURA LEVE / TELHA TERMOACÚSTICA',.22)
for y in [13,24,35]:
 for a,b in [(10,3),(10,17)]:line(a,y,b,y,'COTAS');label(min(a,b)+1,y+.2,'i = 5%*',.18)
label(3,12,'*Inclinação indicativa; confirmar fabricante.\nCalhas / condutores / extravasores a dimensionar.',.18)
dim(2,10,18,10,-1.2);dim(18,10,18,40,-1.5)
# Consistent elevations from actual opening lists.
for name,axis,value,off in [('frontal','X',10,280),('posterior','X',39.85,320),('oeste','Y',2,360),('leste','Y',17.85,410)]:
 start(name,off);L=16 if axis=='X' else 30
 rect(0,0,L,8.1);line(0,4.00,L,4.00);line(0,4.2,L,4.2);line(0,7.05,L,7.05);line(0,7.2,L,7.2)
 for w in walls:
  if w['axis']!=axis or abs(w['y' if axis=='X' else 'x']-value)>.01:continue
  for s,ww,b,h,k,code in w['openings']:
   z=w['z']+b;rect(s,z,ww,h,'ESQUADRIAS');rect(s+.05,z+.05,ww-.1,h-.1,'ESQUADRIAS')
   if k=='J':line(s+ww/2,z,s+ww/2,z+h,'ESQUADRIAS')
   if k=='P':circle(s+ww-.12,z+1,.035,'ESQUADRIAS')
 if name=='frontal':
  for i in range(3):label(i*16/3+1.3,2.95,f'LOJA {i+1:02d}',.24)
 dim(0,0,L,0,-1);dim(L,0,L,4.2,-1);dim(L,4.2,L,7.2,-1);dim(L,7.2,L,8.1,-1)
# Sections at A y25, B x8.8, drawing actual wall intersections and patio voids.
def section(name,off,axis,coord):
 start(name,off);lo=2 if axis=='X' else 10;L=16 if axis=='X' else 30
 rect(0,-.15,L,.15,'CORTE');rect(0,4.00,L,.20,'CORTE')
 # Roof pieces exclude patio footprints intersected by this section.
 gaps=[]
 for px,py,pw,ph in patios:
  if axis=='X' and py<=coord<=py+ph:gaps.append((px-lo,px+pw-lo))
  if axis=='Y' and px<=coord<=px+pw:gaps.append((py-lo,py+ph-lo))
 at=0
 for a,b in sorted(gaps):rect(at,7.05,a-at,.15,'CORTE');at=b
 rect(at,7.05,L-at,.15,'CORTE')
 for w in walls:
  # perpendicular walls crossed by section; no arbitrary relocation of elements.
  if w['axis']==axis:continue
  x,y=w['x'],w['y'];q=(x if axis=='X' else y)-lo
  along=coord-(y if axis=='X' else x)
  if not -.001<=along<=w['length']+.001:continue
  z=w['z'];h=w['height'];op=next((o for o in w['openings'] if o[0]<=along<=o[0]+o[1]),None)
  if op:
   if op[2]>0:rect(q,z,.15,op[2],'CORTE')
   top=op[2]+op[3]
   if h>top:rect(q,z+top,.15,h-top,'CORTE')
  else:rect(q,z,.15,h,'CORTE')
 rect(0,7.2,.15,.9,'CORTE');rect(L-.15,7.2,.15,.9,'CORTE')
 for z,s in [(0,'±0,00'),(4.2,'+4,20'),(7.2,'+7,20'),(8.1,'+8,10')]:line(L+.2,z,L+1,z,'COTAS');label(L+1.1,z+.1,s,.22)
 dim(0,0,L,0,-1);dim(L,0,L,4.2,-3);dim(L,4.2,L,7.2,-3)
 label(.6,2.5,'COMÉRCIO / HALL',.24);label(.6,5.7,'RESIDENCIAL / CIRCULAÇÃO',.24)
 if axis=='Y':
  # Section B at X=8.8 passes through stair landing but not treads; show treads projected dashed schematic.
  for i in range(11):rect(25.2+i*.28,0,.28,(i+1)*4.2/24,'MOBILIARIO')
  label(24,4.5,'NÚCLEO VERTICAL\nESCADA EM PROJEÇÃO',.18)
section('corte_a',460,'X',25);section('corte_b',510,'Y',8.8)
# Detail sheets
start('det_porta',570)
wall('Detalhe porta',0,0,2,opens=[(.5,.9,0,2.1,'P','P3')],record=False);dim(.5,0,1.4,0,-.3);label(.1,1.5,'PLANTA / PORTA P3',.12)
rect(0,2.5,.9,2.1,'ESQUADRIAS');rect(.04,2.54,.82,2.02,'ESQUADRIAS');circle(.77,3.5,.025,'ESQUADRIAS');dim(0,2.5,.9,2.5,-.25);dim(.9,2.5,.9,4.6,-.3);label(0,4.85,'VISTA / BATENTE E FOLHA',.12)
start('det_janela',580)
wall('Detalhe janela',0,0,2.7,opens=[(.25,2.2,.9,1.5,'J','J1')],record=False);dim(.25,0,2.45,0,-.3)
rect(0,2,2.2,1.5,'ESQUADRIAS');rect(.05,2.05,2.1,1.4,'ESQUADRIAS');line(1.1,2,1.1,3.5,'ESQUADRIAS');dim(0,2,2.2,2,-.25);dim(2.2,2,2.2,3.5,-.3);label(0,3.8,'J1 / ABRIR / ÁREA LIVRE >=70%',.12)
start('det_sanitario',590)
wall('WC detalhe',0,0,2.2,opens=[(.15,.9,0,2.1,'V','P3')],record=False)
wall('WC detalhe',0,2.25,2.2,record=False);wall('WC detalhe',0,0,2.4,'Y',record=False);wall('WC detalhe',2.05,0,2.4,'Y',record=False)
# Accessible outward door arc, fixture reference and turning circle.
line(.15,0,.15,-.9,'ESQUADRIAS');arc(.15,0,.9,270,360);toilet(.35,1.65);sink(1.45,1.7);circle(1.15,1.1,.75)
line(.2,1.5,.2,2.1,'ESQUADRIAS');line(.2,2.08,.95,2.08,'ESQUADRIAS');label(.85,1.1,'Ø 1,50',.1)
dim(0,0,2.2,0,-1.2);dim(2.2,0,2.2,2.4,-.5)
label(0,3.1,'SANITÁRIO / ARRANJO PRELIMINAR\nCírculo de giro e barras indicativas.\nConferir transferências livres na etapa legal.',.12)
start('det_escada',600)
# local coordinates for enlarged stair, independent of full building origin.
rect(0,0,6,4.5);rect(.2,.2,1.2,3.08);rect(2.6,.2,1.2,3.08);rect(.2,3.28,3.6,1.2)
for i in range(12):
 for x in [.2,2.6]:line(x,.2+i*.28,x+1.2,.2+i*.28)
for x in [.15,1.45,2.55,3.85]:line(x,.2,x,3.28,'ESQUADRIAS')
dim(.2,0,1.4,0,-.5);dim(2.6,0,3.8,0,-.5);dim(0,0,0,4.5,.6)
label(.3,4.9,'ESCADA / 24 ESPELHOS / 2 LANCES',.15)
# one enlarged corner showing slab, sill drip, parapet waterproofing
start('det_construtivo',620)
rect(0,0,.15,2.7,'CORTE');rect(-.4,0,1.8,.15,'CORTE');rect(-.05,2.7,.25,.15,'CORTE');line(-.1,2.85,.25,2.85,'ESQUADRIAS');line(.25,2.85,.25,2.78,'ESQUADRIAS');line(.15,.15,1.4,.15,'ESQUADRIAS');line(.15,.15,.15,.4,'ESQUADRIAS')
label(.4,2.8,'RUFO / PINGADEIRA',.12);label(.4,.35,'IMPERMEABILIZAÇÃO\nRODAPÉ / CAIMENTO AO RALO',.12)
# preserve machine-readable geometry used by 3D, drawings, areas and verification
(R/'modelo_3d/projeto_geometria.json').write_text(json.dumps({'walls':[dict(w,y=w['y']+2) for w in walls],'patios':[[x,y+2,w,h] for x,y,w,h in patios],'levels':[0,4.2,7.2,8.1]},ensure_ascii=False))
areas={'terreno_m2':1000,'projecao_m2':480,'terreo_coberto_m2':480,'superior_coberto_m2':433.8,'total_coberto_m2':913.8,'construida_incluindo_patios_m2':960,'loja_bruta_m2':128,'apartamento_coberto_bruto_m2':72.45,'patio_por_apartamento_m2':11.55,'comum_terreo_m2':96,'comum_superior_m2':144,'patios_superiores_descobertos_m2':46.2,'livre_solo_m2':520,'permeavel_proposta_m2':200}
(R/'documentacao/areas.json').write_text(json.dumps(areas,indent=2))
with (R/'documentacao/quadro_areas.csv').open('w',newline='') as f:
 w=csv.writer(f,delimiter=';');w.writerow(['Setor','Qtde','m2 unitarios brutos','m2 totais']);w.writerows([['Lojas',3,128,384],['Comum terreo',1,96,96],['Apartamentos cobertos',4,72.45,289.8],['Corredor superior',1,48,48],['Nucleo superior',1,96,96],['Total coberto',1,913.8,913.8],['Patios superiores descobertos',4,11.55,46.2],['Terreno',1,1000,1000],['Livre no solo',1,520,520],['Permeavel proposta',1,200,200]])
# PDF A2 landscape exact metric scales, not fit-to-page.
W,H=594,420
C=canvas.Canvas(str(R/'pranchas/projeto_academico_Icaro.pdf'),pagesize=(W*mm,H*mm));C.setTitle('Projeto misto - Icaro Gamarra Silva - RGM 3322.527')
def txt(x,y,s,size=8,bold=False):
 C.setFillColor(HexColor('#18262d'));C.setFont('Helvetica-Bold' if bold else 'Helvetica',size)
 for i,t in enumerate(s.split('\n')):C.drawString(x*mm,(y-i*size*.45)*mm,t)
def wrap(x,y,s,width=90,size=8):
 for para in s.split('\n'):
  for t in textwrap.wrap(para,width=width):txt(x,y,t,size);y-=size*.46
  y-=2
 return y
def frame(num,title,scales):
 C.setStrokeColor(HexColor('#243b49'));C.setLineWidth(.35*mm);C.rect(10*mm,10*mm,574*mm,400*mm)
 txt(18,400,'PROJETO ARQUITETÔNICO • EDIFICAÇÃO DE USO MISTO',15,True);txt(18,391,title,11)
 # bottom academic titleblock: fixed paper-space dimensions
 C.rect(10*mm,10*mm,574*mm,31*mm)
 for x in [250,421,535]:C.line(x*mm,10*mm,x*mm,41*mm)
 txt(14,35,'ALUNO: Icaro Gamarra Silva',10,True);txt(14,28,'RGM: 3322.527  |  CURSO: Engenharia Civil',9)
 txt(14,21,'PROVA DE DESENHO TÉCNICO',9);txt(14,14,'PROJETO: 3 LOJAS + 4 APARTAMENTOS',7)
 txt(254,35,'PROFESSORA: Rafaella Scalon',10,True);txt(254,27,'LOCAL: Dourados - MS | Lote hipotético: 20 x 50 m',8)
 txt(254,19,'ENTREGA: 28/10/2026 | REVISÃO: 02',8);txt(254,13,'ESTUDO ACADÊMICO / NÃO EXECUTIVO',7)
 txt(425,35,'ESCALAS',8,True);txt(425,27,scales,8);txt(425,18,'UNIDADES: m / detalhes em cm indicados',6.5)
 txt(540,33,f'{num:02d} / 08',17,True);txt(540,19,'A2 / 594 x 420',7)
 # paper-space CAD frame and titleblock, no misleading lack of actual sheets.
 layout=D.layouts.new(f'{num:02d}_{title[:15]}')
 layout.page_setup(size=(594,420),margins=(0,0,0,0),units='mm')
 layout.add_lwpolyline([(10,10),(584,10),(584,410),(10,410)],close=True)
 layout.add_lwpolyline([(10,10),(584,10),(584,41),(10,41)],close=True)
 for x,y,s,h in [(14,35,'Icaro Gamarra Silva | RGM 3322.527',3.2),(14,28,'Engenharia Civil | Prova de desenho tecnico',2.6),(254,35,'Professora: Rafaella Scalon',3),(254,27,'Dourados-MS | Entrega 28/10/2026 | Rev.02',2.6),(425,27,scales,2.6),(540,30,f'{num:02d}/08',6),(18,398,title,4)]:layout.add_text(s,dxfattribs={'height':h,'insert':(x,y)})
 return layout
layout=None
def plot(name,x,y,scale=100,crop=None):
 data=drawings[name];k=1000/scale
 # x,y = paper origin for drawing's local metric origin
 C.saveState();C.translate(x*mm,y*mm);C.scale(k*mm,k*mm)
 for item in data['items']:
  kind=item[0];l=item[-1];color,_,lw=COL[l];C.setStrokeColor(HexColor(color));C.setFillColor(HexColor(color));C.setLineWidth(lw/k)
  if kind=='line':C.line(*item[1:5])
  elif kind=='circle':C.circle(item[1],item[2],item[3],stroke=1,fill=0)
  elif kind=='arc':
   _,xx,yy,r,a,b,_=item;C.arc(xx-r,yy-r,xx+r,yy+r,startAng=a,extent=b-a)
  elif kind=='text':
   _,xx,yy,t,h,_=item;C.setFont('Helvetica',h*1.25);C.drawString(xx,yy,t)
 C.restoreState()
 # A modelspace viewport corresponds exactly to the drawn set; generous extent,
 # nonoverlapping PDF arrangement remains source of print composition.
 if layout is not None:
  pts=[]
  for it in data['items']:
   if it[0]=='line':pts.extend([(it[1],it[2]),(it[3],it[4])])
  if pts:
   xmin=min(p[0] for p in pts)-.4;xmax=max(p[0] for p in pts)+.4;ymin=min(p[1] for p in pts)-.4;ymax=max(p[1] for p in pts)+.4
   vp=layout.add_viewport(center=(x+(xmin+xmax)*k/2,y+(ymin+ymax)*k/2),size=((xmax-xmin)*k,(ymax-ymin)*k),view_center_point=(data['offset']+(xmin+xmax)/2,(ymin+ymax)/2),view_height=ymax-ymin)
   vp.dxf.flags=16384

quant_esq={}
for w in walls:
 for op in w['openings']:
  if op[4] in ['P','J']:quant_esq[op[5]]=quant_esq.get(op[5],0)+1
(R/'documentacao/quantitativo_esquadrias.json').write_text(json.dumps(quant_esq,indent=2))

def subtitle(x,y,s):txt(x,y,s,9,True)
def note(x,y,s,w=75):return wrap(x,y,s,w,8)
def finish():C.showPage()
layout=frame(1,'IMPLANTAÇÃO, COBERTURA E QUADRO DE ÁREAS','1:150 / 1:100')
plot('implantacao',39,52,150);subtitle(30,377,'IMPLANTAÇÃO • 1:150')
plot('cobertura',213,-50,100);subtitle(220,377,'COBERTURA • 1:100')
y=365
for s in ['QUADRO DE ÁREAS BRUTAS','Terreno: 1.000,00 m²','Projeção: 480,00 m²','Térreo coberto: 480,00 m²','Superior coberto: 433,80 m²','TOTAL COBERTO: 913,80 m²','CONSTRUÍDA COM PÁTIOS: 960,00 m²','Pátios superiores descobertos: 46,20 m²','Lojas: 3 x 128,00 = 384,00 m²','Aptos: 4 x 72,45 = 289,80 m² cobertos','Cada unidade: + 11,55 m² de pátio','Áreas comuns: 240,00 m²','Livre no solo: 520,00 m²','Permeável proposta: 200,00 m² (20%)','Ocupação geométrica: 48%','CA com pátios: 0,96 / coberto: 0,9138']:
 txt(430,y,s,9,s.isupper());y-=9
note(430,210,'Áreas brutas incluem paredes e reservas. Pátios superiores não são permeabilidade do solo. Índices legais e cômputo municipal dependem de consulta de viabilidade.',35)
note(430,155,'HIPÓTESES: frente 12 m; fundo 8 m; laterais 2 m. Norte adotado ao fundo. Seis vagas propostas: 4 residenciais e 2 comerciais. Validar demanda da Tabela 05 e trajetórias. Não há endereço nem zoneamento fornecidos.',35)
finish()
layout=frame(2,'PLANTA BAIXA COTADA E MOBILIADA • TÉRREO','1:100')
plot('terreo',40,-46,100);subtitle(35,377,'TÉRREO • NÍVEL ±0,00')
subtitle(300,365,'PROGRAMA COMERCIAL E CIRCULAÇÃO')
note(300,350,'Três lojas de 128,00 m² brutos, com entrada independente, salão flexível, copa e dois sanitários separados por sexo. Módulo de cada loja: 5,333 x 24,00 m. Faixa posterior: hall, escada, reserva de elevador e apoios. Acesso residencial pela lateral oeste, sem atravessar as lojas.',57)
subtitle(300,285,'LEGENDA / ESQUADRIAS')
for j,s in enumerate(['P1: porta dupla comercial 1,60 x 2,70 m','P2: acesso residencial 1,30 x 2,40 m','P3: porta 0,90 x 2,10 m','P4: porta interna 0,80 x 2,10 m','V1: vitrine 1,10 x 2,70 m','J1: janela 2,20 x 1,50 m / peitoril 0,90 m','J2: cozinha 1,40 x 1,40 m / peitoril 1,10 m','J3: pano 5,00 x 1,20 m / peitoril variável','J4: banho 1,20 x 0,80 m / peitoril 1,50 m','J5: sala 3,60 x 1,90 m / peitoril 0,75 m']):txt(300,270-j*9,s+f' | qtd {quant_esq.get(s.split(":")[0],0)}',9)
note(300,170,'Portas com folha, batente e arco de abertura; janelas com marco, vidro e montante. Cotas em metros. Paredes externas/divisórias: 0,15 m indicativos. Não confundir dimensões modulares com vãos úteis.',57)
note(300,115,'*Sanitários comerciais: detalhe preliminar na prancha 07. A sobreposição do círculo de giro com peças deve ser avaliada conforme os critérios de aproximação e transferência da NBR 9050. Acessibilidade integral não está certificada.',57)
finish()
layout=frame(3,'PLANTA BAIXA COTADA E MOBILIADA • SUPERIOR','1:100')
plot('superior',40,-46,100);subtitle(35,377,'SUPERIOR • NÍVEL +4,20')
subtitle(300,365,'QUATRO APARTAMENTOS FAMILIARES')
note(300,350,'Cada unidade ocupa módulo de 7,00 x 12,00 m: 72,45 m² brutos cobertos e 11,55 m² de pátio descoberto. Estar/jantar, dois quartos, cozinha/serviço, banheiro e circulação. Quartos com janelas laterais; cozinha e banheiro voltados a pátio aberto à cobertura.',57)
subtitle(300,270,'MÓDULOS DE AMBIENTES / POR UNIDADE')
for j,s in enumerate(['Estar/jantar: 7,00 x 4,00 = 28,00 m²','Quarto 1: 3,10 x 4,00 = 12,40 m²','Quarto 2: 3,10 x 4,00 = 12,40 m²','Cozinha/serviço: 2,75 x 2,30 = 6,325 m²','Banho: 2,75 x 1,50 = 4,125 m²','Circulação: 1,15 x 8,00 = 9,20 m²','Pátio aberto: 2,75 x 4,20 = 11,55 m²']):txt(300,255-j*9,s,9)
note(300,170,'Módulos não descontam paredes. Circulação coletiva nominal de 2,00 m; livre indicativa de 1,85 m entre faces. Portas de entrada com 0,90 m. Reserva de elevador não substitui projeto de acessibilidade e seleção de equipamento.',57)
note(300,110,'Pátios: dimensão livre proposta de 2,60 x 4,05 m (10,53 m²), comparada ao art. 27 do Código transcrito. Conferir razões de aberturas e confirmação legal. Prever impermeabilização, ralo e manutenção. A reformulação reduz a área coberta anterior para 913,80 m²; construída com pátios: 960 m².',57)
finish()
layout=frame(4,'CORTES LONGITUDINAL B–B E TRANSVERSAL A–A','1:100')
plot('corte_b',35,240,100);subtitle(35,345,'B–B • LONGITUDINAL / X=8,80 m')
plot('corte_a',35,95,100);subtitle(35,200,'A–A • TRANSVERSAL / Y=27,00 m')
note(410,330,'NÍVEIS: térreo ±0,00; superior +4,20; cobertura +7,20; platibanda +8,10. Laje intermediária 20 cm; cobertura 15 cm. Pés-direitos antes de forros: 4,00 m e 2,85 m.',36)
note(410,250,'As seções usam a posição real das paredes e aberturas do modelo. A escada aparece em projeção no corte B, pois o plano passa entre os lances. Ver desenvolvimento na prancha 06.',36)
note(250,170,'SISTEMA CONSTRUTIVO PROPOSTO: estrutura de concreto armado a dimensionar, alvenaria de vedação e cobertura leve termoacústica protegida por platibanda. Não foram dimensionados pilares, vigas, fundações ou armações.',66)
finish()
layout=frame(5,'FACHADAS FRONTAL, POSTERIOR, OESTE E LESTE','1:100')
plot('frontal',35,270,100);subtitle(35,365,'FRONTAL / TESTADA')
plot('posterior',315,270,100);subtitle(315,365,'POSTERIOR')
plot('oeste',35,165,100);subtitle(35,255,'LATERAL OESTE / ACESSO RESIDENCIAL')
plot('leste',35,60,100);subtitle(35,150,'LATERAL LESTE')
note(405,215,'ACABAMENTOS: pintura clara, caixilhos em alumínio grafite, vidros a especificar, portas comerciais com painéis laterais envidraçados. Prever sombreamento conforme orientação real.',32)
note(405,120,'As aberturas destas fachadas são obtidas da mesma geometria das plantas e do modelo 3D. Alturas e peitoris constam na legenda de esquadrias.',32)
finish()
layout=frame(6,'DETALHES DE ESCADA, PORTA, JANELA E IMPERMEABILIZAÇÃO','1:25 / 1:20 / 1:50')
plot('det_escada',55,120,25);subtitle(35,365,'ESCADA EM U • 1:25')
plot('det_porta',350,100,20);subtitle(350,365,'PORTA P3 • 1:20')
plot('det_janela',470,100,25);subtitle(475,365,'JANELA J1 • 1:25')
plot('det_construtivo',45,300,50);subtitle(130,345,'RUFO / IMPERMEABILIZAÇÃO • 1:50')
note(35,90,'Escada: 24 espelhos de 17,50 cm; piso 28 cm; 2e+p = 63,00 cm. Lances de 1,20 m e patamar de 1,20 m. Corrimãos em duas alturas e guarda-corpo a detalhar conforme norma aplicável. Verificar altura livre e exigência de escada protegida.',75)
note(350,70,'Detalhes de batentes, folhas, marcos e peitoril. Cotas gerais em metros. Rufo e impermeabilização são esquemas construtivos, sem especificação executiva.',60)
finish()
layout=frame(7,'APARTAMENTO AMPLIADO E SANITÁRIO COMERCIAL','1:50 / 1:25')
# use exact apartment subset of upper-floor drawing, with full wall details and furniture
full=drawings['superior'];items=full['items'];subset=[]
for it in items:
 if it[0]=='line':
  if all(1.9<=it[i]<=9.2 for i in [1,3]) and all(11.7<=it[i]<=24.2 for i in [2,4]):subset.append(it)
 elif it[0] in ['circle','arc','text'] and 1.9<=it[1]<=9.2 and 11.7<=it[2]<=24.2:subset.append(it)
drawings['apto_ampliado']={'items':subset,'offset':140}
plot('apto_ampliado',0,-160,50);subtitle(35,365,'APARTAMENTO 01 • 1:50')
plot('det_sanitario',350,150,25);subtitle(340,365,'SANITÁRIO COMERCIAL • 1:25')
note(290,100,'A disposição de mobiliário permite leitura do uso e circulação. As portas internas com 0,80 m são dimensões nominais de estudo. Para unidades acessíveis/adaptáveis, conferir vãos livres, áreas de manobra, aproximações, soleiras e instalações. O sanitário comercial tem porta abrindo para fora no detalhe; sua planta geral deve ser lida em conjunto com esta ampliação.',81)
finish()
# sheet 08 is composited with model views after rendering; placeholder replaced by function below.
layout=frame(8,'VISTAS 3D E SÍNTESE DO PARTIDO','VISTAS SEM ESCALA')
for path,x,y,w,h in [(R/'previas/perspectiva_revisada.png',20,205,340,175),(R/'previas/axon_superior.png',20,50,340,150)]:
 if path.exists():
  C.drawImage(str(path),x*mm,y*mm,width=w*mm,height=h*mm,preserveAspectRatio=True,anchor='c')
  dw=min(w,h*1800/1300);dh=dw*1300/1800
  image_def=D.add_image_def(filename='../previas/'+path.name,size_in_pixel=(1800,1300))
  layout.add_image(image_def,insert=(x+(w-dw)/2,y+(h-dh)/2),size_in_units=(dw,dh))
 else:txt(x,y+h/2,'VISTA EM PROCESSAMENTO — REGERAR APÓS MODELO 3D',9)
subtitle(390,360,'PARTIDO ARQUITETÔNICO')
note(390,345,'Comércio no térreo e habitação no superior, com acesso residencial separado. Quatro unidades familiares de dois quartos, pátios de iluminação e circulação coletiva posterior. A maquete possui paredes com vãos reais, folhas, caixilhos, vidro, lajes, escada e cobertura com aberturas sobre os pátios.',40)
note(390,235,'ARQUIVOS EDITÁVEIS: DXF 2D com layouts A2; DXF 3D de faces; modelo Blender e OBJ. O DXF 3D é malha editável, não sólido paramétrico BIM.',40)
note(390,160,'VERIFICAÇÃO LEGAL: lote hipotético sem zona urbanística identificada. Parâmetros municipais e atendimento normativo ainda dependem de consulta e revisão técnica. Este estudo não certifica conformidade nem autoriza execução.',40)
finish();C.save()
# Save modelspace plus eight paper layouts; modelspace contains native door/window geometry.
D.saveas(R/'cad/projeto_academico_2d.dxf')
audit=ezdxf.readfile(R/'cad/projeto_academico_2d.dxf').audit();assert not audit.errors
print('Pranchas A2 e DXF 2D gerados; paredes:',len(walls),'pátios:',len(patios),'erros:',len(audit.errors))
