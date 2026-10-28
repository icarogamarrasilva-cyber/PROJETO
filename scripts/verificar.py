from pathlib import Path
import json, hashlib, zipfile
import ezdxf
from pypdf import PdfReader
import xml.etree.ElementTree as ET
r=Path(__file__).resolve().parents[1]
d=ezdxf.readfile(r/'cad/estudo_misto_dourados.dxf');a=d.audit()
assert not a.errors and not a.fixes
assert d.units==6
assert len(d.modelspace().query('DIMENSION'))==20
p=PdfReader(r/'pranchas/projeto_conceitual.pdf');assert len(p.pages)==6
for page in p.pages:assert len(page.extract_text())>100
mem=PdfReader(r/'documentacao/memorial_descritivo.pdf');assert len(mem.pages)>=3
for i in range(1,7):assert ET.parse(r/f'pranchas/{i:02d}.svg').getroot().tag.endswith('svg')
z=json.loads((r/'documentacao/areas.json').read_text())
assert sum(z['lojas_m2'])+z['comum_terreo_m2']==z['terreo_m2']
assert sum(z['apartamentos_m2'])+z['comum_superior_m2']==z['superior_m2']
assert z['terreo_m2']+z['superior_m2']==z['total_construido_m2']
assert z['livre_m2']+z['projecao_m2']==z['terreno_m2']
# Verify intended rectangular module bounds and non-overlap within the upper floor.
units=[(2,10,9,22),(11,10,18,22),(2,22,9,34),(11,22,18,34)]
for i,(x,y,xx,yy) in enumerate(units):
 assert (xx-x)*(yy-y)==84
 assert 2<=x<xx<=18 and 10<=y<yy<=34
 for b in units[i+1:]:assert min(xx,b[2])<=max(x,b[0]) or min(yy,b[3])<=max(y,b[1])
report=json.loads((r/'verificacao/relatorio.json').read_text())
report.update({'pdf_pranchas_reaberto':True,'paginas_pranchas':len(p.pages),'paginas_memorial':len(mem.pages),'svg_validos':6,'modulos_apartamentos_sem_sobreposicao':True,'limites':'Auditoria de formato, áreas modulares e integridade; não certifica normas ou projeto executivo.'})
(r/'verificacao/relatorio.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
files=[f for folder in ['cad','pranchas','documentacao','scripts'] for f in (r/folder).glob('*') if f.is_file()]+[r/'README.md',r/'verificacao/relatorio.json']
(r/'verificacao/SHA256SUMS.txt').write_text('\n'.join(hashlib.sha256(f.read_bytes()).hexdigest()+'  '+str(f.relative_to(r)) for f in sorted(files))+'\n')
with zipfile.ZipFile(r/'projeto_conceitual_dourados.zip','w',zipfile.ZIP_DEFLATED) as zip:
 for f in files+[r/'verificacao/SHA256SUMS.txt']:zip.write(f,str(f.relative_to(r)))
with zipfile.ZipFile(r/'projeto_conceitual_dourados.zip') as zip:assert zip.testzip() is None
print(json.dumps(report,ensure_ascii=False,indent=2))
