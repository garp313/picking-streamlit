📦 Picking & Arrumação Hub — Documentação de Uso
Ferramenta interna para importação, visualização, análise e exportação de dados de inventário de picking e arrumação.

Visão Geral
O Picking & Arrumação Hub é um painel interativo desenvolvido em Python com Streamlit. Ele permite que a equipe:

Importe dados de estoque direto do Google Sheets ou de arquivos locais (CSV/Excel)
Filtre e visualize os dados por Produto, Cor e Grade/Tamanho
Acompanhe métricas e gráficos do inventário em tempo real
Exporte os dados em formato JSON organizado (sem colunas de descrição internas)
Envie os dados para uma API externa via HTTP (sandbox)
🗂️ Estrutura da Interface

┌─────────────────────────────────────────────────────────────┐
│  Sidebar (Painel Lateral)      │  Área Principal (Abas)     │
│  ─────────────────────         │  ──────────────────────     │
│  ⚙️ Origem dos Dados           │  📊 Dados & Filtros         │
│  ├─ Google Sheets              │  📈 Dashboard Analítico     │
│  └─ Arquivo Local              │  🚀 Pipeline & API          │
│                                │                             │
│  🔍 Importar da Nuvem          │                             │
│  🗑️ Limpar Todos os Dados      │                             │
│  ⬇️ Baixar Arquivo JSON        │                             │
└─────────────────────────────────────────────────────────────┘
📥 Passo a Passo: Como Usar
1. Escolher a Fonte de Dados
No painel lateral (sidebar), selecione a origem dos seus dados:

Opção A — Google Sheets (Planilha Nuvem)
Marque "Usar planilha padrão oficial" para carregar automaticamente a planilha Oficial de Arrumação.
Ou desmarque e cole o ID ou URL de outra planilha do Google Sheets.
IMPORTANT

A planilha do Google Sheets deve estar configurada para acesso público (compartilhada com "Qualquer pessoa com o link"). Caso contrário, o botão de importação retornará erro.

Clique em 🔍 Importar da Nuvem.
Opção B — Arquivo Local (CSV/Excel)
Selecione "Carregar Arquivo Local (CSV/Excel)".
Clique em "Browse files" e selecione um arquivo .csv, .xlsx ou .xls do seu computador.
O carregamento é automático após a seleção.
2. Explorar Dados e Filtros (Aba "📊 Dados & Filtros")
Após carregar os dados, a aba principal exibirá:

Filtros interativos por:

Produto — código do produto
Cor — código de cor
Grade/Tamanho — ex.: PP, P, M, G, GG
Uma tabela completa com os dados filtrados, reordenada automaticamente para exibir as colunas principais primeiro: Produto, Cor, Tamanho, Grade, Quantidade.

TIP

O contador acima da tabela indica quantos registros estão sendo exibidos após os filtros ativos.

3. Analisar o Dashboard (Aba "📈 Dashboard Analítico")
Esta aba exibe métricas e gráficos gerados a partir dos dados filtrados:

Métrica	Descrição
🛒 SKUs Únicos	Quantidade de linhas (combinações produto+cor+grade)
👕 Total de Peças	Soma da coluna Quantidade
📦 Média p/ SKU	Média de peças por linha
🎨 Produtos / Cores	Contagem de produtos e cores distintos
Gráficos disponíveis:

🍩 Donut — Volume por Grade/Tamanho: distribuição percentual por tamanho
📊 Top 10 Produtos por Volume: barras horizontais com os produtos mais volumosos
🎨 Top 15 Cores por Volume: barras horizontais das cores com maior estoque
4. Exportar o JSON (Sidebar e Aba "🚀 Pipeline")
O botão ⬇️ Baixar Arquivo JSON fica disponível na sidebar assim que os dados forem carregados, e também dentro da aba Pipeline.

O arquivo gerado é nomeado automaticamente com a data atual: arrumacao_DD-MM-AAAA.json
Colunas com desc no nome (ex.: desc_produto) são removidas automaticamente do JSON exportado para manter o payload limpo
A coluna Quantidade é convertida para número inteiro no JSON
Exemplo de estrutura do JSON exportado:

json

[
    {
        "Produto": "12345",
        "Cor": "001",
        "Tamanho": "M",
        "Grade": "M",
        "Quantidade": 42
    },
    ...
]
5. Enviar para API Externa (Aba "🚀 Pipeline — API Sandbox")
NOTE

Este recurso é opcional e voltado para integrações técnicas. Não é necessário para o uso cotidiano da ferramenta.

Na aba 🚀 Pipeline de Exportação & API, acesse a coluna da direita.
Ative a opção "Ativar envio de dados para API externa".
Preencha:
URL da API de Destino — ex.: https://api.seuservico.com/v1/picking
Método HTTP — POST, PUT ou PATCH
Headers — no formato JSON (o campo já vem preenchido com um template padrão)
Clique em 🚀 Enviar Carga de Dados.
O painel exibirá:

✅ Código de status HTTP da resposta
⏱️ Tempo de resposta em segundos
📋 Headers e corpo da resposta da API
📜 Histórico dos últimos 3 envios da sessão
🔄 Resetar Dados
Para limpar todos os dados carregados e começar do zero, clique em 🗑️ Limpar Todos os Dados na sidebar.

⚙️ Colunas Esperadas na Planilha
A ferramenta reconhece automaticamente as seguintes colunas (não sensível a maiúsculas):

Coluna	Função
Produto	Código ou nome do produto
Cor	Código de cor
Tamanho	Tamanho do item
Grade	Grade do item (PP, P, M, G, GG...)
Quantidade ou Qtd	Quantidade em estoque
desc_produto	Descrição textual (exibida nos gráficos, omitida no JSON)
NOTE

Colunas fora deste padrão serão mantidas no final da tabela e incluídas no JSON exportado.

❓ Problemas Comuns
Problema	Solução
"Erro ao ler planilha"	Verifique se a planilha está pública no Google Sheets
JSON vazio ou sem dados	Certifique-se de ter carregado os dados antes de baixar
Gráficos não aparecem	Verifique se as colunas Quantidade e Grade/Produto existem na planilha
Erro 401/403 na API	Verifique o token de autorização nos headers
Erro de conexão na API	Verifique a URL e se o serviço está acessível
