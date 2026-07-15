# Projeto Avaliativo - Análise de dados

## Pipeline ETL de Dados — Viagens a Serviço do Governo Federal

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-blue?logo=postgresql)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-blue?logo=pandas)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-red)
![Git](https://img.shields.io/badge/Git-Versionamento-orange?logo=git)
![Status](https://img.shields.io/badge/Status-Concluído-brightgreen)

---

## Sobre o projeto

Este projeto foi desenvolvido com o objetivo de construir um **pipeline ETL completo**, utilizando dados públicos de **Viagens a Serviço do Governo Federal**, disponibilizados pelo Portal da Transparência.

O pipeline realiza desde a extração automatizada dos arquivos até a geração de análises e indicadores de negócio, seguindo uma arquitetura em camadas (**Raw → Silver → Gold**) amplamente utilizada em projetos de Engenharia de Dados.

---

# Objetivos

O projeto foi desenvolvido para:

- Automatizar o download dos dados a partir do Google Drive;
- Preservar os dados originais na camada Raw;
- Limpar, transformar e tipar os dados na camada Silver;
- Garantir integridade referencial entre as tabelas;
- Calcular métricas derivadas;
- Responder perguntas de negócio;
- Produzir visualizações utilizando Python.

---

# Arquitetura do Pipeline

```text
                    Google Drive
                          │
                          ▼
              Download automático (.zip)
                          │
                          ▼
                    data/raw (CSV)
                          │
                          ▼
                PostgreSQL - Camada Raw
                          │
                          ▼
                 Limpeza e Transformação
                          │
                          ▼
               PostgreSQL - Camada Silver
                          │
                          ▼
             Notebook de Análises (Gold)
```

---

# Tecnologias Utilizadas

- Python 3.13
- PostgreSQL
- SQL
- SQLAlchemy
- Psycopg2
- Pandas
- Matplotlib
- Jupyter Notebook
- gdown
- python-dotenv
- Git
- GitHub
- Visual Studio Code
- pgAdmin

---

# Estrutura do Projeto

```text
projeto_analise_dados/
│
├── data/
│   ├── raw/
│   ├── silver/
│   └── gold/
│
├── notebooks/
│   └── 3_analise.ipynb
│
├── 0_criar_banco.sql
├── 1_extrair.py
├── 2_transformar.py
├── banco.py
├── config.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

# Camadas do Projeto

## Raw

Responsável por preservar uma cópia fiel dos arquivos CSV.

Características:

- Todos os campos inicialmente armazenados como texto;
- Datas mantidas no formato original;
- Valores monetários preservados;
- Nenhuma transformação aplicada.

Tabelas:

- raw_viagem
- raw_pagamento
- raw_passagem
- raw_trecho

---

## Silver

Responsável pela limpeza, padronização e transformação dos dados.

Transformações realizadas:

- Conversão de datas;
- Conversão de valores monetários;
- Conversão de tipos;
- Remoção de registros inválidos;
- Remoção de duplicidades;
- Padronização de textos;
- Cálculo de colunas derivadas;
- Integridade referencial;
- Aplicação de constraints.

Tabelas:

- silver_viagem
- silver_pagamento
- silver_passagem
- silver_trecho

---

## Gold

Representada pelo notebook:

```text
notebooks/3_analise.ipynb
```

Nele são realizadas consultas SQL, agregações, visualizações e análises para responder às perguntas de negócio propostas.

---

# Download dos Dados

Os dados são baixados automaticamente a partir de um arquivo ZIP hospedado no Google Drive.

Arquivos utilizados:

- 2025_Viagem.csv
- 2025_Pagamento.csv
- 2025_Passagem.csv
- 2025_Trecho.csv

O download é realizado automaticamente pelo script:

```text
1_extrair.py
```

utilizando o pacote **gdown**.

---

# Configuração do Ambiente

## 1. Clonar o repositório

```bash
git clone https://github.com/fgofilipe/projeto_analise_de_dados.git
```

Entrar na pasta:

```bash
cd projeto_analise_de_dados
```

---

## 2. Criar ambiente virtual

Windows

```bash
python -m venv venv
```

Ativar:

```bash
venv\Scripts\activate
```

---

## 3. Instalar dependências

```bash
pip install -r requirements.txt
```

---

## 4. Configurar o arquivo .env

Crie um arquivo chamado:

```text
.env
```

com base em:

```text
.env.example
```

Preencha:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=analise_dados
DB_USER=postgres
DB_PASSWORD=sua_senha

DRIVE_FILE_ID=id_do_google_drive
```

---

# Execução

## 1. Criar o banco

Execute o arquivo:

```text
0_criar_banco.sql
```

Serão criadas:

- 4 tabelas Raw
- 4 tabelas Silver
- Primary Keys
- Foreign Keys
- Constraints

---

## 2. Extração

Execute:

```bash
python 1_extrair.py
```

O script:

- realiza download do ZIP;
- extrai os CSVs;
- valida os arquivos;
- limpa as tabelas Raw;
- carrega os dados no PostgreSQL;
- trata exceções.

---

## 3. Transformação

Execute:

```bash
python 2_transformar.py
```

Transformações realizadas:

- limpeza;
- tipagem;
- datas;
- valores monetários;
- cálculo de métricas;
- integridade referencial;
- remoção de duplicidades;
- carga da camada Silver.

---

## 4. Análise

Abra:

```text
notebooks/3_analise.ipynb
```

Execute todas as células.

O notebook responde às perguntas de negócio utilizando SQL, Pandas e Matplotlib.

---

# Colunas Calculadas

## Valor Total

```text
valor_total =
valor_diarias +
valor_passagens +
valor_devolucao +
valor_outros_gastos
```

## Duração da Viagem

```text
duracao_dias =
data_fim - data_inicio
```

---

# Perguntas de Negócio Respondidas

O notebook responde:

- Visão geral dos dados;
- Órgãos com maior gasto total;
- Destinos com maior quantidade de viagens;
- Destinos com maior custo médio;
- Viagem de maior duração;
- Tipo de pagamento com maior valor médio;
- Meio de transporte mais utilizado;
- Meio de transporte menos utilizado;
- Órgãos com maior quantidade de viagens;
- Evolução mensal dos gastos.

---

# Tratamentos Realizados

Durante a construção do pipeline foram aplicados:

- Conversão de datas;
- Conversão de números brasileiros;
- Limpeza de espaços;
- Padronização de textos;
- Conversão para DECIMAL;
- Conversão para DATE;
- Conversão para INTEGER;
- Remoção de valores inválidos;
- Remoção de duplicidades;
- Filtragem por chaves estrangeiras;
- Aplicação de constraints;
- Tratamento de exceções.

---

# Boas Práticas Utilizadas

- Organização em camadas;
- Configuração via `.env`;
- Versionamento com Git;
- Código modular;
- Download automatizado;
- Tratamento de exceções;
- Encerramento das conexões com o banco;
- Integridade referencial;
- Notebook documentado;
- Funções reutilizáveis.

---

# Resultados

O pipeline permite:

- automatizar a ingestão dos dados;
- preservar os dados originais;
- produzir uma camada analítica consistente;
- responder perguntas de negócio;
- gerar visualizações para apoio à tomada de decisão.

---


**Filipe de Oliveira Gomes**

GitHub

https://github.com/fgofilipe

LinkedIn

https://www.linkedin.com/in/filipe-oliveirahrs/

---

## Licença

Este projeto foi desenvolvido para fins acadêmicos, utilizando dados públicos disponibilizados pelo Portal da Transparência do Governo Federal.