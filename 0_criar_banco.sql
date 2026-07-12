DROP TABLE IF EXISTS raw_viagem;
DROP TABLE IF EXISTS raw_pagamento;
DROP TABLE IF EXISTS raw_passagem;
DROP TABLE IF EXISTS raw_trecho;

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

DROP TABLE IF EXISTS silver_trecho;
DROP TABLE IF EXISTS silver_passagem;
DROP TABLE IF EXISTS silver_pagamento;
DROP TABLE IF EXISTS silver_viagem;

CREATE TABLE silver_viagem (
    id_viagem BIGINT PRIMARY KEY,
    num_proposta VARCHAR(30) NOT NULL,
    situacao VARCHAR(80) NOT NULL,
    viagem_urgente VARCHAR(5) NOT NULL CHECK (viagem_urgente IN ('Sim', 'Não')),
    justificativa_urgencia TEXT,
    cod_orgao_superior VARCHAR(20) NOT NULL,
    nome_orgao_superior VARCHAR(255) NOT NULL,
    cod_orgao_solicitante VARCHAR(20) NOT NULL,
    nome_orgao_solicitante VARCHAR(255) NOT NULL,
    cpf_viajante VARCHAR(20),
    nome_viajante VARCHAR(255) NOT NULL,
    cargo VARCHAR(255),
    funcao VARCHAR(80),
    descricao_funcao TEXT,
    data_inicio DATE NOT NULL,
    data_fim DATE NOT NULL,
    destinos TEXT NOT NULL,
    motivo TEXT,
    valor_diarias NUMERIC(14,2) NOT NULL DEFAULT 0,
    valor_passagens NUMERIC(14,2) NOT NULL DEFAULT 0,
    valor_devolucao NUMERIC(14,2) NOT NULL DEFAULT 0,
    valor_outros_gastos NUMERIC(14,2) NOT NULL DEFAULT 0,
    valor_total NUMERIC(14,2) NOT NULL DEFAULT 0,
    duracao_dias INTEGER NOT NULL,
    
    CONSTRAINT chk_datas_viagem CHECK (data_fim >= data_inicio),
    CONSTRAINT chk_duracao_viagem CHECK (duracao_dias >= 0),
    CONSTRAINT chk_valores_viagem CHECK (
        valor_diarias >= 0 AND
        valor_passagens >= 0 AND
        valor_devolucao >= 0 AND
        valor_outros_gastos >= 0
    )
);

CREATE TABLE silver_pagamento (
    id_pagamento SERIAL PRIMARY KEY,
    id_viagem BIGINT NOT NULL,
    num_proposta VARCHAR(30) NOT NULL,
    cod_orgao_superior VARCHAR(20),
    nome_orgao_superior VARCHAR(255) NOT NULL,
    cod_orgao_pagador VARCHAR(20),
    nome_orgao_pagador VARCHAR(255) NOT NULL,
    cod_unidade_gestora_pagadora VARCHAR(30) NOT NULL,
    nome_unidade_gestora_pagadora VARCHAR(255) NOT NULL,
    tipo_pagamento VARCHAR(80) NOT NULL,
    valor NUMERIC(14,2) NOT NULL,

    CONSTRAINT fk_pagamento_viagem
        FOREIGN KEY (id_viagem)
        REFERENCES silver_viagem(id_viagem),

    CONSTRAINT chk_valor_pagamento CHECK (valor >= 0)
);

CREATE TABLE silver_passagem (
    id_passagem SERIAL PRIMARY KEY,
    id_viagem BIGINT NOT NULL,
    num_proposta VARCHAR(30) NOT NULL,
    meio_transporte VARCHAR(80) NOT NULL,
    pais_origem_ida VARCHAR(80) NOT NULL,
    uf_origem_ida VARCHAR(80),
    cidade_origem_ida VARCHAR(120) NOT NULL,
    pais_destino_ida VARCHAR(80) NOT NULL,
    uf_destino_ida VARCHAR(80),
    cidade_destino_ida VARCHAR(120) NOT NULL,
    pais_origem_volta VARCHAR(80) NOT NULL,
    uf_origem_volta VARCHAR(80),
    cidade_origem_volta VARCHAR(120) NOT NULL,
    pais_destino_volta VARCHAR(80) NOT NULL,
    uf_destino_volta VARCHAR(80),
    cidade_destino_volta VARCHAR(120) NOT NULL,
    valor_passagem NUMERIC(14,2) NOT NULL,
    taxa_servico NUMERIC(14,2) NOT NULL,
    data_emissao DATE,
    hora_emissao TIME,

    CONSTRAINT fk_passagem_viagem
        FOREIGN KEY (id_viagem)
        REFERENCES silver_viagem(id_viagem),

    CONSTRAINT chk_valores_passagem CHECK (
        valor_passagem >= 0 AND taxa_servico >= 0
    )
);

CREATE TABLE silver_trecho (
    id_trecho SERIAL PRIMARY KEY,
    id_viagem BIGINT NOT NULL,
    num_proposta VARCHAR(30) NOT NULL,
    sequencia_trecho INTEGER NOT NULL,
    origem_data DATE NOT NULL,
    origem_pais VARCHAR(80) NOT NULL,
    origem_uf VARCHAR(80),
    origem_cidade VARCHAR(120) NOT NULL,
    destino_data DATE NOT NULL,
    destino_pais VARCHAR(80) NOT NULL,
    destino_uf VARCHAR(80),
    destino_cidade VARCHAR(120) NOT NULL,
    meio_transporte VARCHAR(80) NOT NULL,
    numero_diarias NUMERIC(10,2) NOT NULL,
    missao VARCHAR(5) NOT NULL CHECK (missao IN ('Sim', 'Não')),

    CONSTRAINT fk_trecho_viagem
        FOREIGN KEY (id_viagem)
        REFERENCES silver_viagem(id_viagem),

    CONSTRAINT unq_trecho_viagem_sequencia
        UNIQUE (id_viagem, sequencia_trecho),

    CONSTRAINT chk_datas_trecho CHECK (destino_data >= origem_data),
    CONSTRAINT chk_numero_diarias CHECK (numero_diarias >= 0)
);