from pathlib import Path
import json, math, hashlib
import ezdxf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
ROOT=Path(__file__).resolve().parents[1]
doc=ezdxf.new('R2010'); doc.units=6
for name,color in [('PAREDES',7),('COTAS',2),('TEXTOS',3),('ESQUADRIAS',4),('TERRENO',5),('MOBILIARIO',8)]: doc.layers.new(name,dxfattribs={'color':color})
msp=doc.modelspace(); pages=[]; ax=None; offset=0

def line(x1,y1,x2,y2,layer='PAREDES'):
 msp.add_line((x1+offset,y1),(x2+offset,y2),dxfattribs={'layer':layer})
 ax.plot([x1,x2],[y1,y2],color={'COTAS':'#8b6508','TERRENO':'#347346','ESQUADRIAS':'#167caa','MOBILIARIO':'#999999'}.get(layer,'#222222'),lw=.65)
def rect(x,y,w,h,layer='PAREDES'):
 for a,b,c,d in [(x,y,x+w,y),(x+w,y,x+w,y+h),(x+w,y+h,x,y+h),(x,y+h,x,y)]:line(a,b,c,d,layer)
def text(x,y,s,size=.24):
 for i,t in enumerate(s.split('\n')):
  msp.add_text(t,dxfattribs={'height':size,'insert':(x+offset,y-i*size*1.5),'layer':'TEXTOS'})
 ax.text(x,y,s,fontsize=max(5.5,size*20),va='top',ha='left')
def dim(x1,y1,x2,y2,distance):
 # Native DXF dimension, metres, decimal comma on printed annotation.
 d=msp.add_aligned_dim((x1+offset,y1),(x2+offset,y2),distance=distance,dimstyle='EZDXF',override={'dimtxt':.22,'dimasz':.16,'dimdec':2,'dimtad':1,'dimclrd':2,'dimclre':2,'dimclrt':2},dxfattribs={'layer':'COTAS'}); d.render()
 if abs(y2-y1)<.001:
  yy=y1+distance;line(x1,yy,x2,yy,'COTAS');text((x1+x2)/2,yy+.3,f'{abs(x2-x1):.2f} m',.22)
 else:
  xx=x1-distance;line(xx,y1,xx,y2,'COTAS');text(xx+.1,(y1+y2)/2,f'{abs(y2-y1):.2f} m',.22)
def door(x,y,w= .9):
 line(x,y,x,y+w,'ESQUADRIAS');line(x,y+w,x+w,y,'ESQUADRIAS')
 # symbolic swing arc
 import numpy as np
 ts=np.linspace(0,math.pi/2,16)
 pts=[(x+w*math.cos(t)+offset,y+w*math.sin(t)) for t in ts]
 msp.add_lwpolyline(pts,dxfattribs={'layer':'ESQUADRIAS'})
 ax.plot([p[0]-offset for p in pts],[p[1] for p in pts],color='#167caa',lw=.5)
def window(x,y,w):
 line(x,y,x+w,y,'ESQUADRIAS');line(x,y+.08,x+w,y+.08,'ESQUADRIAS')
def begin(title,off,limits=(-4,26,-4,55)):
 global ax,offset
 offset=off; fig,ax=plt.subplots(figsize=(11.69,16.54));ax.set_aspect('equal');ax.set_xlim(limits[:2]);ax.set_ylim(limits[2:]);ax.axis('off');ax.set_title(title,fontsize=14,pad=18)
 fig.text(.08,.035,'ESTUDO CONCEITUAL • DOURADOS/MS • unidades: metro\nNão executivo. Recuos, acessibilidade, incêndio e estrutura sujeitos a projeto e aprovação.',fontsize=8)
 pages.append((title,fig))
def shell(upper=False):
 # 15 cm schematic external walls with explicit openings on front/rear
 for x in [2,2.15,17.85,18]:
  gaps=[(35,36.2)] if x<3 and not upper else []
  if upper: gaps=[(v+5,v+6.5) for v in [10,22]]+[(v+9,v+10.5) for v in [10,22]]
  pos=10
  for a,b in sorted(gaps):
   line(x,pos,x,a);pos=b
  line(x,pos,x,40)
 for y in [10,10.15,39.85,40]:
  if y<11 and not upper:
   pos=2
   for i in range(3):
    a=2+i*16/3+.8;b=a+3.8
    line(pos,y,a,y);pos=b
   line(pos,y,18,y)
  else:
   line(2,y,3,y);line(8,y,12,y);line(17,y,18,y)
 window(3,40,5);window(12,40,5)
def stair():
 rect(7,35,6,4.5);rect(7.2,35.2,1.2,3);rect(9.6,35.2,1.2,3)
 for i in range(11):
  line(7.2,35.2+i*.28,8.4,35.2+i*.28);line(9.6,35.2+i*.28,10.8,35.2+i*.28)
 text(7.2,39.4,'ESCADA EM U / reserva 6 x 4,5\n22 espelhos de 0,164 m; piso 0,28\nlances 1,20 m; conferir patamares',.18)
 text(3,38,'HALL / APOIO',.25);text(13.2,37,'RESERVA\nELEVADOR\n2 x 2 m',.2);rect(14,34.8,2,2)

begin('01 • IMPLANTAÇÃO / COBERTURA • escala gráfica em metros',0)
rect(0,0,20,50,'TERRENO');rect(2,10,16,30);text(4,26,'PROJEÇÃO EDIFÍCIO\n16,00 x 30,00 m\n480,00 m² / pavimento',.32)
line(2,25,18,25,'ESQUADRIAS');text(3,33,'COBERTURA LEVE • inclinação a definir\nCalhas e condutores em projeto complementar',.22)
text(3,48,'FUNDO LIVRE / ÁREA PERMEÁVEL PROPOSTA\n10,00 m de profundidade',.23)
text(.1,32,'ACESSO',.18);text(18.2,32,'FAIXA\nLIVRE\n2 m',.18)
for x,w,label in [(2,3.5,'PCD'),(7,2.5,'V2'),(9.5,2.5,'V3')]:rect(x,2,w,5,'MOBILIARIO');text(x+.2,5,label,.24)
rect(5.5,2,1.2,5,'ESQUADRIAS');text(12.4,5,'ACESSO LOJAS\nPÁTIO FRONTAL\nMANOBRAS A ESTUDAR',.2)
text(2.2,15,'ACESSO RESIDENCIAL\npela lateral oeste até hall posterior',.19)
text(1,-1,'RUA / TESTADA 20,00 m • posição hipotética');line(21,43,21,48,'TERRENO');text(20.5,49,'N*',.35)
dim(0,0,20,0,-1.7);dim(0,0,0,50,2);dim(2,10,18,10,-1);text(2,52,'*Norte assumido ao fundo; confirmar levantamento.',.22)

begin('02 • PLANTA TÉRREO • 3 lojas + acesso independente',65)
rect(0,0,20,50,'TERRENO');shell()
for x in [2+16/3,2+32/3]:
 line(x,10,x,34);line(x+.15,10,x+.15,34)
# rear wall shop openings into no shared route: continuous partition
line(2,34,18,34);line(2,34.15,18,34.15)
for i in range(3):
 x=2+i*16/3
 text(x+.4,22,f'LOJA 0{i+1}\n128,00 m² brutos\nSalão flexível',.27)
 # WC reserve: 2.2 x 2.4 at back, opening .90 in front partition
 line(x+.25,31.45,x+.25,33.85);line(x+.25,33.85,x+2.45,33.85);line(x+2.45,33.85,x+2.45,31.45)
 line(x+.25,31.45,x+.5,31.45);line(x+1.4,31.45,x+2.45,31.45);door(x+.5,31.45,.9);text(x+.4,33.4,'SANIT.\n2,20 x 2,40',.18)
 # erase-free explicit door gap on new partition represented by doorway white mask in print only avoided: lines rebuilt below
 window(x+.8,10,3.8);text(x+.7,9.4,'VITRINE / ENTRADA',.17)
 text(x+2.8,32.8,'COPA\nreserva',.18);rect(x+2.8,31.6,1.7,.6,'MOBILIARIO')
# independent rear entry through west wall opening symbolic labelled
text(.1,36,'ENTRADA\nRESIDENCIAL',.18);door(2,35,1.2);stair()
dim(2,7,18,7,-1);dim(18,10,18,34,-1);dim(18,34,18,40,-1)
for i in range(3):dim(2+i*16/3,10,2+(i+1)*16/3,10,-1)
line(0,25,20,25,'COTAS');text(0,26,'A',.3);text(19,26,'A',.3);line(10,8,10,42,'COTAS');text(10.2,42,'B',.3)
text(2,45,'Paredes esquemáticas 0,15 m; áreas são brutas.\nSanitários reservados; detalhar giro, barras e portas acessíveis.\nVitrines: módulos de 3,80 m com porta incorporada a detalhar.',.23)

begin('03 • PLANTA SUPERIOR • 4 apartamentos familiares',130)
shell(upper=True)
# corridor and unit divides with entry openings 0.9
for x in [9,11]:
 for a,b in [(10,11),(11.9,23),(23.9,34)]:line(x,a,x,b);line(x+.15,a,x+.15,b)
line(2,22,9,22);line(11,22,18,22);line(2,34,9,34);line(11,34,18,34)
for n,(x,y) in enumerate([(2,10),(11,10),(2,22),(11,22)],1):
 text(x+.25,y+3.3,f'APTO {n:02d} • 84 m² brutos\nESTAR / JANTAR 7 x 4',.23)
 # Two bedrooms arranged along the external side, each with its own window.
 def lx(u):return x+u if x==2 else x+7-u
 def ll(u,v,u2,v2,layer='PAREDES'):line(lx(u),y+v,lx(u2),y+v2,layer)
 def rr(u,v,w,h):rect(min(lx(u),lx(u+w)),y+v,w,h,'MOBILIARIO')
 def tt(u,v,s):text(min(lx(u),lx(u+2.5)),y+v,s,.19)
 ll(0,4,3.5,4);ll(4.5,4,7,4)
 ll(0,8,3.5,8)
 for aa,bb in [(4,5),(5.9,9),(9.9,12)]:ll(3.5,aa,3.5,bb)
 for aa,bb in [(4,4.8),(5.7,7.5),(8.4,10),(10.9,12)]:ll(4.5,aa,4.5,bb)
 ll(4.5,7,7,7);ll(4.5,9.4,7,9.4)
 tt(.3,6.9,'QUARTO 1\n3,50 x 4,00')
 tt(.3,10.9,'QUARTO 2\n3,50 x 4,00')
 tt(4.6,6.5,'COZINHA\n2,50 x 3,00')
 tt(4.6,8.9,'BANHO\n2,50 x 2,40')
 tt(4.6,11.4,'SERVIÇO\n2,50 x 2,60')
 tt(3.6,11.9,'CIRC. 1 m')
 rr(.5,4.5,1.4,2);rr(.5,8.5,1.4,2);rr(6.3,4.2,.6,2.5)
 for vv in [5,9]:
  ll(0,vv,0,vv+1.5,'ESQUADRIAS')
 for u,v in [(3.5,5),(3.5,9),(4.5,4.8),(4.5,7.5),(4.5,10)]:
  ll(u,v,u+.8,v,'ESQUADRIAS')
 # Exhaust riser reservation, without assuming legal acceptance of mechanical ventilation.
 rr(6.5,8.9,.4,.4);tt(5,11.9,'DUTO*')
 door(9 if x==2 else 11,y+1,.9)
text(9.35,30,'CIRC.\n2 m',.2);stair()
dim(2,10,9,10,-1.2);dim(9,10,11,10,-1.2);dim(11,10,18,10,-1.2);dim(18,10,18,22,-1.5);dim(18,22,18,34,-1.5)
text(2,47,'Ambientes dimensionados por módulos entre eixos/limites brutos.\nÁreas úteis menores após paredes; *Banhos/cozinhas/serviço: exaustão a dimensionar e aprovar.\nAptos 01/02 voltados à frente; 03/04 ao fundo/laterais.',.23)

begin('04 • CORTES A–A / B–B • esquema construtivo',195,(-3,36,-6,26))
for yy in [0,3.45,3.6,6.45,6.6]:line(0,yy,16,yy)
for xx in [0,5.33,10.67,16]:line(xx,0,xx,3.45)
for xx in [0,7,9,16]:line(xx,3.6,xx,6.45)
rect(0,6.6,16,.9);line(0,7,8,7.25);line(8,7.25,16,7)
text(1,2,'LOJAS • pé-direito conceitual 3,45 m',.25);text(1,5.8,'APARTAMENTOS • pé-direito 2,85 m',.25)
text(0,-1,'A–A TRANSVERSAL • passagem pelo meio do lote');dim(0,0,16,0,-2);dim(16,0,16,3.6,-1.5);dim(16,3.6,16,6.6,-1.5)
for yy in [12,15.45,15.6,18.45,18.6]:line(0,yy,30,yy)
for xx in [0,24,30]:line(xx,12,xx,18.6)
line(24,12,27,15.6);line(27,15.6,30,15.6);rect(0,18.6,30,.9)
text(1,14,'SALÕES COMERCIAIS',.25);text(1,17,'UNIDADES / CIRCULAÇÃO',.25);text(24.3,14,'HALL\nESCADA',.22)
text(0,11,'B–B LONGITUDINAL • esquema pelo núcleo posterior');dim(0,12,30,12,-2)
text(0,23,'Níveis: térreo ±0,00 | superior +3,60 | cobertura +6,60 | platibanda +7,50\nLajes 0,15 m indicativas; fundações e estrutura não dimensionadas.',.27)

begin('05 • FACHADAS • frontal e lateral oeste',260,(-3,36,-6,26))
rect(0,0,16,7.5);line(0,3.6,16,3.6);line(0,6.6,16,6.6)
for i in range(3):rect(i*16/3+.7,0,3.8,2.7,'ESQUADRIAS');text(i*16/3+1,3.2,f'LOJA {i+1}',.22)
for x in [1,5,10,14]:rect(x,4.5,1.2,1.2,'ESQUADRIAS')
text(0,-1,'FACHADA FRONTAL • marquise a estudar sem avanço assumido');dim(0,0,16,0,-2)
rect(0,12,30,7.5);line(0,15.6,30,15.6);line(0,18.6,30,18.6)
for x in [1,5,9,13,17,21]:rect(x,16.5,1.3,1.2,'ESQUADRIAS')
rect(25,12,1.2,2.4,'ESQUADRIAS');text(24,11.6,'ENTRADA RESIDENCIAL',.2)
text(0,10,'FACHADA LATERAL OESTE • leste semelhante, sem acesso');text(0,23,'Paleta conceitual: reboco claro, caixilhos metálicos e proteção solar externa.\nFachada posterior: janelas do hall e núcleo de circulação; ver prancha 06.',.26)

begin('06 • FACHADA POSTERIOR / QUADRO DE ÁREAS',325,(-3,25,-8,30))
rect(0,0,16,7.5);line(0,3.6,16,3.6);line(0,6.6,16,6.6)
for y in [1.2,4.8]:
 for x in [1,11]:rect(x,y,4,1.2,'ESQUADRIAS')
text(0,-1,'FACHADA POSTERIOR • vista do fundo');dim(0,0,16,0,-2)
rows=['TERRENO: 20 x 50 = 1.000,00 m²','PROJEÇÃO: 16 x 30 = 480,00 m²','TÉRREO: 3 lojas x 128 = 384,00 m²','TÉRREO: hall / núcleo / apoio = 96,00 m²','SUPERIOR: 4 aptos x 84 = 336,00 m²','SUPERIOR: corredor 2 x 24 = 48,00 m²','SUPERIOR: hall / núcleo = 96,00 m²','ÁREA CONSTRUÍDA CONCEITUAL: 960,00 m²','ÁREA LIVRE: 520,00 m² | ocupação: 48%','COEFICIENTE GEOMÉTRICO: 0,96','PERMEÁVEL PROPOSTA: 240,00 m² (24%)']
for i,r in enumerate(rows):text(0,27-i*1.25,r,.29)
text(0,-4,'Áreas brutas, incluem paredes; não equivalem a áreas legais aprovadas.\nPermeabilidade: fundo 200 m² + faixa lateral leste nos 20 m finais (40 m²).\nRecuos adotados: frente/fundo 10 m; laterais 2 m. Confirmar legislação.',.24)

out=ROOT/'cad/estudo_misto_dourados.dxf';doc.saveas(out)
with PdfPages(ROOT/'pranchas/projeto_conceitual.pdf') as pdf:
 for i,(title,fig) in enumerate(pages,1):
  pdf.savefig(fig);fig.savefig(ROOT/f'pranchas/{i:02d}.svg');plt.close(fig)
areas={'terreno_m2':1000,'projecao_m2':480,'terreo_m2':480,'superior_m2':480,'total_construido_m2':960,'lojas_m2':[128]*3,'apartamentos_m2':[84]*4,'comum_terreo_m2':96,'comum_superior_m2':144,'livre_m2':520,'permeavel_proposta_m2':240}
(ROOT/'documentacao/areas.json').write_text(json.dumps(areas,indent=2),encoding='utf-8')
loaded=ezdxf.readfile(out);audit=loaded.audit()
assert not audit.errors, str(audit.errors)
assert sum(areas['lojas_m2'])+96==480
assert sum(areas['apartamentos_m2'])+144==480
assert 480*2==960 and 480+520==1000
report={'dxf_reaberto':True,'erros_auditoria_dxf':len(audit.errors),'correcoes_auditoria':len(audit.fixes),'entidades_modelspace':len(loaded.modelspace()),'cotas_nativas':len(loaded.modelspace().query('DIMENSION')),'pranchas':len(pages),'consistencia_areas':'OK','unidade_dxf':'metro (INSUNITS=6)'}
(ROOT/'verificacao/relatorio.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
