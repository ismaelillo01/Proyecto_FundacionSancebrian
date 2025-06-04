# Proyecto_FundacionSancebrian
Proyecto para unificar y centralizar los datos de distintos sensores



git clone https://github.com/ismaelillo01/Proyecto_FundacionSancebrian.git


CREATE TABLE trabajadores (
  id_trabajador INT NOT NULL,
  nombre_usuario VARCHAR(100) NOT NULL,
  contraseña VARCHAR(100) NOT NULL,
  nombre VARCHAR(100) NOT NULL,
  apellido1 VARCHAR(100) NOT NULL,
  apellido2 VARCHAR(100),
  CONSTRAINT pk1_trabajadores PRIMARY KEY (id_trabajador),
  CONSTRAINT uq1_trabajadores_nombre_usuario UNIQUE (nombre_usuario)
);

CREATE TABLE gestores (
  id_gestor INT NOT NULL,
  CONSTRAINT pk1_gestores PRIMARY KEY (id_gestor),
  CONSTRAINT fk1_gestores_trabajadores FOREIGN KEY (id_gestor) REFERENCES trabajadores(id_trabajador)
    ON DELETE CASCADE
);

CREATE TABLE cuidadores (
  id_cuidador INT NOT NULL,
  telefono VARCHAR(20) NOT NULL,
  CONSTRAINT pk1_cuidadores PRIMARY KEY (id_cuidador),
  CONSTRAINT fk1_cuidadores_trabajadores FOREIGN KEY (id_cuidador) REFERENCES trabajadores(id_trabajador)
    ON DELETE CASCADE
);

CREATE TABLE hogares (
  id_hogar INT NOT NULL,
  url VARCHAR(255) NOT NULL,
  token VARCHAR(255) NOT NULL,
  codigo_postal CHAR(5) NOT NULL,
  direccion VARCHAR(255) NOT NULL,
  CONSTRAINT pk1_hogares PRIMARY KEY (id_hogar)
);

CREATE TABLE clientes (
  id_cliente INT NOT NULL,
  id_hogar INT NOT NULL,
  id_gestor INT NOT NULL,
  CONSTRAINT pk1_clientes PRIMARY KEY (id_cliente),
  CONSTRAINT fk1_clientes_hogares FOREIGN KEY (id_hogar) REFERENCES hogares(id_hogar),
  CONSTRAINT fk2_clientes_gestores FOREIGN KEY (id_gestor) REFERENCES gestores(id_gestor)
);

CREATE TABLE datos_clientes (
  id_cliente INT NOT NULL,
  nombre VARCHAR(100) NOT NULL,
  apellido1 VARCHAR(100) NOT NULL,
  apellido2 VARCHAR(100),
  dni VARCHAR(9) UNIQUE,
  sexo VARCHAR(20),
  telefono_contacto VARCHAR(20),
  telefono_familiar VARCHAR(20),
  fecha_registro TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT pk1_datos_clientes PRIMARY KEY (id_cliente),
  CONSTRAINT fk1_datos_clientes_clientes FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
    ON DELETE CASCADE
);

CREATE TABLE horarios (
  id_horario INT NOT NULL,
  id_cuidador INT NOT NULL,
  id_cliente INT NOT NULL,
  fecha_inicio DATE,
  fecha_fin DATE,
  dia_inicio VARCHAR(20),
  dia_fin VARCHAR(20),
  hora_inicio TIME,
  hora_fin TIME,
  CONSTRAINT pk1_horarios PRIMARY KEY (id_horario),
  CONSTRAINT fk1_horarios_cuidadores FOREIGN KEY (id_cuidador) REFERENCES cuidadores(id_cuidador),
  CONSTRAINT fk2_horarios_cliente FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
);

