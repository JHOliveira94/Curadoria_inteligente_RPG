# Curadoria inteligente de sessões de RPG de Mesa

Projeto para portfólio de Engenharia de Dados<br>
Autoria de [José Henrique de Oliveira](https://www.linkedin.com/in/jholiveira94/)<br>
Orientado por [Pedro Fogaça](https://www.linkedin.com/in/pedrohfogacas/)
<br><br>

## Sumário
- [Contexto do projeto](#contexto-do-projeto)
    - [O problema enfrentado](#o-problema-enfrentado)
    - [A solução proposta](#a-solução-proposta)
- [Detalhes da solução](#detalhes-da-solução)
    - [Arquitetura do pipeline](#arquitetura-do-pipeline)
    - [Fonte de dados](#fonte-de-dados)
    - [Métricas de impacto](#métricas-de-impacto)
    - [Diferenciais e vantagens](#diferenciais-e-vantagens)
- [Implementação e ferramentas](#implementação-e-ferramentas)
<br><br>

## Contexto do projeto

O RPG de mesa vem ganhando espaço em plataformas de distribuição de conteúdo digital com produções como [Ordem Paranormal Quarta Temporada - Calamidade no YouTube](https://www.youtube.com/playlist?list=PL7ZwE005lvhpwy5LoKj8FXi2MXtJyey54), que contém treze episódios que variam de três a cinco horas e sua playlist acumula mais de seis milhões de visualizações.

De forma geral, sessões de RPG de mesa costumam ser longas e complexas, ainda mais quando estendem-se por uma longa campanha, então é natural que criadores de conteúdo desse nicho produzam materiais promocionais a partir de suas gravações, pois assim podem destacar momentos que chamem mais público e fidelize aqueles quem já acompanha. Mas, buscar tais momentos de forma manual torna-se uma tarefa árdua em uma produção que pode ultrapassar as cinco horas de duração.

Agravando a situação dos produtores de conteúdo, essas plataformas de distribuição costumam impor altas exigências por consistência, volume e engajamento para quem deseja trabalhar com elas, fazendo com que precisem produzir mais em menos tempo, o que vai de encontro com o ritmo de curadoria de uma sessão de RPG.

Com esse projeto, tenho o objetivo de auxiliar criadores de conteúdo e editores de vídeo que trabalhem com gravações de sessões de RPG de Mesa e buscam agilidade e eficiência para gerar cortes, resumos ou trailers a partir de vídeos, especialmente quando longos, postados no YouTube ou Twitch.

### O problema enfrentado

Como realizar de forma mais ágil e eficiente a curadoria de conteúdo a partir de gravações de sessões de RPG de mesa?

### A solução proposta
Considerando um fluxo de curadoria, é necessário elencar possíveis partes do conteúdo original para depois selecionar os que servirão de material promocional.

Assim, proponho um dashboard interativo em que momentos de maior carga emocional estarão destacados, agilizando o processo de listagem inicial e deixando para o curador a tarefa de escolher apenas entre as sugestões.

Com essa solução espero:
- Reduzir drasticamente o tempo de análise manual.
- Facilitar a identificação de momentos marcantes.
- Apoiar decisões criativas com base em dados emocionais.
- Aumentar a produtividade e a qualidade da curadoria.
- Ajudar a gerar novas ideias de conteúdo com potencial de engajamento.


## Detalhes da solução
Para a execução do dashboard para curadoria, será necessário construir um pipeline que parta do conteúdo original em vídeo e entregue uma análise de sentimentos tabelada.

### Arquitetura do pipeline
![alt text](image.png)

Para essa solução, proponho:
- Data Lake com arquitetura medallion:<br>
    Cada etapa do processamento terá seus respectivos arquivos separados, dando segurança em caso de perdas em qualquer momento do pipeline, retomando o projeto com mais facilidade.

- Banco de dados relacional para armazenamento de dados prontos para uso:<br>
    Nesse projeto, os dados tratados serão conectados ao PowerBI, mas poderão ser usados em análises com outras ferramentas e por outros profissionais de forma facilitada por estarem em um banco de dados.

- Banco de dados NoSQL para dados não estruturados:<br>
    Assim como será feito com os dados já tratados, as transcrições que são dados ainda sem estrutura, mas ricos em informações, serão armazenadas em banco de dados para facilitar seu uso no próprio pipeline quanto em momentos futuros.

- Padronização de ferramentas:<br>
    Preocupando-me com a quebra de ferramentas, tanto pela diferença de configuração entre máquinas quanto por atualizações de pacotes usados, escolhi a solução de contêineres do Docker para estruturar o projeto.

### Fonte de dados
Os dados trabalhados são gravações de sessões de RPG de mesa publicadas em plataforma de mídia digital - nesse projeto o foco será o YouTube. 

Além dos vídeos, serão  extraídos também metadados, informações relevantes e intrínsecas às publicações, como título, descrição, duração, palavras-chave (tags) e timestamps.

### Métrica de impacto
- Redução do tempo da curadoria<br>
    Originalmente, o tempo mínimo para análise de um vídeo está próximo de sua duração. Em uma gravação de 4h de duração, será necessário dedicar algo próximo a esse tempo para curadoria.

    Com essa proposta de solução, a duração da curadoria estará próxima da execução do pipeline mais o tempo para rever os trechos indicados que a pessoa responsável desejar.

### Diferenciais e vantagens
Mesmo ganhando espaço na mídia digital, o RPG ainda é um conteúdo de nicho, portanto ter um produto que automatize de forma orientada por dados parte do processo braçal da curadoria é algo inesperado no mercado, em especial usando tecnologias modernas como NLP (Processamento de Linguagem Natural) e análise de sentimento.

Com essa abordagem, algumas vantagens destacam-se:

- Eficiência operacional<br>
É comum entre criadores de conteúdo a contratação de editores de vídeo e até de profissionais dedicados especificamente para geração de cortes de conteúdo.<br>
Com parte da curadoria automatizada, o tempo antes dedicado a busca de trechos interessantes poderá ser direcionado para a edição e demais etapas técnicas que poderão ser executadas com mais tranquilidade.

- Vantagem competitiva<br>
Dada a pressão das plataformas e as expectativas dos consumidores, os criadores de conteúdo precisam ser ágeis para novas publicações, além disso, há também pessoas que criam conteúdo a partir da publicação de terceiros.<br>
Portanto, reduzindo o tempo de curadoria, o criador de conteúdo que queira aproveitar suas gravações estará a frente dos demais.

## Implementação e ferramentas
Para a execução desse projeto, defini previamente uma estrutura de Data Lake local e uma série de tecnologias que visam automatizar os processos de forma sustentável e escalável.

### Armazenamento do projeto
- Config<br>
Contém arquivos de configuração do projeto, como .env, settings.json, chaves de API, parâmetros de processamento e conexões com banco de dados.

- Dashboard<br>
Armazena o código da aplicação de visualização (ex: Streamlit ou Dash), responsável por exibir os dados analisados e permitir interações com os resultados.

- Db<br>
Scripts e arquivos relacionados ao banco de dados relacional (PostgreSQL) e não relacional (MongoDB).

- Notebooks<br>
Notebooks Jupyter

- Scripts<br>
Scripts Python que implementam as etapas do pipeline de dados.

- Volumes<br>
Diretório onde ficam os dados persistentes dos bancos PostgreSQL e MongoDB, utilizados quando os serviços são executados em containers Docker.<br>
Essa pasta garante que os dados não se percam ao parar os contêineres.

- Docs<br>
Contém documentação técnica do projeto, como instruções de uso, diagramas de arquitetura, versões, e decisões de design.

- Data<br>
    - Data Lake<br>
    Repositório central de armazenamento que organiza os dados do projeto em diferentes estágios de processamento, desde a coleta bruta até os dados prontos para consumo analítico.

    - Estrutura medalhão<br>
    Modelo de organização em camadas do Data Lake, onde os dados evoluem em qualidade e estrutura conforme avançam no pipeline. Camadas: raw, bronze, silver, gold, export.

    - Raw<br>
    Contém os dados brutos coletados diretamente da fonte, como vídeos originais, arquivos de áudio e metadados obtidos via download.

    - Bronze<br>
    Armazena os dados processados de forma inicial, como os áudios extraídos dos vídeos e as transcrições automáticas sem limpeza ou estruturação.

    - Silver<br>
    Contém os dados tratados e enriquecidos com informações analíticas, como os sentimentos identificados, timestamps, pontuações de emoção e estrutura narrativa preliminar.

    - Gold<br>
    Reúne os dados refinados e prontos para uso final, como momentos marcantes indexados, segmentos narrativos categorizados e informações otimizadas para tomada de decisão

    - Export<br>
    Diretório destinado a armazenar arquivos finais exportados para visualização e compartilhamento, como relatórios, dashboards, planilhas e arquivos JSON ou CSV utilizados em outras ferramentas (ex: Power BI).

### Ferramentas
- Docker<br>
Contêinerização da aplicação para garantir portabilidade e reprodutibilidade do ambiente de desenvolvimento.<br>
Docker Compose: para orquestrar múltiplos serviços.

- Airflow<br>
Orquestração de tarefas do pipeline de dados (extração, transcrição, análise de sentimentos e indexação narrativa).

- PostgreSQL<br>
Banco de dados relacional utilizado para armazenar dados estruturados, como eventos emocionais, timestamps e indexações narrativas.

- MongoDB<br>
Banco de dados NoSQL utilizado para armazenar dados semiestruturados, como transcrições completas, documentos JSON e blocos narrativos.

- Python<br>
Linguagem principal do projeto, utilizada em todos os scripts de processamento, integração e visualização.<br>
    - Requirements<br>
    Arquivo requirements.txt com as dependências do projeto para recriação rápida do ambiente Python.

    - Moviepy<br>
    Utilizada para extrair e salvar o áudio dos vídeos das sessões de RPG de mesa em arquivos .wav.

    - Yt-dlp<br>
    Utilizada para fazer o download de vídeos a partir de plataformas de streaming, salvando os arquivos localmente e extraindo metadados relevantes em formato .json.

    - Whisper<br>
    Modelo open source de reconhecimento de fala (ASR) utilizado para transcrever os áudios em texto.

    - Feel-it (Emotion detection em português)<br>
    Modelo pré-treinado de NLP usado para identificar emoções predominantes nos trechos das sessões.

    - Indexação narrativa<br>
    Classificação semiestruturada dos trechos com base nas emoções detectadas e palavras-chave, para identificar o papel narrativo (combate, revelação, despedida, clímax, etc.)
    - Logging<br>
    Utilizado para registrar a execução das etapas do pipeline, detectar erros, medir tempo de execução e armazenar histórico de processamento.<br>
    Pode ser implementado com a biblioteca `logging ou `loguru.
- PowerBI<br>
Ferramenta utilizada para construção de dashboards interativos que visualizam os momentos emocionais mais relevantes das sessões.
