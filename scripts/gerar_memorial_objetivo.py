from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,KeepTogether,Image
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
R=Path(__file__).resolve().parents[1]/'revisao_02'
navy=colors.HexColor('#17384c');muted=colors.HexColor('#536674');light=colors.HexColor('#edf3f6')
body=ParagraphStyle('Body',fontName='Helvetica',fontSize=9.2,leading=13.4,textColor=colors.HexColor('#253540'),spaceAfter=7)
head=ParagraphStyle('Heading',parent=body,fontName='Helvetica-Bold',fontSize=11,leading=15,textColor=navy,spaceBefore=9,spaceAfter=7,keepWithNext=True)
small=ParagraphStyle('Small',parent=body,fontSize=8.3,leading=11)
cell=ParagraphStyle('Cell',parent=body,fontSize=8.8,leading=11,spaceAfter=0)
blocks=(R/'documentacao/memorial_descritivo.md').read_text().split('\n\n')
story=[]
# Logo fornecida pelo aluno; preservar proporção e arquivo original.
from reportlab.lib.utils import ImageReader
logo_path=R/'documentacao/identidade/logo_unigran.png'
logo_w,logo_h=ImageReader(str(logo_path)).getSize()
logo=Image(str(logo_path),width=48*mm,height=48*mm*logo_h/logo_w);logo.hAlign='LEFT'
story.extend([logo,Spacer(1,7)])
story.append(Paragraph('ENGENHARIA CIVIL  |  PROVA DE DESENHO TÉCNICO',small));story.append(Spacer(1,6))
story.append(Paragraph('MEMORIAL DESCRITIVO',ParagraphStyle('Title',fontName='Helvetica-Bold',fontSize=22,leading=26,textColor=navy)))
story.append(Paragraph('Edificação de uso misto · Dourados–MS',ParagraphStyle('Subtitle',parent=body,fontSize=11,leading=16,textColor=muted)))
card=Table([[Paragraph('<b>Aluno:</b> Icaro Gamarra Silva<br/><b>RGM:</b> 3322.527',small),Paragraph('<b>Professora:</b> Rafaella Scalon<br/><b>Entrega:</b> 28/10/2026',small)]],colWidths=[85*mm,85*mm]);card.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),light),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),10),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),5)]));story.extend([card,Spacer(1,5)])
for part in blocks[2:]:
 part=part.strip()
 if not part:continue
 if part.startswith('## 4.'):
  story.append(PageBreak());story.append(Paragraph('SOLUÇÕES CONSTRUTIVAS E ÁREAS',ParagraphStyle('Page2',parent=head,fontSize=14,leading=19,spaceBefore=0,spaceAfter=8)))
 if part.startswith('## '):story.append(Paragraph(escape(part[3:]),head))
 elif part.startswith('|'):
  rows=[]
  for line in part.splitlines():
   cells=[t.strip() for t in line.strip('|').split('|')]
   if all(set(t)<=set('-: ') for t in cells):continue
   rows.append([Paragraph(escape(t),cell) for t in cells])
  whitecell=ParagraphStyle('WhiteCell',parent=cell,textColor=colors.white,fontName='Helvetica-Bold')
  rows[0]=[Paragraph('Componente',whitecell),Paragraph('Área',whitecell)]
  t=Table(rows,colWidths=[125*mm,45*mm]);t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),navy),('TEXTCOLOR',(0,0),(-1,0),colors.white),('ROWBACKGROUNDS',(0,1),(-1,-1),[light,colors.white]),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),('LINEBELOW',(0,0),(-1,0),.6,navy)]))
  story.extend([t,Spacer(1,7)])
 else:story.append(Paragraph(escape(part.replace('\n',' ')),body))
def footer(c,doc):
 w,h=A4;c.setStrokeColor(navy);c.setLineWidth(.6);c.line(20*mm,16*mm,w-20*mm,16*mm)
 c.setFont('Helvetica',7.3);c.setFillColor(muted);c.drawString(20*mm,11.8*mm,'Icaro Gamarra Silva · RGM 3322.527 | Projeto acadêmico · REV02')
 c.drawRightString(w-20*mm,11.8*mm,f'{doc.page}')
SimpleDocTemplate(str(R/'documentacao/memorial_descritivo.pdf'),pagesize=A4,leftMargin=20*mm,rightMargin=20*mm,topMargin=17*mm,bottomMargin=22*mm,title='Memorial descritivo - Icaro Gamarra Silva - UNIGRAN',author='Icaro Gamarra Silva').build(story,onFirstPage=footer,onLaterPages=footer)
print('Memorial objetivo gerado')
