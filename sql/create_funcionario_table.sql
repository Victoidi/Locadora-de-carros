USE LOCADORA_CARROS;

CREATE TABLE IF NOT EXISTS funcionario (
    id_funcionario INT NOT NULL AUTO_INCREMENT,
    nm_primeiro VARCHAR(100) NOT NULL,
    nm_ultimo VARCHAR(100) NOT NULL,
    ds_login VARCHAR(100) NOT NULL,
    ds_email VARCHAR(150) NOT NULL,
    ds_senha_hash VARCHAR(255) NOT NULL,
    nr_telefone VARCHAR(20),
    nr_cpf VARCHAR(14),
    ds_cargo VARCHAR(100),
    dt_admissao DATE,
    st_ativo BOOLEAN DEFAULT TRUE,
    dt_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_funcionario),
    UNIQUE (ds_login),
    UNIQUE (ds_email),
    UNIQUE (nr_cpf)
);
