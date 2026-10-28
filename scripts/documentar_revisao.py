from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4,landscape
from reportlab.lib import colors
R=Path(__file__).resolve().parents[1]/'revisao_02';styles=getSampleStyleSheet()
for name in ['memorial_descritivo','referencias_legais','conferencia_enunciado']:
 s=(R/f'documentacao/{name}.md').read_text();story=[];land=name!='memorial_descritivo';pagesize=landscape(A4) if land else A4
 for part in s.split('\n\n'):
  part=part.strip()
  if not part:continue
  if part.startswith('|'):
   rows=[]
   for line in part.splitlines():
    cells=[v.strip() for v in line.strip('|').split('|')]
    if all(set(v)<=set('-: ') for v in cells):continue
    rows.append([Paragraph(escape(v.replace('**','')),styles['BodyText']) for v in cells])
   cols=len(rows[0]);available=pagesize[0]-72
   widths=[available*.24,available*.44,available*.32] if cols==3 else [available/cols]*cols
   t=Table(rows,colWidths=widths,repeatRows=1);t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e6edf1')),('GRID',(0,0),(-1,-1),.4,colors.grey),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5)]));story.append(t)
  else:
   style=styles['Title'] if part.startswith('# ') else styles['Heading2'] if part.startswith('## ') else styles['BodyText']
   story.append(Paragraph(escape(part.lstrip('# ').replace('**','').replace('\n',' ')),style))
  story.append(Spacer(1,9))
 def footer(c,doc):
  c.setFont('Helvetica',8);c.drawString(36,20,'Icaro Gamarra Silva | RGM 3322.527 | Rev.02');c.drawRightString(pagesize[0]-36,20,str(doc.page))
 SimpleDocTemplate(str(R/f'documentacao/{name}.pdf'),pagesize=pagesize,leftMargin=36,rightMargin=36,topMargin=36,bottomMargin=36).build(story,onFirstPage=footer,onLaterPages=footer)
 print(name,'PDF gerado')
