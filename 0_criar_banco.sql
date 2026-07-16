DROP TABLE IF EXISTS silver_trecho;
DROP TABLE IF EXISTS silver_passagem;
DROP TABLE IF EXISTS silver_pagamento;
DROP TABLE IF EXISTS silver_viagem;

DROP TABLE IF EXISTS raw_trecho;
DROP TABLE IF EXISTS raw_passagem;
DROP TABLE IF EXISTS raw_pagamento;
DROP TABLE IF EXISTS raw_viagem;

-- CAMADA RAW

CREATE TABLE raw_viagem (
    id_viagem VARCHAR(20),
    num_proposta VARCHAR(20),
    situacao VARCHAR(50),
    viagem_urgente VARCHAR(5),
    justificativa_urgencia TEXT,
    cod_orgao_superior VARCHAR(20),
    nome_orgao_superior VARCHAR(255),
    cod_orgao_solicitante VARCHAR(20),
    nome_orgao_solicitante VARCHAR(255),
    cpf_viajante VARCHAR(20),
    nome_viajante VARCHAR(255),
    cargo VARCHAR(255),
    funcao VARCHAR(50),
    descricao_funcao TEXT,
    data_inicio VARCHAR(20),
    data_fim VARCHAR(20),
    destinos TEXT,
    motivo TEXT,
    valor_diarias VARCHAR(30),
    valor_passagens VARCHAR(30),
    valor_devolucao VARCHAR(30),
    valor_outros_gastos VARCHAR(30)
);


CREATE TABLE raw_pagamento (
    id_viagem VARCHAR(20),
    num_proposta VARCHAR(20),
    cod_orgao_superior VARCHAR(20),
    nome_orgao_superior VARCHAR(255),
    cod_orgao_pagador VARCHAR(20),
    nome_orgao_pagador VARCHAR(255),
    cod_unidade_gestora_pagadora VARCHAR(20),
    nome_unidade_gestora_pagadora VARCHAR(255),
    tipo_pagamento VARCHAR(50),
    valor VARCHAR(30)
);


CREATE TABLE raw_passagem (
    id_viagem VARCHAR(20),
    num_proposta VARCHAR(20),
    meio_transporte VARCHAR(50),
    pais_origem_ida VARCHAR(60),
    uf_origem_ida VARCHAR(60),
    cidade_origem_ida VARCHAR(80),
    pais_destino_ida VARCHAR(60),
    uf_destino_ida VARCHAR(60),
    cidade_destino_ida VARCHAR(80),
    pais_origem_volta VARCHAR(60),
    uf_origem_volta VARCHAR(60),
    cidade_origem_volta VARCHAR(80),
    pais_destino_volta VARCHAR(60),
    uf_destino_volta VARCHAR(60),
    cidade_destino_volta VARCHAR(80),
    valor_passagem VARCHAR(30),
    taxa_servico VARCHAR(30),
    data_emissao VARCHAR(20),
    hora_emissao VARCHAR(20)
);


CREATE TABLE raw_trecho (
    id_viagem VARCHAR(20),
    num_proposta VARCHAR(20),
    sequencia_trecho VARCHAR(20),
    origem_data VARCHAR(20),
    origem_pais VARCHAR(60),
    origem_uf VARCHAR(60),
    origem_cidade VARCHAR(80),
    destino_data VARCHAR(20),
    destino_pais VARCHAR(60),
    destino_uf VARCHAR(60),
    destino_cidade VARCHAR(80),
    meio_transporte VARCHAR(50),
    numero_diarias VARCHAR(30),
    missao VARCHAR(20)
);


-- CAMADA SILVER

CREATE TABLE silver_viagem (
    id_viagem BIGINT PRIMARY KEY,
    num_proposta VARCHAR(20),
    situacao VARCHAR(50),
    viagem_urgente VARCHAR(5),
    justificativa_urgencia TEXT,
    cod_orgao_superior VARCHAR(20),

    nome_orgao_superior VARCHAR(255)
        CONSTRAINT nn_viagem_nome_orgao_superior NOT NULL,

    cod_orgao_solicitante VARCHAR(20),
    nome_orgao_solicitante VARCHAR(255),
    cpf_viajante VARCHAR(20),
    nome_viajante VARCHAR(255),
    cargo VARCHAR(255),
    funcao VARCHAR(255),
    descricao_funcao TEXT,
    data_inicio DATE,
    data_fim DATE,
    destinos VARCHAR(4000),
    motivo VARCHAR(4000),

    valor_diarias DECIMAL(10,2)
        CONSTRAINT chk_viagem_valor_diarias
        CHECK (valor_diarias >= 0),

    valor_passagens DECIMAL(10,2),
    valor_devolucao DECIMAL(10,2),
    valor_outros_gastos DECIMAL(10,2),
    valor_total DECIMAL(12,2),
    duracao_dias INT
);


CREATE TABLE silver_pagamento (
    id_pagamento SERIAL PRIMARY KEY,
    id_viagem BIGINT,
    num_proposta VARCHAR(20),
    cod_orgao_superior VARCHAR(20),
    nome_orgao_superior VARCHAR(255),
    cod_orgao_pagador VARCHAR(20),
    nome_orgao_pagador VARCHAR(255),
    cod_unidade_gestora_pagadora VARCHAR(30),
    nome_unidade_gestora_pagadora VARCHAR(255),

    tipo_pagamento VARCHAR(50)
        CONSTRAINT nn_pagamento_tipo_pagamento NOT NULL,

    valor DECIMAL(10,2)
        CONSTRAINT chk_pagamento_valor
        CHECK (valor >= 0),

    CONSTRAINT fk_pagamento_viagem
        FOREIGN KEY (id_viagem)
        REFERENCES silver_viagem(id_viagem)
);


CREATE TABLE silver_passagem (
    id_passagem SERIAL PRIMARY KEY,
    id_viagem BIGINT,
    num_proposta VARCHAR(20),
    meio_transporte VARCHAR(50),
    pais_origem_ida VARCHAR(60),
    uf_origem_ida VARCHAR(40),
    cidade_origem_ida VARCHAR(80),
    pais_destino_ida VARCHAR(60),
    uf_destino_ida VARCHAR(40),
    cidade_destino_ida VARCHAR(80),
    pais_origem_volta VARCHAR(60),
    uf_origem_volta VARCHAR(40),
    cidade_origem_volta VARCHAR(80),
    pais_destino_volta VARCHAR(60),
    uf_destino_volta VARCHAR(40),
    cidade_destino_volta VARCHAR(80),

    valor_passagem DECIMAL(10,2)
        CONSTRAINT chk_passagem_valor_passagem
        CHECK (valor_passagem >= 0),

    taxa_servico DECIMAL(10,2)
        CONSTRAINT chk_passagem_taxa_servico
        CHECK (taxa_servico >= 0),

    data_emissao DATE,
    hora_emissao TIME,

    CONSTRAINT fk_passagem_viagem
        FOREIGN KEY (id_viagem)
        REFERENCES silver_viagem(id_viagem)
);


CREATE TABLE silver_trecho (
    id_trecho SERIAL PRIMARY KEY,
    id_viagem BIGINT,
    num_proposta VARCHAR(20),
    sequencia_trecho INT,
    origem_data DATE,
    origem_pais VARCHAR(60),
    origem_uf VARCHAR(40),
    origem_cidade VARCHAR(80),
    destino_data DATE,
    destino_pais VARCHAR(60),
    destino_uf VARCHAR(40),
    destino_cidade VARCHAR(80),
    meio_transporte VARCHAR(50),

    numero_diarias DECIMAL(10,2)
        CONSTRAINT chk_trecho_numero_diarias
        CHECK (numero_diarias >= 0),

    missao VARCHAR(5),

    CONSTRAINT uq_trecho_viagem_sequencia
        UNIQUE (id_viagem, sequencia_trecho),

    CONSTRAINT fk_trecho_viagem
        FOREIGN KEY (id_viagem)
        REFERENCES silver_viagem(id_viagem)
);