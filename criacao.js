-- Tabela principal: Dados do Contrato
CREATE TABLE contratos (
    id_contrato INT PRIMARY KEY AUTO_INCREMENT,
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    status_contrato ENUM('pendente', 'assinado', 'cancelado', 'alterado') DEFAULT 'pendente',

    -- Dados do Contratado
    nome_contratado VARCHAR(150) NOT NULL,
    cpf_contratado VARCHAR(14) NOT NULL,
    endereco_contratado VARCHAR(255) NOT NULL,
    telefone_contratado VARCHAR(20) NOT NULL,

    -- Dados do Contratante
    nome_contratante VARCHAR(150) NOT NULL,
    cpf_contratante VARCHAR(14) NOT NULL,
    endereco_contratante VARCHAR(255) NOT NULL,
    telefone_contratante VARCHAR(20) NOT NULL,

    -- Dados do Evento
    tipo_evento VARCHAR(100) NOT NULL,
    observacao_evento TEXT,
    data_evento DATE NOT NULL,
    horario_inicio TIME NOT NULL,
    horario_termino TIME NOT NULL,
    qtd_mesas INT DEFAULT 15,
    uso_piscina ENUM('sim', 'sem_uso', 'nao') NOT NULL,
    uso_som ENUM('nao', 'sim', 'sim_microfone') NOT NULL,
    horario_entrega_bebidas TIME NOT NULL,
    horario_recebimento_espaco TIME NOT NULL,
    pula_pula BOOLEAN DEFAULT FALSE,
    piscina_bolinha BOOLEAN DEFAULT FALSE,

    -- Dados de Pagamento
    valor_locacao DECIMAL(10,2) NOT NULL,
    valor_entrada DECIMAL(10,2) NOT NULL,
    forma_pagamento_entrada ENUM('pix', 'dinheiro', 'transferencia') NOT NULL,
    data_vencimento_restante DATE NOT NULL,

    -- Aceite dos Termos (sem acentos nos nomes)
    aceite_funcionamento BOOLEAN NOT NULL,
    aceite_uso_espaco BOOLEAN NOT NULL,
    aceite_obrigacoes_contratado BOOLEAN NOT NULL,
    aceite_obrigacoes_contratante BOOLEAN NOT NULL,
    aceite_cancelamento BOOLEAN NOT NULL,
    aceite_gerais BOOLEAN NOT NULL,
    aceite_final_contrato BOOLEAN NOT NULL,

    -- Controle
    data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_data_evento (data_evento, horario_inicio, horario_termino)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
