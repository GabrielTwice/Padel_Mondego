CREATE TABLE usuario (
	id_usuario BIGINT,
	pass	 VARCHAR(512) NOT NULL,
	nome	 CHAR(255) NOT NULL,
	email	 VARCHAR(512) NOT NULL,
	nif	 INTEGER NOT NULL,
	PRIMARY KEY(id_usuario)
);

CREATE TABLE cliente (
	telefone		 INTEGER NOT NULL,
	usuario_id_usuario BIGINT,
	PRIMARY KEY(usuario_id_usuario)
);

CREATE TABLE admin (
	morada		 VARCHAR(512),
	super_admin	 BOOL,
	usuario_id_usuario BIGINT,
	PRIMARY KEY(usuario_id_usuario)
);

CREATE TABLE reservar (
	id_reserva		 BIGINT,
	disponivel		 BOOL NOT NULL DEFAULT TRUE,
	receber_notific		 BOOL NOT NULL DEFAULT True,
	data			 DATE,
	reserva_alterada		 BOOL NOT NULL,
	horario_id		 SMALLINT NOT NULL,
	cliente_usuario_id_usuario BIGINT NOT NULL,
	PRIMARY KEY(id_reserva)
);

CREATE TABLE campos (
	id_campo BIGINT,
	PRIMARY KEY(id_campo)
);

CREATE TABLE mensagem_ (
	id_mensagem	 BIGINT,
	texto		 TEXT,
	mensagem_all	 BOOL,
	mensagem_particular BOOL,
	PRIMARY KEY(id_mensagem)
);

CREATE TABLE horario (
	hora	 DATE NOT NULL,
	preco INTEGER,
	id	 SMALLINT,
	fimds BOOL,
	PRIMARY KEY(id)
);

CREATE TABLE visualizacao (
	vista			 BOOL,
	horas_mensagem		 TIMESTAMP NOT NULL,
	mensagem__id_mensagem	 BIGINT,
	cliente_usuario_id_usuario BIGINT NOT NULL,
	PRIMARY KEY(vista,mensagem__id_mensagem)
);

CREATE TABLE listadeespera (
	hora_notificada		 BOOL NOT NULL,
	hora			 TIMESTAMP,
	cliente_usuario_id_usuario BIGINT NOT NULL
);

CREATE TABLE reservar_listadeespera (
	reservar_id_reserva BIGINT,
	PRIMARY KEY(reservar_id_reserva)
);

CREATE TABLE admin_horario (
	admin_usuario_id_usuario BIGINT,
	horario_id		 SMALLINT,
	PRIMARY KEY(admin_usuario_id_usuario,horario_id)
);

CREATE TABLE admin_mensagem_ (
	admin_usuario_id_usuario BIGINT NOT NULL,
	mensagem__id_mensagem	 BIGINT,
	PRIMARY KEY(mensagem__id_mensagem)
);

CREATE TABLE reservar_campos (
	reservar_id_reserva BIGINT,
	campos_id_campo	 BIGINT NOT NULL,
	PRIMARY KEY(reservar_id_reserva)
);

ALTER TABLE usuario ADD UNIQUE (nif);
ALTER TABLE usuario ADD CONSTRAINT NIF_digits CHECK ((LEN(NIF)= 9)
);
ALTER TABLE cliente ADD UNIQUE (telefone);
ALTER TABLE cliente ADD CONSTRAINT cliente_fk1 FOREIGN KEY (usuario_id_usuario) REFERENCES usuario(id_usuario);
ALTER TABLE admin ADD CONSTRAINT admin_fk1 FOREIGN KEY (usuario_id_usuario) REFERENCES usuario(id_usuario);
ALTER TABLE reservar ADD CONSTRAINT reservar_fk1 FOREIGN KEY (horario_id) REFERENCES horario(id);
ALTER TABLE reservar ADD CONSTRAINT reservar_fk2 FOREIGN KEY (cliente_usuario_id_usuario) REFERENCES cliente(usuario_id_usuario);
ALTER TABLE horario ADD CONSTRAINT constraint_0 CHECK ((Preco >= 0));
ALTER TABLE visualizacao ADD CONSTRAINT visualizacao_fk1 FOREIGN KEY (mensagem__id_mensagem) REFERENCES mensagem_(id_mensagem);
ALTER TABLE visualizacao ADD CONSTRAINT visualizacao_fk2 FOREIGN KEY (cliente_usuario_id_usuario) REFERENCES cliente(usuario_id_usuario);
ALTER TABLE listadeespera ADD CONSTRAINT listadeespera_fk1 FOREIGN KEY (cliente_usuario_id_usuario) REFERENCES cliente(usuario_id_usuario);
ALTER TABLE reservar_listadeespera ADD CONSTRAINT reservar_listadeespera_fk1 FOREIGN KEY (reservar_id_reserva) REFERENCES reservar(id_reserva);
ALTER TABLE admin_horario ADD CONSTRAINT admin_horario_fk1 FOREIGN KEY (admin_usuario_id_usuario) REFERENCES admin(usuario_id_usuario);
ALTER TABLE admin_horario ADD CONSTRAINT admin_horario_fk2 FOREIGN KEY (horario_id) REFERENCES horario(id);
ALTER TABLE admin_mensagem_ ADD CONSTRAINT admin_mensagem__fk1 FOREIGN KEY (admin_usuario_id_usuario) REFERENCES admin(usuario_id_usuario);
ALTER TABLE admin_mensagem_ ADD CONSTRAINT admin_mensagem__fk2 FOREIGN KEY (mensagem__id_mensagem) REFERENCES mensagem_(id_mensagem);
ALTER TABLE reservar_campos ADD CONSTRAINT reservar_campos_fk1 FOREIGN KEY (reservar_id_reserva) REFERENCES reservar(id_reserva);
ALTER TABLE reservar_campos ADD CONSTRAINT reservar_campos_fk2 FOREIGN KEY (campos_id_campo) REFERENCES campos(id_campo);
