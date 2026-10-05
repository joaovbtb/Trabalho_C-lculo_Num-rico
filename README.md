# Trabalho Prático 1 — Cálculo Numérico

Implementação em Python das três questões do Trabalho Prático 1 da disciplina DAS-5103 — Cálculo Numérico para Controle e Automação (UFSC).

## Conteúdo

- `codigo_q1.py`: resolução de uma equação não linear pelos métodos da bisseção, falsa posição, Newton e secante;
- `codigo_q2.py`: solução de um sistema linear por eliminação de Gauss com pivotamento parcial;
- `codigo_q3.py`: solução de um sistema não linear pelo método de Newton-Raphson;
- `gerar_tabelas_iteracoes_latex.py`: geração das tabelas de iteração em LaTeX;
- `gerar_relatorio_pdf.py`: geração do relatório final em PDF.

As figuras geradas estão em `figures/` e o relatório final em `output/pdf/`.

## Requisitos

- Python 3.10 ou superior;
- dependências listadas em `requirements.txt`.

## Como executar

No PowerShell, crie e ative um ambiente virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Execute cada questão:

```powershell
python codigo_q1.py
python codigo_q2.py
python codigo_q3.py
```

Para gerar os artefatos do relatório:

```powershell
python gerar_tabelas_iteracoes_latex.py
python gerar_relatorio_pdf.py
```
# Trabalho_C-lculo_Num-rico