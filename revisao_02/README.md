# Projeto acadêmico — revisão 02

**Icaro Gamarra Silva — RGM 3322.527**  
Professora: Rafaella Scalon | Engenharia Civil | Prova de desenho técnico | Entrega: 28/10/2026.

## Abrir primeiro

1. `pranchas/projeto_academico_Icaro.pdf`: oito folhas A2 com carimbo, escalas, implantação, cobertura, plantas mobiliadas/cotadas, cortes, quatro fachadas, detalhes, apartamento ampliado e duas vistas 3D.
2. `documentacao/memorial_descritivo.pdf`: memorial objetivo em duas páginas A4, com logo UNIGRAN fornecida pelo aluno, dados acadêmicos e quadro de áreas.
3. `documentacao/referencias_legais.pdf`: análise da LUOS enviada e limitações de conformidade.
4. `documentacao/conferencia_enunciado.pdf`: relação entre requisitos e entregas.

## Arquivos editáveis

- `cad/projeto_academico_2d.dxf`: geometria 2D em metros e oito layouts A2 em milímetros.
- `cad/projeto_academico_3d.dxf`: geometria 3D em faces, em metros; usar vista isométrica e Zoom Extents. É malha, não sólido BIM paramétrico.
- `modelo_3d/projeto_Icaro.blend`: abrir no Blender 4.3 ou superior; coleções por setor permitem ocultar cobertura e pavimentos.
- `modelo_3d/projeto_Icaro.obj` + `.mtl`: intercâmbio 3D com materiais; manter os dois arquivos juntos.
- `previas/`: perspectivas em PNG.

PDF: imprimir em A2 paisagem, **tamanho real/100%**, sem ajustar à página. Plantas 1:100, implantação 1:150, apartamento 1:50, detalhes 1:25 e 1:20; vistas 3D sem escala. No DXF, cada desenho está separado no modelspace e organizado em layout próprio. O modelo 3D fica em arquivo separado para não sobrepor as plantas.

## O que mudou

Carimbo com os dados fornecidos, portas com batentes/folhas/arcos e janelas com marcos/montantes, mobiliário, cotas internas, pátios abertos, seis vagas propostas, oito pranchas em escala definida, duas vistas 3D e quadro de referências legais. Área coberta foi revisada para 913,80 m² cobertos (960 m² incluindo pátios) em razão dos pátios; não usar o quadro antigo de 960 m².

A revisão anterior na raiz do repositório permanece apenas como histórico. **Use exclusivamente esta pasta e o ZIP REV02 para avaliar a versão atual.**

## Situação legal

O lote é hipotético, por orientação do aluno. A LUOS fornecida foi consultada; o documento contém alterações e revogações e não permite certificar sozinho os parâmetros de 2026. O Código de Obras foi transcrito pelo aluno e aplicado a verificações pontuais; a tabela vigente de quantitativos de vagas não foi disponibilizada. Atendimento integral às normas e legislação **não certificado**. As entregas são acadêmicas e não executivas.

As imagens da folha 08 no DXF são referências a `../previas/*.png`; manter a estrutura de pastas ao extrair o pacote. Para iniciar o 3D em CAD, escolher vista isométrica e Zoom Extents. O arquivo Blender preserva o modelo completo com cobertura; a vista de planta humanizada foi renderizada ocultando a cobertura e cortando paredes apenas para apresentação.
