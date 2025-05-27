# Tech Challenge – Fase 3

> Neste repositório, apresentamos a solução completa para o Tech Challenge Fase 3, em que foi um modelo de Machine Learning integrada a um pipeline de dados e a uma aplicação produtiva (um site) que consome esse modelo por meio de uma API.

## Índice

* [Introdução](#introdução)
* [Fontes de dados usadas](#fontes-de-dados-usadas)
* [Análise exploratória dos dados](#análise-exploratória-dos-dados)
* [Modelos utilizados](#modelos-utilizados)
* [Resultados obtidos](#resultados-obtidos)
* [Pipeline](#pipeline)
* [Arquitetura](#arquitetura)
* [Como rodar o projeto](#como-rodar-o-projeto)
* [Deploy](#deploy)

---

## Introdução

O projeto teve como foco criar um modelo de Machine Learning para predizer resultados de partidas de futebol do campeonato inglês (Premier League). O modelo foi treinado com uma base de dados pública e seu objetivo é tentar prever o resultado de uma partida de futebol, ou seja, dado um time que joga em casa e um time que joga como visitante, o modelo vai prever qual a probabilidade do time que joga em casa ganhar (H - home), qual a probabilidade de empate (D - draw) e qual a probabilidade do time visitante vencer (A - away).

Dado esse contexto, pode-se dizer que o problema se trata de um problema de aprendizado supervisionado de classificação, em que o modelo vai tentar prever a probabilidade de 3 classes: H, D, A. O modelo foi treinado com algoritmos de classificação e foram usadas medidas como: total de gols marcados, total de pontos, total de gols sofridos e se um time é considerado um time de elite.

Por fim, foi implantando um site em produção para consumo do modelo em tempo real no [render](https://render.com/). O site está disponível aqui: https://tech-challenge3.onrender.com/


## Fontes de dados usadas

A fonte de dadaos utilizada pode ser encontrada no [football-data](https://www.football-data.co.uk/englandm.php). É um grande site que contém várias bases de dados relacionadas ao futebol. O football-data disponibiliza dados de vários campeonatos pelo mundo em forma de arquivos .csv, o que facilita bastante o consumo desses dados.

Além disso, o football-data é estruturado de uma maneira amigável ao scraping desses arquivos .csv, o que facilita um fluxo de pipeline de dados, por exemplo.

Dado essas características, foi construído um mecanismo de scraping no arquivo **MLpipeline/downloader.py** que tem como objetivo baixar os arquivos .csv desse site e armazená-los numa pasta chamada data/england/premier_league.

Os arquivos .csv foram salvos seguindo uma nomenclatura em que os primeiros 2 digitos representam o ano de início da temporada e os 2 último dígitos representam o último ano da temporada. Então o arquivo 9394.csv se refere-se aos dados da temporada de 1993-1994, o 0102 seria o da temporada de 2001-2002. Isso porque a Premier League começa em agosto de um ano e termina em maio do ano seguinte.

Abaixo, uma imagem do site football-data:
![football-data](./images/football-data.png)


## Análise exploratória dos dados

### Entendendo as colunas
Os dados coletados têm dezenas de colunas, que podemos dividir por grupos para facilitar o entendimento (para saber o significado de cada coluna, veja o arquivo [notes.txt](./notes.txt) fornecido pelo site oficial).

Basicamente, existem 2 tipos de colunas nessa base de dados bruta, as colunas que representam estatísticas que ocorreram nos jogos (número de gols, faltas, etc) e probabilidades de várias casas de apostas relacionada aos eventos, por exemplo, a probabilidade de sair mais 2 gols num jogo. A coluna target é a coluna FTR (Full Time Result), pois é ela que contém o resultado final da partida. O foco foi nas colunas de estatísticas e são elas que vamos explicar melhor, mas nem todas elas foram usadas:

- **Div**: representa a divisão do campeonato, a inglaterra tem várias divisões, algo como série A ou série B aqui no Brasil. A Nessa base dados, a Premier League (primeira divisão) recebeu o valor de E0.

- **Date**: data em que ocorreu o jogo.

- **Time**: hora do dia em que a partida iniciou.

- **HomeTeam**: nome do time que está jogando em casa.

- **AwayTeam**: nome do time que está jogando como visitante.

- **FTHG**: é uma abreviação para "Full Time Home Goals", ou seja, quantos gols o time da casa marcou no tempo total de jogo.

- **FTAG**: é uma abreviação para "Full Time Away Goals", ou seja, quantos gols o time visitante marcou no tempo total de jogo.

- **FTR**: é uma abreviação para "Full Time Result", ou seja, é o resultado da partida e pode ter 3 valore: H (o time da casa venceu), D (empate) ou A (o time visitante venceu).

- **HTHG**: é uma abreviação para "Half Time Home Goals", ou seja, quantos gols o time da casa marcou no primeiro tempo.

- **HTAG**: é uma abreviação para "Half Time Away Goals", ou seja, quantos gols o time visitante marcou no primeiro tempo.

- **HTR**: é uma abreviação para "Half Time Result", ou seja, quem venceu o primeiro tempo do jogo.

- **Referee**: é nome do juiz da partida.

- **HS**: é uma abreviação para "Home shots", ou seja, é o número de chutes ao gol do time da casa.

- **AS**: é uma abreviação para "Away shots", ou seja, é o número de chutes ao gol do time visitante.

- **HST**: é uma abreviação para "Home Shots on Target", ou seja, é o número de chutes ao gol do time da casa no gol (não considera chutes para fora).

- **AST**: é uma abreviação para "Away Shots on Target", ou seja, é o número de chutes ao gol do time visitante no gol (não considera chutes para fora).

- **HF**: é uma abreviação para "Home Fouls", ou seja, o número de faltas cometidas pelo time da casa.

- **AF**: é uma abreviação para "Away Fouls", ou seja, o número de faltas cometidas pelo time visitante.

- **HC**: é uma abreviação para "Home Corners", ou seja, o número de escanteios cobrados pelo time da casa.

- **AC**: é uma abreviação para "Away Corners", ou seja, o número de escanteios cobrados pelo time visitante.

- **HY**: é uma abreviação para "Home Yellow Cards", ou seja, o número de cartões amarelos que o time da casa recebeu.

- **AY**: é uma abreviação para "Away Yellow Cards", ou seja, o número de cartões amarelos que o time visitante recebeu.

- **HR**: é uma abreviação para "Home Red Cards", ou seja, o número de cartões vermelhos que o time da casa recebeu.

- **AR**: é uma abreviação para "Away Red Cards", ou seja, o número de cartões vermelhos que o time visitante recebeu


Abaixo, uma imagem dos dados brutos de um csv da base de dados:
![football-data](./images/dados_brutos.png)



### Multicolinearidade

Durante a análise exploratória dos dados, foi possível observar que diversas variáveis da base apresentavam alta correlação entre si, o que pode indicar a presença de multicolinearidade. A multicolinearidade ocorre quando duas ou mais variáveis independentes carregam informações muito semelhantes, dificultando a interpretação dos coeficientes em modelos preditivos e, em alguns casos, prejudicando o desempenho do modelo.

No nosso caso, pode-se ver claramente que quantos mais gols o time marca, por exemplo, mais escanteios ele vai ter e provavelmente menos cartões amarelos e vermelhos ele vai levar. Da mesma fora, quanto mais gols um time fez, provavelmente, mais chute ao gol ele deu.

Rodando o script presente em /scripts/matriz_correlacao.py podemos perceber que há grange correlação entre algumas variáveis da base de dados, algumas variáveis chegam a ter correlação com 2 ou até 3 outras variáveis da base de dados (multicolinearidade)

Abaixo temos a matriz de correlação de um dos CSVs da nossa base de dados bruta:
![asdfsd](./images/matriz_correlacao.png) 


### Gerando novas features
A partir das features que já estão nos CSVs, foi possível gerar novas features que ajudaram bastante o desempenho dos modelos.

Features Geradas
- **Gols marcados**: representa o total de gols marcados por um time na temporada em todos os jogos anteriores naquela mesma temporada. Tem o propósito de avaliar a força ofensiva geral do time na temporada. Foi adicionado à base de dados com os nomes: TotalHomeGoals e TotalAwayGoals.

- **Gols sofridos**: representa o total de gols sofridos por um time na temporada em todos os jogos anteriores naquela mesma temporada. Tem o propósito de avaliar a força defensiva geral do time na temporada. Foi adicionado à base de dados com os nomes: TotalHomeConceded e TotalAwayConceded.

- **Total de partidas jogadas**: representa o total de partidas jogadas por um time no campeonato da premier league. A premier League tem no total 38 partidas. Alguns times tendem a jogar de maneiras diferentes em relação ao final ou ao início da competição. Foi adicionado à base de dados com os nomes: TotalHomeMatches e TotalAwayMatches.

- **Total de pontos**: 



### Features selecionadas



### Falta de dados



## Etapa de pré-processamento


## Modelos utilizados






Detalhe os algoritmos de ML escolhidos, hiperparâmetros, estratégias de validação e justificativas para cada escolha.




## Resultados obtidos

Mostre métricas de performance (ex.: acurácia, recall, F1-score, log-loss), comparações entre modelos e interpretação dos resultados.



## Pipeline

Explique passo a passo o fluxo de dados, desde a ingestão até a geração de previsões, incluindo tecnologias e frameworks.

## Arquitetura

Descreva a arquitetura geral da solução (diagrama, componentes, integrações) e como cada parte se conecta.

## Como rodar o projeto

1. Pré-requisitos: lista de dependências.
2. Instalação: comandos para configurar o ambiente.
3. Execução: como iniciar a aplicação localmente.

## Deploy

Detalhe o processo de deploy em produção, ambientes suportados e comandos necessários.
