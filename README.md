# Projeto arquitetônico acadêmico — Icaro Gamarra Silva

**Versão atual: revisão 02**, com carimbo do aluno e professora, plantas mobiliadas/cotadas, detalhes de portas/janelas, cortes, quatro fachadas e vistas/modelo 3D.

- [Baixar pacote REV02](PROJETO_ICARO_REV02.zip)
- [Abrir as oito pranchas A2 em PDF](revisao_02/pranchas/projeto_academico_Icaro.pdf)
- [Memorial descritivo](revisao_02/documentacao/memorial_descritivo.pdf)
- [DXF 2D editável](revisao_02/cad/projeto_academico_2d.dxf)
- [DXF 3D editável](revisao_02/cad/projeto_academico_3d.dxf)
- [Informações da versão e arquivos Blender/OBJ](revisao_02/README.md)
- [Análise da LUOS e Código de Obras fornecidos pelo aluno](revisao_02/documentacao/referencias_legais.pdf)
- [Conferência do enunciado](revisao_02/documentacao/conferencia_enunciado.pdf)

Aluno: **Icaro Gamarra Silva — RGM 3322.527**. Professora: **Rafaella Scalon**. Engenharia Civil — Prova de desenho técnico — 28/10/2026.

Lote hipotético de 20 × 50 m em Dourados-MS; três lojas e quatro apartamentos familiares. Revisão atual: 913,80 m² cobertos e 46,20 m² de pátios descobertos, totalizando 960 m² de pisos utilizáveis. Não confundir área coberta com área construída incluindo pátios.

Imprimir PDF em A2 paisagem, tamanho real/100%, sem ajustar à página. A documentação gráfica é acadêmica; conformidade integral legal/ABNT não certificada. A análise detalha os itens comparados e as limitações de localização, atividade comercial, vagas e normas.

Arquivos na raiz em `cad`, `pranchas`, `documentacao` e o ZIP `projeto_conceitual_dourados.zip` correspondem ao histórico inicial. **Para a versão atual, usar `revisao_02` e `PROJETO_ICARO_REV02.zip`.**

## Reprodução

Usar o checkout existente, sem criar worktree. Dependências em `scripts/requirements.txt`, mais Blender 4.3 e PyMuPDF. Na raiz do repositório:

```sh
python scripts/gerar_revisao.py
blender -b -t 2 --python scripts/renderizar_revisao.py
python scripts/gerar_revisao.py
python scripts/documentar_revisao.py
python scripts/verificar_revisao.py
```

A segunda geração das pranchas incorpora as imagens recém-renderizadas. Os scripts sobrescrevem os arquivos gerados da revisão; guardar cópia antes de editar DXF/Blender manualmente.
