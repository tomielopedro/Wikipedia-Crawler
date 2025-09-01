# Web Scraper de Pessoas na Wikipédia

Este projeto implementa um web scraper assíncrono em Python para identificar e coletar informações sobre pessoas na Wikipédia, utilizando técnicas de busca em largura (BFS) e processamento paralelo para otimizar a performance. O objetivo é construir uma árvore de links que represente as conexões entre as páginas de pessoas encontradas, permitindo análises como o "grau de separação" entre indivíduos.




## Descrição do Projeto

O projeto consiste em um crawler que navega pela Wikipédia, identificando páginas que provavelmente pertencem a pessoas. Ele faz isso analisando a presença de certas palavras-chave em infoboxes (caixas de informação) nas páginas. O processo é assíncrono, permitindo que múltiplas requisições HTTP sejam feitas em paralelo, o que acelera significativamente a coleta de dados. Uma vez que uma página é identificada como sendo sobre uma pessoa, seu HTML é salvo localmente e o link é adicionado a uma estrutura de árvore, que mapeia as relações de links entre as pessoas encontradas. Além disso, o projeto inclui um módulo para análise da árvore gerada, permitindo calcular o grau de separação entre duas pessoas e visualizar a rede de conexões.




## Funcionalidades

- **Web Scraping Assíncrono**: Utiliza `asyncio` e `aiohttp` para realizar requisições HTTP de forma não bloqueante, permitindo o processamento simultâneo de múltiplas páginas da Wikipédia.
- **Detecção de Páginas de Pessoas**: Implementa uma heurística baseada na análise de infoboxes para determinar a probabilidade de uma página ser sobre uma pessoa.
- **Filtragem de Links**: Exclui links irrelevantes ou indesejados com base em uma lista de palavras-chave configurável.
- **Salvamento de HTML**: Armazena o conteúdo HTML das páginas de pessoas encontradas em um diretório local para análise posterior.
- **Construção de Árvore de Links**: Cria uma estrutura de dados em árvore (`LinkNode`) que representa as relações de links entre as páginas de pessoas, permitindo rastrear a origem da descoberta.
- **Monitoramento de Limite**: Interrompe o scraping automaticamente quando um número predefinido de pessoas é encontrado.
- **Geração de Relatório Final**: Ao término da execução, exibe um relatório consolidado com métricas como tempo total, número de pessoas encontradas, links verificados e requisições HTTP.
- **Visualização da Árvore de Conexões**: Um módulo separado (`notebook`) permite carregar a árvore de links salva e visualizá-la graficamente usando `networkx` e `matplotlib`.
- **Cálculo de Grau de Separação**: Funcionalidade para determinar o menor caminho (grau de separação) entre duas pessoas na árvore de conexões.




## Eficiência

Este projeto foi projetado com a eficiência em mente, aproveitando os seguintes recursos:

- **Programação Assíncrona (`asyncio`, `aiohttp`)**: A utilização de `asyncio` e `aiohttp` permite que o scraper execute múltiplas operações de I/O (como requisições HTTP) concorrentemente, sem a necessidade de threads ou processos adicionais. Isso é crucial para web scraping, onde a maior parte do tempo é gasta esperando por respostas de servidores. Ao invés de esperar por uma requisição terminar antes de iniciar a próxima, o programa pode iniciar várias requisições e processar as respostas à medida que chegam, maximizando a utilização da rede e minimizando o tempo ocioso.

- **Limitação de Conexões Concorrentes (`MAX_CONEXOES`)**: O parâmetro `MAX_CONEXOES` controla o número máximo de requisições HTTP que podem ser feitas simultaneamente. Isso evita sobrecarregar o servidor da Wikipédia e também o próprio sistema que executa o scraper, garantindo um comportamento responsável e eficiente. Um número otimizado de conexões concorrentes pode reduzir significativamente o tempo total de execução.

- **Filtragem Inteligente de Links**: A função `extrair_links_validos` utiliza expressões regulares e uma lista de palavras a serem excluídas para filtrar links irrelevantes ou que não levam a artigos de pessoas. Isso reduz a quantidade de páginas a serem processadas, focando os recursos computacionais apenas no que é relevante para o objetivo do projeto.

- **Detecção Heurística de Pessoas (`eh_pessoa`)**: A função `eh_pessoa` rapidamente avalia a probabilidade de uma página ser sobre uma pessoa com base em palavras-chave presentes na infobox. Isso evita o processamento completo de páginas que não são de interesse, economizando tempo e recursos de parsing.

- **Salvamento Local de HTML**: Ao salvar o HTML das páginas de pessoas localmente, o projeto evita a necessidade de fazer requisições repetidas para as mesmas páginas, caso sejam necessárias análises futuras ou depuração. Isso contribui para a eficiência a longo prazo e reduz a carga sobre os servidores externos.

- **Monitoramento de Limite (`LIMITE_PESSOAS`)**: A capacidade de definir um limite para o número de pessoas a serem encontradas e de interromper o processo automaticamente ao atingir esse limite garante que o scraper não execute indefinidamente, economizando recursos computacionais e tempo quando um número suficiente de dados já foi coletado.





## Como Usar

Para executar este projeto, siga os passos abaixo:

### Pré-requisitos

Certifique-se de ter o Python 3.8 ou superior instalado em seu sistema. Além disso, você precisará das seguintes bibliotecas Python:

- `aiohttp`
- `beautifulsoup4`
- `regex`
- `aiofiles`
- `PyYAML`
- `networkx` (para o notebook de visualização)
- `matplotlib` (para o notebook de visualização)

Você pode instalar todas as dependências usando o `pip` e o arquivo `requirements.txt` fornecido:

```bash
pip install -r requirements.txt
```

### Configuração

As configurações do scraper são definidas no arquivo `configuration.yaml`. Você pode ajustar os seguintes parâmetros:

- `URL_INICIAL`: A URL da página da Wikipédia a partir da qual o scraping será iniciado. (Padrão: `https://pt.wikipedia.org`)
- `LIMITE_PESSOAS`: O número máximo de pessoas a serem encontradas antes que o scraper pare. (Padrão: `1200`)
- `MAX_CONEXOES`: O número máximo de conexões HTTP simultâneas. (Padrão: `50`)
- `PROB_PESSOA`: A probabilidade mínima (0.0 a 1.0) para uma página ser considerada sobre uma pessoa. (Padrão: `0.6`)
- `TIMEOUT_GERAL`: O tempo limite em segundos para as requisições HTTP. (Padrão: `10`)
- `PASTA_HTML`: O diretório onde os arquivos HTML das páginas de pessoas serão salvos. (Padrão: `data/paginas_html`)
- `PASTA_ARVORE`: O diretório onde o arquivo da árvore de conexões entre páginas. (Padrão: `data/arvore_links.txt`)
- `PASTA_PALAVRAS_EXCLUIR`: O diretório onde o arquivo de palavras para excluir dos links será salvo. (Padrão: `data/palavras_para_excluir.txt`)


Exemplo de `configuration.yaml`:

```yaml
URL_INICIAL: "https://pt.wikipedia.org"
LIMITE_PESSOAS: 50
MAX_CONEXOES: 50
PROB_PESSOA: 0.6
TIMEOUT_GERAL: 10
PASTA_HTML: "data/paginas_html"
PASTA_ARVORE: "data/arvore_links.txt"
PASTA_PALAVRAS_EXCLUIR: "data/palavras_para_excluir.txt"
```

Você também pode criar um arquivo `data/palavras_para_excluir.txt` (um por linha) para listar palavras-chave que, se presentes em um link, farão com que ele seja ignorado. Isso é útil para evitar páginas de desambiguação, listas, etc.

### Executando o Scraper

Para iniciar o web scraper, execute o arquivo `main.py`:

```bash
python main.py
```

O scraper começará a navegar pela Wikipédia, procurando por páginas de pessoas. O progresso será exibido no console, e os arquivos HTML das páginas de pessoas encontradas serão salvos no diretório especificado em `PASTA_HTML`.

Ao final da execução (ou quando o limite de pessoas for atingido), um relatório final será exibido, e a árvore de links será salva em `data/arvore_links.txt`.

### Visualizando a Árvore de Conexões

Após a execução do scraper, você pode visualizar a árvore de conexões gerada e calcular o grau de separação entre pessoas usando o código fornecido na seção `notebook` do arquivo `pasted_content.txt` (que pode ser adaptado para um Jupyter Notebook ou script Python separado). Certifique-se de que o arquivo `data/arvore_links.txt` foi gerado.

Exemplo de uso (adaptado do código original):


### Estrutura do Projeto

```
.  
├── main.py
├── requirements.txt
├── configuration.yaml
├── README.md
└── data/
    ├── paginas_html/ (criado automaticamente)
    ├── palavras_para_excluir.txt (opcional)
    └── arvore_links.txt (gerado após execução)
```

- `main.py`: O script principal do web scraper.
- `requirements.txt`: Lista as dependências Python do projeto.
- `configuration.yaml`: Contém as configurações do scraper.
- `README.md`: Este arquivo, com a documentação do projeto.
- `data/`: Diretório para armazenar dados gerados e arquivos de configuração adicionais.
  - `paginas_html/`: Subdiretório onde os arquivos HTML das páginas de pessoas são salvos.
  - `palavras_para_excluir.txt`: Arquivo opcional para listar palavras-chave a serem excluídas na filtragem de links.
  - `arvore_links.txt`: Arquivo gerado que contém a representação da árvore de links de pessoas encontradas.

