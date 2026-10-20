# Duplicated & Compare Lists Tool — Python (macOS / Linux / Windows)

Port do `src/duplicated_compare_tool.ahk` (AutoHotkey v1, só Windows) para
Python 3 + tkinter (stdlib, sem dependências).

## Requisitos

- Python 3.10+ com Tk 8.6+ (o Tk 8.5 do Python 3.9 fornecido pela Apple pode travar a interface).
- tkinter:
  - Windows/macOS: use o Python oficial; no macOS também é possível instalar com `brew install python@3.13 python-tk@3.13`.
  - Linux (Debian/Ubuntu): `sudo apt install python3-tk`
  - Fedora: `sudo dnf install python3-tkinter`

## Rodar

```bash
python duplicated_compare_tool.py
```

No macOS com a instalação via Homebrew, execute com `python3.13 duplicated_compare_tool.py`.

No menu `open_hub_logs_lnav.sh` da pasta `Montreal`, escolha a opção `6. Duplicated & Compare Lists Tool` para abrir a interface. O menu seleciona um Python compatível e localiza o programa a partir da própria pasta, independentemente do diretório atual do terminal.

Comportamento inicial = AHK com `--run`: carrega o clipboard e analisa.
Atalho dentro do app: `Ctrl+Shift+Y` ou `Cmd+Shift+Y` recarrega do clipboard.

## Interface

Janela principal com áreas de texto que acompanham o tamanho da janela. A comparação abre em outra janela:

- File > Quit (`Ctrl+Q`)
- Edit > Copy duplicates / Copy distinct
- View > Always on top (sincronizado com o checkbox da aba Duplicates)
- Tools > Compare 2 lists (`Ctrl+T` ou `Cmd+T`, abre a janela de comparação)
- Janela principal: input + duplicadas + distintas; o botão Paste from Clipboard carrega e analisa o texto copiado.
- Janela `Compare 2 lists`: a lista A começa com o conteúdo da entrada principal; as listas A/B têm botões Paste, `Ln X / Y`, Process, Clear e resultado.
- O ícone com duas listas e uma linha destacada aparece no Dock do macOS e nas janelas do aplicativo.

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
atalho interno (`Ctrl+Shift+Y` ou `Cmd+Shift+Y` com a janela focada) funciona sem permissão.

## Paridade com o AHK

- Case-insensitive (via `casefold`, superset do `StringUpper` do AHK).
- Linhas vazias ignoradas; `distinct` mantém a 1ª grafia vista.
- Duplicadas renderizam como `original (xN)`; sem duplicadas: `No duplicates found.`
- Compare gera as mesmas seções do AHK (`=== Comuns em ... ===`, etc.) e o
  mesmo `summary` (`Distinct A: ... | ...`), com nomes A/B como fallback.
- Indicador `Ln X / Y` nos dois inputs do compare; `Always on top` nas 2 janelas.
