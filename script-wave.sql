DROP DATABASE IF EXISTS wave;
CREATE DATABASE wave
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE wave;

CREATE TABLE pescador (
    id_pescador INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    telefone VARCHAR(20),
    cidade VARCHAR(100),
    tipo_pesca ENUM('Esportiva','Artesanal','Industrial','Amadora') DEFAULT 'Amadora',
    data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE local_pesca (
    id_local INT AUTO_INCREMENT PRIMARY KEY,
    nome_area VARCHAR(100) NOT NULL,
    latitude DECIMAL(10,7) NOT NULL,
    longitude DECIMAL(10,7) NOT NULL,
    situacao ENUM('Seguro','Atenção','Perigoso') NOT NULL DEFAULT 'Seguro',
    descricao VARCHAR(255)
);

CREATE TABLE clima (
    id_clima INT AUTO_INCREMENT PRIMARY KEY,
    temperatura DECIMAL(5,2),
    vento DECIMAL(5,2),
    umidade INT CHECK (umidade BETWEEN 0 AND 100),
    condicao VARCHAR(50),
    data_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
    id_local INT NOT NULL,

    CONSTRAINT fk_clima_local
        FOREIGN KEY (id_local)
        REFERENCES local_pesca(id_local)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE equipamento (
    id_equipamento INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    valor DECIMAL(10,2) NOT NULL CHECK (valor >= 0),
    imagem VARCHAR(255)
);

CREATE TABLE venda (
    id_venda INT AUTO_INCREMENT PRIMARY KEY,
    especie VARCHAR(100) NOT NULL,
    quantidade INT NOT NULL CHECK (quantidade > 0),
    preco DECIMAL(10,2) NOT NULL CHECK (preco >= 0),
    localizacao VARCHAR(100),
    data_venda DATETIME DEFAULT CURRENT_TIMESTAMP,
    id_pescador INT NOT NULL,

    CONSTRAINT fk_venda_pescador
        FOREIGN KEY (id_pescador)
        REFERENCES pescador(id_pescador)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE chatbot (
    id_chat INT AUTO_INCREMENT PRIMARY KEY,
    pergunta TEXT NOT NULL,
    resposta TEXT NOT NULL,
    data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
    id_pescador INT NOT NULL,

    CONSTRAINT fk_chatbot_pescador
        FOREIGN KEY (id_pescador)
        REFERENCES pescador(id_pescador)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE pescador_equipamento (

    id_pescador INT,
    id_equipamento INT,

    PRIMARY KEY (id_pescador, id_equipamento),

    CONSTRAINT fk_pe_pescador
        FOREIGN KEY (id_pescador)
        REFERENCES pescador(id_pescador)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_pe_equipamento
        FOREIGN KEY (id_equipamento)
        REFERENCES equipamento(id_equipamento)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE TABLE pescador_local (

    id_pescador INT,
    id_local INT,

    PRIMARY KEY (id_pescador, id_local),

    CONSTRAINT fk_pl_pescador
        FOREIGN KEY (id_pescador)
        REFERENCES pescador(id_pescador)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_pl_local
        FOREIGN KEY (id_local)
        REFERENCES local_pesca(id_local)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);

CREATE INDEX idx_pescador_nome
ON pescador(nome);

CREATE INDEX idx_venda_especie
ON venda(especie);

CREATE INDEX idx_local_nome
ON local_pesca(nome_area);

CREATE INDEX idx_clima_local
ON clima(id_local);

INSERT INTO pescador (nome,email,senha,telefone,cidade,tipo_pesca)
VALUES
('João Silva','joao@email.com','123456','47999990000','Itajaí','Artesanal'),
('Maria Souza','maria@email.com','123456','47999991111','Navegantes','Esportiva');

INSERT INTO local_pesca (nome_area,latitude,longitude,situacao,descricao)
VALUES
('Praia Brava',-26.9500000,-48.6350000,'Seguro','Mar calmo'),
('Rio Itajaí',-26.9070000,-48.6610000,'Atenção','Correnteza moderada');

INSERT INTO clima (temperatura,vento,umidade,condicao,id_local)
VALUES
(27.5,12.4,75,'Ensolarado',1),
(22.0,18.0,82,'Nublado',2);

INSERT INTO equipamento (nome,descricao,valor,imagem)
VALUES
('Vara Shimano','Vara de carbono 2,10m',550.00,'vara.jpg'),
('Molinete Marine Sports','Molinete tamanho 4000',320.00,'molinete.jpg');

INSERT INTO venda (especie,quantidade,preco,localizacao,id_pescador)
VALUES
('Tainha',30,450.00,'Itajaí',1),
('Robalo',12,720.00,'Navegantes',2);

INSERT INTO chatbot (pergunta,resposta,id_pescador)
VALUES
('O mar está bom hoje?','Sim, as condições são favoráveis para pesca.',1);

INSERT INTO pescador_equipamento
VALUES
(1,1),
(1,2),
(2,2);

INSERT INTO pescador_local
VALUES
(1,1),
(1,2),
(2,1);
