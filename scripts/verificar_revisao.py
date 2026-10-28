from pathlib import Path
import json,math,hashlib,zipfile
import ezdxf,fitz
R=Path(__file__).resolve().parents[1]/'revisao_02'
# Export the full OBJ as CAD faces; no dependency on Blender Python packages.
vertices=[];faces=[]
for l in (R/'modelo_3d/projeto_Icaro.obj').read_text().splitlines():
 if l.startswith('v '):
  # Blender OBJ defaults to Y up / -Z forward; CAD uses Z up.
  ox,oy,oz=map(float,l.split()[1:4]);vertices.append((ox,-oz,oy))
 if l.startswith('f '):
  f=[]
  for v in l.split()[1:]:
   i=int(v.split('/')[0]);f.append(i-1 if i>0 else len(vertices)+i)
  faces.append(f)
assert vertices and faces
D=ezdxf.new('R2010');D.units=6;D.layers.new('MODELO_3D',dxfattribs={'color':7});M=D.modelspace()
for f in faces:
 pts=[vertices[i] for i in f]
 if len(pts)<=4:M.add_3dface(pts,dxfattribs={'layer':'MODELO_3D'})
 else:
  for i in range(1,len(pts)-1):M.add_3dface([pts[0],pts[i],pts[i+1]],dxfattribs={'layer':'MODELO_3D'})
D.saveas(R/'cad/projeto_academico_3d.dxf')
report={}
for n in ['projeto_academico_2d','projeto_academico_3d']:
 d=ezdxf.readfile(R/f'cad/{n}.dxf');a=d.audit();assert not a.errors and not a.fixes
 assert d.units==6
 report[n]={'erros_auditoria':len(a.errors),'correcoes_auditoria':len(a.fixes),'entidades':len(d.modelspace()),'layouts':len(d.layouts)}
 if n.endswith('2d'):
  assert len(d.layouts)==10 # model + default Layout1 + eight named academic sheets
  assert len(d.modelspace().query('ARC'))>=35
  assert len(d.modelspace().query('DIMENSION'))>50
  report[n]['cotas_nativas']=len(d.modelspace().query('DIMENSION'));report[n]['arcos_abertura']=len(d.modelspace().query('ARC'))
  assert len([l for l in d.layouts if l.name[:2].isdigit()])==8
 else:
  assert len(d.modelspace().query('3DFACE'))>2500
  zs=[v[2] for v in vertices];assert min(zs)<0 and max(zs)>=8.09
  report[n]['altura_maxima_m']=round(max(zs),3)
a=json.loads((R/'documentacao/areas.json').read_text());assert math.isclose(3*a['loja_bruta_m2']+96,480)
assert math.isclose(4*a['apartamento_coberto_bruto_m2']+144,a['superior_coberto_m2'])
assert math.isclose(a['total_coberto_m2']+a['patios_superiores_descobertos_m2'],960)
assert math.isclose(a['total_coberto_m2'],480+a['superior_coberto_m2'])
g=json.loads((R/'modelo_3d/projeto_geometria.json').read_text());assert len(g['patios'])==4
assert all(math.isclose(w*h,11.55) and (w-.15)*(h-.15)>=10 for x,y,w,h in g['patios'])
assert all(w['height']==4 for w in g['walls'] if w['z']==0)
assert sum(1 for w in g['walls'] if w['name']=='WC frente')==6
assert all(o[1]>=1.5 for w in g['walls'] for o in w['openings'] if o[5]=='P1')
assert .62<=2*(4.2/24)+.28<=.64
# Conservative nominal-room checks with 70% effective window opening specification.
checks={'quarto':(2.2*1.5*.7,12.4/6),'sala':(3.6*1.9*.7,28/6),'cozinha':(1.4*1.4*.7,6.325/6),'banho':(1.2*.8*.7,4.125/8)}
assert all(actual>=required for actual,required in checks.values())
report['comparacoes_codigo_transcrito']={'espelho_m':4.2/24,'blondel_m':2*(4.2/24)+.28,'patio_livre_estimado_m2':(2.75-.15)*(4.2-.15),'aberturas_70pct':checks,'seis_sanitarios_comerciais':True}
p=fitz.open(R/'pranchas/projeto_academico_Icaro.pdf');assert len(p)==8
for i,page in enumerate(p):
 assert abs(page.rect.width/72*25.4-594)<.01 and abs(page.rect.height/72*25.4-420)<.01
 t=page.get_text();assert 'Icaro Gamarra Silva' in t and 'Rafaella Scalon' in t and '3322.527' in t
 assert 'EM PROCESSAMENTO' not in t
 assert len(t)>500
# Confirm two actual embedded renders, not text placeholders.
assert len(p[7].get_images())==2
report['pdf']={'pranchas':8,'formato':'A2 paisagem','carimbos_conferidos':8,'vistas_3d_incorporadas':2}
for name in ['memorial_descritivo','referencias_legais','conferencia_enunciado']:
 q=fitz.open(R/f'documentacao/{name}.pdf');assert len(q)>0 and len(q[0].get_text())>200
 report[name]={'paginas':len(q)}
report['areas']=a;report['conformidade_integral_legal_ABNT']='NAO CERTIFICADA; ver referencias_legais.pdf'
(R/'verificacao/relatorio.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
# Per-sheet PDFs for submission systems with separate upload fields.
for i in range(8):
 q=fitz.open();q.insert_pdf(p,from_page=i,to_page=i);q.save(R/f'pranchas/{i+1:02d}.pdf');q.close()
# integrity hashes for all deliverables except self hash
files=[f for f in R.rglob('*') if f.is_file() and f.name!='SHA256SUMS.txt' and f.suffix not in ['.blend1']]
(R/'verificacao/SHA256SUMS.txt').write_text('\n'.join(hashlib.sha256(f.read_bytes()).hexdigest()+'  '+str(f.relative_to(R)) for f in sorted(files))+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
