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

## Resultados

A submissão `56716107` (`Agente economico multi-worker v1`, enviada em
30/09/2026) recebeu **600,0 pontos públicos** no Kaggle e foi concluída com
status `COMPLETE`.

Depois dessa submissão, o agente foi ajustado em três tentativas locais. Na
última, venceu a versão submetida em 8 de 8 partidas (quatro sementes, cada
agente em ambos os lados), com média de 24.309 moedas. Essas moedas são a
recompensa dentro das partidas e não equivalem à pontuação pública. O pacote
atual `submission.tar.gz` contém essa versão ajustada; ainda não há pontuação
pública registrada para ela.

Para repetir a comparação local com a versão da submissão `56716107`:

```powershell
uv run --with kaggle-environments -- python evaluate_local.py --seeds 4
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
