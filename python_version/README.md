# Duplicated & Compare Lists Tool — Python (macOS / Linux / Windows)

Port do `src/duplicated_compare_tool.ahk` (AutoHotkey v1, só Windows) para
Python 3 + tkinter (stdlib, sem dependências).

## Requisitos

- Python 3.10+
- tkinter:
  - Windows/macOS: já vem com o Python oficial.
  - Linux (Debian/Ubuntu): `sudo apt install python3-tk`
  - Fedora: `sudo dnf install python3-tkinter`

## Rodar

```bash
python duplicated_compare_tool.py
```

Comportamento inicial = AHK com `--run`: carrega o clipboard e analisa.
Atalho dentro do app: `Ctrl+Shift+Y` recarrega do clipboard.

## Interface

Menu principal + abas (o Compare fica numa aba, nunca escondido atrás):

- File > Quit (`Ctrl+Q`)
- Edit > Copy duplicates / Copy distinct
- View > Always on top (sincronizado com o checkbox da aba Duplicates)
- Tools > Compare 2 lists (`Ctrl+T`, abre a aba de comparação)
- Aba `Duplicates`: input + duplicadas + distintas.
- Aba `Compare 2 lists`: listas A/B com `Ln X / Y`, Process, Clear.

## CLI

```bash
# headless (sem janela) — análise simples
python duplicated_compare_tool.py --no-gui --text "a\nA\nb"

# headless — de arquivo
python duplicated_compare_tool.py --no-gui --file input.txt

# headless — comparar 2 listas
python duplicated_compare_tool.py --no-gui --compare-a a.txt --compare-b b.txt --name-a Frutas1 --name-b Frutas2

# hotkey global no SO (opcional, precisa de `pip install pynput`)
python duplicated_compare_tool.py --global-hotkey
```

No macOS o hotkey global pode pedir permissão de Acessibilidade; o
atalho interno (`Ctrl+Shift+Y` com a janela focada) funciona sem permissão.

## Paridade com o AHK

- Case-insensitive (via `casefold`, superset do `StringUpper` do AHK).
- Linhas vazias ignoradas; `distinct` mantém a 1ª grafia vista.
- Duplicadas renderizam como `original (xN)`; sem duplicadas: `No duplicates found.`
- Compare gera as mesmas seções do AHK (`=== Comuns em ... ===`, etc.) e o
  mesmo `summary` (`Distinct A: ... | ...`), com nomes A/B como fallback.
- Indicador `Ln X / Y` nos dois inputs do compare; `Always on top` nas 2 janelas.
