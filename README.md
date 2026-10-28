# Edifício misto — Dourados/MS

Estudo arquitetônico conceitual criado do zero para lote hipotético de **20 × 50 m**, com dois pavimentos, três lojas e quatro apartamentos de dois quartos.

## Entregas

- `cad/estudo_misto_dourados.dxf`: desenho editável em metros, DXF R2010, com seis conjuntos separados horizontalmente no modelspace, camadas por função e cotas nativas.
- `pranchas/projeto_conceitual.pdf`: seis pranchas A3, com implantação/cobertura, térreo, superior, dois cortes, quatro fachadas e quadro de áreas. Impressão ajustada à página; usar cotas, não medir o PDF como escala fixa.
- `pranchas/01.svg` a `06.svg`: versões vetoriais individuais.
- `documentacao/memorial_descritivo.md` e `.pdf`: programa, distribuição, hipóteses, materiais e pendências.
- `documentacao/quadro_areas.csv` e `areas.json`: áreas brutas e indicadores.
- `verificacao/relatorio.json`: auditoria do DXF e conferência aritmética.
- `scripts/gerar_projeto.py`: fonte reproduzível da geometria e pranchas.

## Síntese

Projeção de 16 × 30 m, recuos hipotéticos de 10 m na frente/fundo e 2 m nas laterais. Área construída conceitual de **960 m²**, ocupação de 48%. Cada loja ocupa módulo bruto de 128 m²; cada apartamento, 84 m². A circulação residencial é independente das lojas.

## Regenerar

Python 3.11 ou superior. Instalar `python -m pip install -r scripts/requirements.txt` em ambiente virtual e executar, na raiz:

```sh
MPLCONFIGDIR=/tmp/mpl-projeto XDG_CACHE_HOME=/tmp/cache-projeto python scripts/gerar_projeto.py
python scripts/gerar_memorial.py
python scripts/verificar.py
```

Não é necessário servidor. Usar o checkout existente; não criar worktree para este fluxo. Os scripts sobrescrevem somente as entregas geradas indicadas acima. Não executar após edição manual do DXF sem salvar uma cópia.

## Limites de uso

Não é projeto executivo, legal aprovado ou levantamento do imóvel. Não foram fornecidos endereço, inscrição imobiliária, topografia, orientação real nem consulta urbanística. As dimensões de ambientes são modulares brutas; não certificam áreas úteis. Estacionamento, acessibilidade integral, elevador, ventilação mecânica, incêndio e estrutura precisam de desenvolvimento profissional. Ver o memorial antes de utilizar o desenho.
