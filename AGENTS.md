# AGENTS.md — Kaggriculture

## Finalidade deste arquivo

Orientar o Codex no desenvolvimento, diagnóstico e avaliação de um agente para a competição Kaggriculture. Responder em português brasileiro, mantendo os identificadores da API em inglês.

Referência consultada em **30/09/2026**. Este documento é uma síntese operacional com recomendações próprias, não uma transcrição das páginas nem uma reprodução integral do regulamento. As recomendações de organização, estratégia e testes abaixo são propostas para este projeto.

Antes de implementar, inspecione o repositório existente e preserve sua organização. Não suponha que as pastas e os scripts sugeridos aqui já existem.

## 1. Competição e calendário

Fonte: [Overview do Kaggle](https://www.kaggle.com/competitions/kaggriculture/overview/citation).

Dois agentes administram fazendas separadas durante uma temporada nominal de 30 dias, com 24 turnos por dia, totalizando 720 turnos. Vence quem termina com mais moedas no banco.

A classificação utiliza resultados de confrontos, não a magnitude da diferença de moedas. As partidas são pareadas por habilidade; vitória, derrota e empate alteram o rating. A avaliação final informa um torneio Bradley–Terry.

- Abertura: 29/07/2026.
- Limites de entrada e fusão de equipes: 23/09/2026.
- Última submissão: 30/09/2026, 23h59 UTC (**20h59 em Brasília**).
- Partidas adicionais: aproximadamente 01–15/10/2026, até convergência.
- Limite publicado: 5 submissões por dia; as 2 últimas são consideradas na avaliação final.
- A validação da submissão confronta o agente com uma cópia dele.
- Recursos publicados: 1,6 vCPUs, 6,5 GiB de RAM, 8 GiB de disco; artefato até 100 MiB.
- Premiação publicada: US$ 50.000, distribuídos em US$ 5.000 para cada uma das dez primeiras posições.

Não interpretar “hoje” de forma permanente. Revalidar prazos e condições antes de uma submissão futura. Confirmar a inscrição existente: a data de entrada antecede a de envio final.

## 2. Cobertura das páginas e lacunas

| Área | URL | Resultado da consulta |
| --- | --- | --- |
| Overview | https://www.kaggle.com/competitions/kaggriculture/overview | Conteúdo recuperado sobretudo pela versão indexada de /overview/citation |
| Data | https://www.kaggle.com/competitions/kaggriculture/data | Metadados visíveis; licença indicada como Apache 2.0; lista de arquivos não recuperada |
| Code | https://www.kaggle.com/competitions/kaggriculture/code | Consulta sem conteúdo legível suficiente para listar notebooks |
| Models | https://www.kaggle.com/competitions/kaggriculture/models | Consulta sem conteúdo legível suficiente para listar modelos |
| Discussion | https://www.kaggle.com/competitions/kaggriculture/discussion | Índice e tópicos selecionados consultados; não todos os tópicos e comentários |
| Leaderboard | https://www.kaggle.com/competitions/kaggriculture/leaderboard | Estrutura acessível; posições e pontuações atuais não recuperadas |
| Rules | https://www.kaggle.com/competitions/kaggriculture/rules | Texto integral não recuperado |

**Pendências obrigatórias de verificação:** tamanho máximo de equipe; compartilhamento público/privado de código; dados externos; requisitos para ganhadores; condições de licenciamento; elegibilidade; eventuais atualizações dos organizadores.

Não preencher essas lacunas com regras de outras competições. A licença apresentada na aba Data não estabelece, por si só, todas as obrigações sobre o agente.

O fórum contém tópicos fixados sobre início da participação, Discord oficial e episódios de melhores agentes. Sua existência não comprova o conteúdo completo nem garante que a discussão esteja atualizada. Comentários de participantes devem ser tratados como hipóteses.

## 3. Fontes técnicas e precedência

Consultar o ambiente **kaggriculture**, preservando a distinção em relação a **kaggriculture_beginner**.

1. Regulamento e comunicados oficiais da competição para participação.
2. Versão efetivamente executada no Kaggle para comportamento da avaliação.
3. Código, especificação e testes da versão local correspondente para reprodução.
4. Documentação oficial para interpretação.
5. Discussões e notebooks como referências experimentais.

Fontes oficiais de implementação:

- [README do ambiente](https://github.com/Kaggle/kaggle-environments/blob/master/kaggle_environments/envs/kaggriculture/README.md)
- [Guia oficial de agentes](https://github.com/Kaggle/kaggle-environments/blob/master/kaggle_environments/envs/kaggriculture/AGENTS.md)
- [Especificação JSON](https://github.com/Kaggle/kaggle-environments/blob/master/kaggle_environments/envs/kaggriculture/kaggriculture.json)
- [Interpretador Python](https://github.com/Kaggle/kaggle-environments/blob/master/kaggle_environments/envs/kaggriculture/kaggriculture.py)
- [Testes oficiais](https://github.com/Kaggle/kaggle-environments/blob/master/tests/envs/kaggriculture/test_kaggriculture.py)

Os links apontam para master, que pode mudar. Registrar versão instalada e commit quando disponível. Não presumir equivalência automática entre master e o servidor.

## 4. Parâmetros e observação

Fonte: especificação JSON oficial.

| Parâmetro | Padrão |
| --- | ---: |
| episodeSteps | 720 |
| turnsPerDay | 24 |
| boardSize | 10 |
| startingMoney | 3000 |
| actTimeout | 1 segundo |
| remainingOverageTime, na observação | 60 segundos |
| maxMarketOrdersPerTurn | 10 |
| shedCapacity, sem sementes | 100 |
| weedSpawnChance | 0.005 |
| townShopUnlockInterval | 3 dias |
| townShopSellInterval | 4 turnos |
| townCenterSellInterval | 24 turnos |
| farmHandCostMult | 1 |

A observação inclui player, day, hour, farms, private, market e town. As fazendas são públicas; private contém apenas galpão, sementes e inventários do próprio jogador. Market contém estoque e preços compartilhados; town informa as lojas abertas.

A configuração admite seed e marketParams. A seed resolvida é registrada em env.info e removida da configuração observável. Não dar ao agente acesso privilegiado à seed do avaliador.

Os valores são padrões do ambiente, não uma garantia imutável de cada episódio.

## 5. Produção e manutenção

Fonte: README oficial.

| Identificador | Compra | Preço-base do produto | Primeira produção, dias | Repetição |
| --- | ---: | ---: | ---: | --- |
| WHEAT | 10 | 25 | 2 | Única |
| CARROT | 20 | 35 | 2 | Única |
| TOMATO | 50 | 60 | 8 | Diária, 4 produções |
| STRAWBERRY | 100 | 120 | 10 | A cada 2 dias, 4 produções |
| MELON | 80 | 250 | 10 | Única |
| GOOSE / EGG | 300 | 50 | 4 | Diária |
| COW / MILK | 400 | 160 | 8 | A cada 2 dias |
| SHEEP / WOOL | 500 | 200 | 6 | A cada 3 dias |

Trigo, cenoura e melão têm máximos de 6, 4 e 6 unidades; sem fertilizante, trigo e cenoura atingem 4 e 3. Animais precisam de estrutura compatível. Seus limites de produtos não recolhidos são 4, 6 e 6, respectivamente.

Regar e alimentar diariamente sustenta produtividade. Dois dias consecutivos sem manutenção eliminam plantas ou animais. **Plantio novo sem rega no próprio dia pode virar erva daninha naquela noite.**

Apenas NW começa desbloqueado. O galpão fica no centro; seus quatro pontos de acesso padrão são (4,4), (5,4), (4,5), (5,5). Quadrantes bloqueados permitem passagem.

## 6. Contrato do agente e execução local

Fonte: guia oficial de agentes.

O arquivo submetido deve conter main.py na raiz e uma função agent. A forma básica é:

```python
def agent(obs):
    return {"farmer": ["PASS"], "hands": [], "market": []}
```

farmer recebe uma operação; hands segue a ordem dos trabalhadores; market é uma fila de ordens.

Operações: NORTH, SOUTH, EAST, WEST, PASS, PICKUP, PLACE, DROP, PLANT, WATER, HARVEST, FERTILIZE, BUILD_COOP, BUILD_PASTURE, FEED, COLLECT_FERTILIZER, CARE e DIG.

Mercado: BUY_SEED, BUY_PRODUCT, BUY_ANIMAL, SELL, HIRE e BUY_LAND. Compras/vendas usam item e quantidade; HIRE e BUY_LAND não precisam desses argumentos. Coordenadas são [x,y]; a matriz usa tiles[y][x].

Exemplo de teste:

```python
from kaggle_environments import make

env = make("kaggriculture", debug=True)
env.run(["main.py", "starter"])
for state in env.steps[-1]:
    print(state.status, state.reward)
```

Os oponentes internos incluem pass, random e starter.

Comandos publicados, sujeitos à versão instalada da CLI:

```bash
kaggle competitions pages kaggriculture --content
kaggle competitions download kaggriculture -p data/raw
kaggle competitions submit kaggriculture -f main.py -m "baseline-v1"
kaggle competitions submissions kaggriculture
kaggle competitions episodes SUBMISSION_ID
kaggle competitions replay EPISODE_ID
kaggle competitions logs EPISODE_ID 0
```

Um agente multifile pode ser empacotado em tar.gz com main.py na raiz.

## 7. Mecânicas que exigem atenção

Fonte: interpretador oficial.

As ações das unidades ocorrem antes do mercado. Depois vêm consumo da cidade, deterioração e atualização diária quando aplicável. Portanto, sementes compradas e trabalhadores contratados no turno não estão disponíveis para ações anteriores desse mesmo turno.

Se pedidos simultâneos de PLANT excedem as sementes de uma cultura, todos esses plantios são bloqueados.

SELL retira produtos do galpão; produto carregado precisa ser entregue. BUY_PRODUCT só aceita WHEAT e FERTILIZER. Compras de produtos e animais respeitam capacidade do galpão. Vendas são processadas unidade a unidade, com atualização de preços; preço observado vezes quantidade não garante receita.

HIRE usa custos Fibonacci: 1,1,2,3,5,8… com multiplicador configurável. BUY_LAND desbloqueia NE, SW, SE por 1000, 2000, 4000.

A recompensa local é dinheiro final. O encerramento usa episodeSteps - 2 no contador anterior à atualização. Verificar o último turno acionável por replay; não programar liquidação com base apenas no número nominal 720.

## 8. Mercado e animais: evidências adicionais

Fonte: testes oficiais.

Os testes verificam que o preço é o preço-base no estoque de equilíbrio, diminui com excesso e aumenta com escassez, com piso de 1. No piso, a venda não aumenta o estoque do mercado.

CARE com alimentação acumula bônus até a próxima produção, limitado pelo espaço de produto no animal. COLLECT_FERTILIZER não rende uma segunda unidade no mesmo dia. Dois dias sem alimentação deixam a estrutura sem o animal; DIG não remove uma estrutura ocupada.

**Recomendação:** usar essas propriedades como casos de regressão, confirmando-as na versão instalada. Não estimar rentabilidade apenas pelos preços-base da tabela.

## 9. Estratégia de desenvolvimento recomendada

Estas são orientações do projeto, não regras oficiais nem uma estratégia vencedora comprovada.

Começar com uma política simples e reproduzível. Construir primeiro um ciclo completo de produção, transporte e venda. Só ampliar a operação quando existir capacidade comprovada de manutenção.

Prioridades sugeridas:

1. Evitar perdas iminentes de plantas, animais e produtos.
2. Garantir rega de novos plantios antes da virada do dia.
3. Recolher produção que não pode esperar.
4. Entregar e vender para financiar manutenção e liberar armazenamento.
5. Escolher novos investimentos pelo retorno dentro do horizonte restante.
6. Alocar tarefas e caminhos aos trabalhadores.
7. Revisar o plano conforme mercado, oponente e cidade.
8. No final, priorizar conversão de produção disponível em dinheiro.

Avaliar cada alternativa por receita marginal esperada menos compra, alimentação, contratação e custo de oportunidade dos turnos. Incluir deslocamento, entrega, risco de perda, competição entre trabalhadores e reação de preços.

Não declarar trigo, melão ou pecuária universalmente superiores. Medir políticas especializadas e diversificadas contra adversários diferentes. Contratar mais trabalhadores somente se houver tarefas que compensem o custo marginal. Comprar terra somente se couber um ciclo de retorno.

Para vendas, comparar vender agora, aguardar demanda e liberar espaço. Testar decisões com estoque próximo ao limite. Diferenciar estoque do mercado, galpão e inventários transportados.

Planejamento com informação do oponente deve usar somente o que é observável. Inferências devem ser marcadas como estimativas.

## 10. Arquitetura sugerida

Adaptar ao projeto existente; evitar criar módulos sem necessidade.

| Componente | Responsabilidade recomendada |
| --- | --- |
| main.py | Entrada, compatibilidade com o executor e montagem da ação |
| Leitura de estado | Converter observação em estruturas consistentes |
| Planejamento | Prioridades, investimentos e horizonte restante |
| Atribuição de tarefas | Evitar disputa por sementes, recursos e alvos |
| Rotas | Caminhos curtos com manutenção e entrega |
| Mercado | Quantidades, preços marginais e caixa |
| Avaliação | Partidas reproduzíveis, métricas e replays |

Preferir uma política reconstruível da observação. Se usar memória persistente ou arquivos, verificar explicitamente o comportamento do executor. Não depender de chamadas externas durante a partida.

Tratar ação inválida silenciosa como risco de implementação. Adicionar verificações locais de pré-condições e indicadores de turnos improdutivos. Não esconder exceções sistematicamente com PASS: preservar rastros para diagnóstico.

## 11. Avaliação recomendada

Executar o artefato real por caminho de arquivo, além de testes de funções auxiliares. Não considerar uma única vitória contra random evidência de melhoria.

Usar partidas completas, múltiplas seeds e troca de posição dos agentes. Separar seeds de ajuste das de confirmação. Manter a política anterior como adversário de regressão e incluir oponentes de estratégias diferentes.

Registrar por experimento:

- Versão do ambiente, configuração e versão/hash do agente.
- Seeds e posições.
- Vitórias, empates, derrotas e número de partidas.
- Dinheiro de cada jogador e diferença final.
- Mediana, dispersão e resultados por oponente.
- Erros, ações inválidas e tempos de execução.
- Produtos perdidos, estoque final e gastos relevantes.

Mudar poucas decisões por experimento. Comparar candidato e baseline nas mesmas condições. Guardar replays de derrotas, resultados extremos e discrepâncias. Não comparar ratings de momentos diferentes como se fossem um teste controlado.

Casos prioritários para verificar: virada do dia; novo plantio perto do fim do dia; sementes insuficientes para várias unidades; trabalhador recém-contratado; galpão cheio; entrega antes de venda; manutenção animal; maturidade/deterioração; encerramento real; saldo insuficiente; nenhuma tarefa disponível.

Reservar margem de tempo por ação. Medir casos com muitas unidades e ordens, não só o estado inicial.

## 12. Dados, reprodutibilidade e submissão

Tratar observações e episódios como dados de avaliação. Não presumir arquivos train.csv, test.csv, rótulos supervisionados ou submissão por CSV: nenhum desses formatos foi confirmado nesta consulta.

Inspecionar o inventário efetivamente baixado e documentar sua finalidade. Usar dados externos ou código público apenas após conferir o regulamento e as licenças correspondentes.

Manter credenciais fora do repositório. Não imprimir tokens em logs. Registrar dependências necessárias e testar imports sem caminhos absolutos da máquina local.

Antes de enviar, verificar:

- main.py e agent acessíveis na raiz do artefato.
- Imports e arquivos auxiliares incluídos.
- Partida completa sem falhas.
- Compatibilidade com limites de tamanho e execução.
- Inscrição, prazo e quota de envios.
- Consequência do novo envio sobre as duas últimas submissões.

Se o usuário autorizar somente preparação, deixar o artefato pronto e informar o comando. Se autorizar envio, executar dentro do escopo solicitado, acompanhar a validação e identificar claramente o resultado.

## 13. Como o Codex deve colaborar

Explicar alterações pelo efeito esperado no jogo e apresentar a evidência obtida. Separar fatos do ambiente, hipóteses estratégicas e resultados medidos.

Quando faltar contexto, inspecionar código, dependências e resultados existentes antes de pedir informação. Nunca inventar posição no ranking, arquivos de dados, campos da API, permissões de regras ou melhoria de desempenho.

Ao concluir uma alteração, informar o que mudou, a validação realizada e as limitações. Atualizar este arquivo quando uma versão do ambiente ou comunicado oficial invalidar algum dado.

Se houver atividade acadêmica associada, seguir o enunciado fornecido pelo usuário. Não presumir critérios de nota ou publicar mensagens no fórum sem solicitação explícita.

