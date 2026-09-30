# Kaggriculture Agent

Este projeto inclui um agente competitivo e um runner local que salva o replay visual de uma partida.

## Requisitos

- Windows com Python instalado.
- `uv` no PATH. Como alternativa, use `python -m pip`.
- Conexão com a internet na primeira instalação de `kaggle-environments`.

## Executar uma partida visual

1. Abra o PowerShell na pasta do projeto:

   ```powershell
   cd C:\Users\nober\OneDrive\Desktop\kaggriculture_agent
   ```

2. Rode o agente contra o jogador aleatório do ambiente:

   ```powershell
   uv run --with kaggle-environments -- python src/main.py
   ```

   Na primeira execução, `uv` baixa o ambiente e suas dependências. A partida tem até 720 turnos.

3. Aguarde o resumo no terminal. O runner mostra a recompensa e o status dos dois jogadores, grava `resultado.html` na pasta do projeto e abre o replay no navegador padrão.

4. No replay, use os controles da interface para avançar pelos turnos e observar a movimentação, os cultivos, as colheitas e o resultado final.

5. Se o navegador não abrir automaticamente, abra o arquivo `resultado.html` manualmente:

   ```powershell
   start .\resultado.html
   ```

## Opções do runner

```powershell
uv run --with kaggle-environments -- python src/main.py --opponent starter
uv run --with kaggle-environments -- python src/main.py --steps 240 --output teste-curto.html
uv run --with kaggle-environments -- python src/main.py --no-open
```

`--opponent` aceita os agentes disponíveis no `kaggle-environments`, como `random` e `starter`. `--steps` altera o limite de turnos; `--output` escolhe o caminho do replay; `--no-open` salva o HTML sem iniciar o navegador.

## Benchmark

Para repetir as partidas comparativas e o self-play:

```powershell
uv run --with kaggle-environments -- python benchmark.py --seeds 30 --opponents random pass starter
```

O benchmark testa o agente nos dois lados. Para rodar apenas o self-play:

```powershell
uv run --with kaggle-environments -- python benchmark.py --seeds 30 --self-play-only
```

## Arquivo de submissão

O pacote `submission.tar.gz` contém `main.py` e `agent.py` na raiz. Para recriá-lo após alterações:

```powershell
tar --exclude='*__pycache__*' -C src -czf submission.tar.gz .
tar -tzf submission.tar.gz
```

Envie pelo CLI do Kaggle:

```powershell
uv run kaggle competitions submit kaggriculture -f submission.tar.gz -m "Competitive multi-worker economic agent"
```
