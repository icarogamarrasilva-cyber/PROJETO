from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
import csv
r=Path(__file__).resolve().parents[1]
styles=getSampleStyleSheet();story=[]
for p in (r/'documentacao/memorial_descritivo.md').read_text().split('\n\n'):
 p=p.strip()
 if not p:continue
 style=styles['Title'] if p.startswith('# ') else styles['Heading2'] if p.startswith('## ') else styles['BodyText']
 story.append(Paragraph(escape(p.lstrip('# ').replace('\n',' ')),style));story.append(Spacer(1,8))
SimpleDocTemplate(str(r/'documentacao/memorial_descritivo.pdf'),pagesize=A4,rightMargin=42,leftMargin=42,topMargin=42,bottomMargin=42).build(story)
with (r/'documentacao/quadro_areas.csv').open('w',newline='') as f:
 w=csv.writer(f,delimiter=';');w.writerow(['Item','Quantidade','Area unitaria bruta m2','Area total m2'])
 w.writerows([['Terreno',1,1000,1000],['Loja',3,128,384],['Comum terreo',1,96,96],['Apartamento',4,84,336],['Corredor superior',1,48,48],['Hall/nucleo superior',1,96,96],['Total construido',1,960,960],['Area livre',1,520,520],['Permeavel proposta',1,240,240]])
print('Memorial PDF e CSV gerados')
