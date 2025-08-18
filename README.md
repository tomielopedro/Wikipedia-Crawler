# Wikipedia-Crawler

## Plano de Trabalho – Projeto de Coleta e Grau de Separação (Wikipédia)

## Etapa 1 – Preparação do ambiente
- [ ] Definir pasta onde os arquivos `.html` serão salvos
- [ ] Criar estrutura inicial do notebook (seções)

## Etapa 2 – Desenvolvimento do Crawler
- [x] Criar função para fazer requisição e obter o conteúdo da página
- [x] Criar função para extrair todos os links do corpo da página
- [ ] Filtrar links:  
  - [ ] Apenas links da Wikipedia em português  
  - [ ] Evitar links externos  
  - [ ] Evitar links já visitados
- [ ] Desenvolver método para identificar se a página é sobre uma pesso
- [ ] Implementar loop de navegação até coletar 1.000 páginas válidas
- [ ] Exibir proporção `páginas_coletadas / páginas_visitadas`

## Etapa 3 – Pré-processamento das páginas coletadas
- [ ] Ler arquivos `.html` salvos
- [ ] Construir um grafo onde:  
  - vértices = pessoas  
  - arestas = links entre as páginas

## Etapa 4 – Algoritmo dos 6 Graus de Separação
- [ ] Definir função que recebe nome da pessoa A e nome da pessoa B
- [ ] Implementar busca (ex: BFS) para encontrar o caminho mais curto
- [ ] Exibir sequência de pessoas do caminho encontrado
- [ ] Tratar caso não exista conexão

## Etapa 5 – Testes e Validação
- [ ] Testar o crawler com um número pequeno de páginas (ex: 20)  
- [ ] Validar se as páginas realmente correspondem a pessoas
- [ ] Testar o grau de separação com pessoas conhecidas (ex: políticos, artistas, etc.)

## Etapa 6 – Documentação e Repositório
- [ ] Adicionar instruções de execução (README ou células Markdown)
- [ ] Adicionar link para repositório com os dados coletados
- [ ] Comentar o código onde necessário
