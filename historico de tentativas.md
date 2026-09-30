# Histórico de tentativas — Kaggriculture

Registro das tentativas realizadas em 30/09/2026. Os valores de moedas são recompensas de partidas locais completas; a pontuação pública do Kaggle é uma métrica diferente. Os resultados intermediários abaixo foram anotados durante os experimentos. As versões de cada tentativa não foram todas salvas em commits separados.

## Ponto de partida e primeira submissão

- No replay local `resultado.html`, o agente era o jogador 0 e terminou com 30.119 moedas contra 0 do jogador 1 (oponente `random`), no passo 719, semente 7667221. Uma partida isolada não demonstra desempenho geral.
- A primeira chamada à CLI falhou com `Authentication required`. Inicialmente foi sugerido `kaggle.json`, mas a CLI instalada indicou `kaggle auth login` ou um token em `~/.kaggle/access_token`. Nenhuma credencial está registrada aqui.
- O pacote `submission.tar.gz` continha `main.py` e `agent.py` na raiz. O primeiro envio ficou aparentemente parado em 0% durante o upload, mas terminou posteriormente.
- A submissão **56716107**, descrição `Agente economico multi-worker v1`, apareceu como `COMPLETE` em 30/09/2026, com **600,0 pontos públicos**. Esse resultado pertence ao agente anterior aos ajustes abaixo. A meta mencionada pelo usuário era chegar a 3.000 pontos públicos; nenhum teste local comprova que ela foi atingida.

## Primeira série: três tentativas sobre a versão submetida

Referência: código anterior ao commit `169a088` (revisão `66e34b7`). O avaliador local executou partidas de 720 passos com sementes 0–3, trocando os lados dos agentes: 8 partidas por adversário. Contra `starter`, a referência fez média de 30.063,4 moedas. As médias contra a própria referência variam porque ambos os agentes afetam o mesmo mercado.

| Tentativa | Hipótese e mudança | Contra a referência | Moedas médias contra a referência | Moedas médias contra `starter` | Decisão |
| --- | --- | ---: | ---: | ---: | --- |
| 1 | Esperar até a idade de rendimento máximo para colher trigo, cenoura e melão, em vez de colher na primeira maturidade. | 1 vitória, 7 derrotas | 15.671,9 | 30.329,4 | Isoladamente, piorou o confronto direto. A hipótese foi mantida para testar a correção dos gargalos de plantio e rega. |
| 2 | Limitar plantios simultâneos ao número de sementes, repor sementes antes de zerar e elevar a prioridade de rega. | 8 vitórias | 23.470,0 | 29.729,4 | Melhorou fortemente o confronto direto, embora a média contra `starter` tenha caído. |
| 3 | Parar de escolher cultivos que não amadureceriam até o fim, comprar mais sementes para culturas rápidas e continuar contratando mãos nos últimos dias. | 8 vitórias | 24.308,9 | 29.748,9 | Mantida por ampliar a margem no confronto direto; o ganho contra `starter` foi pequeno. |

Diagnóstico importante da tentativa 2: a política original podia atribuir mais ações `PLANT` do que sementes disponíveis. Pela regra do ambiente, quando pedidos simultâneos excedem o estoque, todos os plantios daquela cultura falham. A rega também competia com colheitas de alta prioridade, deixando plantas vulneráveis. O rastreamento da tentativa 2 mostrou ainda pouca atividade produtiva após a colheita tardia de melões.

A versão da tentativa 3, o avaliador `evaluate_local.py` e o pacote correspondente foram registrados no commit **`169a088`** (`Registra score publico 600 e melhorias locais do agente`). O commit documentou corretamente que os 600 pontos públicos pertenciam à submissão anterior. Uma execução por arquivo `src/main.py` terminou com `DONE` para os dois jogadores e 29.487 contra 3.602 moedas.

## Segunda série: três tentativas sobre `169a088`

Referência: commit `169a088fe37a3854d847c870e7b630599dce33cc`. Novamente foram usadas sementes 0–3, ambos os lados e 8 partidas por adversário. A referência fez média de 29.748,9 moedas contra `starter` e 21.290,9 em confronto consigo mesma.

| Tentativa | Hipótese e mudança | Contra `169a088` | Moedas médias contra `169a088` | Moedas médias contra `starter` | Decisão |
| --- | --- | ---: | ---: | ---: | --- |
| 1 | Colher melões no dia 10, quando a rega diária já completa seu rendimento máximo, em vez de aguardar o dia 12. | 8 vitórias | 24.653,4 | 34.141,5 | Mantida: liberou os espaços dois dias antes e melhorou ambas as comparações. |
| 2 | Acrescentar a ordem `BUY_SEED` também no ramo de mercado do fim da temporada, onde era calculada mas descartada. | 8 vitórias | 24.627,1 | 34.170,4 | Mantida: melhora pequena contra `starter`, com leve recuo de moedas no confronto direto. |
| 3 | Elevar `max_plants` de 21 para 25 para usar todo o quadrante inicial. | 8 vitórias | 25.178,4 | 31.872,1 | Mantida após confronto direto com o limite anterior, apesar da queda de moedas contra `starter`. |

Validação adicional da tentativa 3: limite de 25 plantas contra o de 21, com sementes 0–7 e troca de lados. O limite de 25 venceu **13 de 16** partidas, mas sua margem média foi **−471,9 moedas**: as três derrotas pesaram mais na diferença de dinheiro do que as 13 vitórias. A decisão priorizou a contagem de vitórias, pois a classificação é baseada em confrontos. Essa amostra ainda é pequena e não garante melhor rating público. Uma partida completa por `src/main.py`, semente 9, terminou `DONE` com 30.855 contra 3.639 moedas. O pacote `submission.tar.gz` foi reconstruído e verificado com `main.py` e `agent.py` na raiz.

## Estado e reprodução

- A versão atual de `src/agent.py` contém as três mudanças da segunda série e estava **sem commit e sem submissão ao Kaggle** quando este histórico foi escrito. Portanto, **600,0** continua sendo o único resultado público informado nesta conversa.
- `evaluate_local.py` compara a versão atual com o commit `169a088` e com `starter`: `uv run --with kaggle-environments -- python evaluate_local.py --seeds 4`.
- Para repetir o confronto entre limites de plantas: `uv run --with kaggle-environments -- python evaluate_local.py --seeds 8 --compare-plants`.
- Para inspecionar ações e dinheiro por dia em uma partida: `uv run --with kaggle-environments -- python evaluate_local.py --trace`.
- O avaliador usa `configuration={"episodeSteps": 720, "seed": seed}`. Um benchmark preliminar usava `env.reset(seed=...)`, mas a versão instalada não aceita esse argumento; por isso, seus números não foram usados nas tabelas reproduzíveis.
- Limitações: o adversário `starter` é fraco, os testes abrangeram poucas sementes e não reproduzem o conjunto de adversários nem o rating do Kaggle. As variantes intermediárias não têm hashes próprios; os números acima preservam o que foi observado, mas não permitem reexecutar exatamente cada uma delas a partir do Git.
