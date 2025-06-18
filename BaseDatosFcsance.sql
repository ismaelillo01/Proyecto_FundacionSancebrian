CREATE TABLE trabajadores (
  id_trabajador INT NOT NULL AUTO_INCREMENT,
  nombre_usuario VARCHAR(100) NOT NULL,
  contraseña VARCHAR(100) NOT NULL,
  nombre VARCHAR(100) NOT NULL,
  apellido1 VARCHAR(100) NOT NULL,
  apellido2 VARCHAR(100),
  activo ENUM('activo', 'inactivo') DEFAULT 'activo',
  CONSTRAINT pk1_trabajadores PRIMARY KEY (id_trabajador),
  CONSTRAINT uq1_trabajadores_nombre_usuario UNIQUE (nombre_usuario),
  CONSTRAINT chk_nombre_no_espacio CHECK (TRIM(nombre_usuario) <> ''),
  CONSTRAINT chk_contraseña CHECK (TRIM(contraseña) <> '')
);

CREATE TABLE gestores (
  id_gestor INT NOT NULL,
  color VARCHAR(7) NOT NULL UNIQUE,
  CONSTRAINT pk1_gestores PRIMARY KEY (id_gestor),
  CONSTRAINT fk1_gestores_trabajadores FOREIGN KEY (id_gestor) REFERENCES trabajadores(id_trabajador)
    ON DELETE CASCADE
);

CREATE TABLE cuidadores (
  id_cuidador INT NOT NULL,
  telefono VARCHAR(20) NOT NULL,
  CONSTRAINT pk1_cuidadores PRIMARY KEY (id_cuidador),
  CONSTRAINT chk_telefono CHECK (telefono REGEXP '^[0-9]{9,15}$'),
  CONSTRAINT fk1_cuidadores_trabajadores FOREIGN KEY (id_cuidador) REFERENCES trabajadores(id_trabajador)
    ON DELETE CASCADE
);

CREATE TABLE hogares (
  id_hogar INT NOT NULL AUTO_INCREMENT,
  url VARCHAR(255) NOT NULL,
  token VARCHAR(255) NOT NULL,
  codigo_postal CHAR(5) ,
  provincia VARCHAR(100) ,
  direccion VARCHAR(255) NOT NULL,
  activo ENUM('activo', 'inactivo') DEFAULT 'activo',
  CONSTRAINT pk1_hogares PRIMARY KEY (id_hogar)
);


CREATE TABLE datos_clientes (
  id_cliente INT NOT NULL,
  nombre VARCHAR(100) NOT NULL,
  apellido1 VARCHAR(100) NOT NULL,
  apellido2 VARCHAR(100),
  dni VARCHAR(9) UNIQUE,
  sexo VARCHAR(20),
  descripcion VARCHAR(500),
  fecha_nacimiento DATE,
  telefono_contacto VARCHAR(20),
  telefono_familiar VARCHAR(20),
  fecha_registro TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  email VARCHAR(255),
  CONSTRAINT fk1_clientes_datos_clientes FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
  CONSTRAINT pk1_datos_clientes PRIMARY KEY (id_cliente),
  CONSTRAINT chk_email_valid CHECK (email REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
  CONSTRAINT chk_telefono_contacto CHECK (telefono_contacto REGEXP '^[0-9]{9,15}$'),
  CONSTRAINT chk_telefono_familiar CHECK (telefono_familiar REGEXP '^[0-9]{9,15}$')
);

CREATE TABLE clientes (
  id_cliente INT NOT NULL AUTO_INCREMENT,
  id_hogar INT NOT NULL,
  id_gestor INT NOT NULL,
  activo ENUM('activo', 'inactivo') DEFAULT 'activo',
  CONSTRAINT pk1_clientes PRIMARY KEY (id_cliente),
  CONSTRAINT fk2_clientes_hogares FOREIGN KEY (id_hogar) REFERENCES hogares(id_hogar),
  CONSTRAINT fk3_clientes_gestores FOREIGN KEY (id_gestor) REFERENCES gestores(id_gestor)
);



CREATE TABLE horarios (
     id_horario INT AUTO_INCREMENT PRIMARY KEY,
    id_cuidador INT NOT NULL,
    id_cliente INT NOT NULL,
    tipo_horario CHAR(1) NOT NULL COMMENT "'R' para Rango, 'I' para Individual",
    fecha DATE NULL COMMENT "Fecha para horarios individuales",
    fecha_inicio DATE NULL COMMENT "Fecha inicio para rangos",
    fecha_fin DATE NULL COMMENT "Fecha fin para rangos",
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    color VARCHAR(7) NOT NULL DEFAULT '#3498db' COMMENT "Código hexadecimal del color",
    descripcion TEXT NULL,
    parent_id INT NULL COMMENT "ID del horario padre para excepciones en rangos",
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
   CONSTRAINT fk1_horario_cuidadores FOREIGN KEY (id_cuidador) REFERENCES cuidadores(id_cuidador),
    CONSTRAINT fk2_horario_hogares FOREIGN KEY (id_cliente) REFERENCES hogares(id_hogar),
    CONSTRAINT fk3_horario_horario FOREIGN KEY (parent_id) REFERENCES horarios(id_horario),
    CONSTRAINT chk_tipo_horario CHECK (tipo_horario IN ('R', 'I')),
    CONSTRAINT chk_fechas_rango CHECK (
        (tipo_horario = 'R' AND fecha IS NULL AND fecha_inicio IS NOT NULL AND fecha_fin IS NOT NULL AND fecha_inicio <= fecha_fin) OR
        (tipo_horario = 'I' AND fecha IS NOT NULL AND fecha_inicio IS NULL AND fecha_fin IS NULL)
    ),
    CONSTRAINT chk_horarios_validos CHECK (hora_inicio < hora_fin)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT="Tabla de horarios para cuidadores";



create table formar (
    id_gestor int NOT NULL,
    id_grupo int NOT NULL ,
    CONSTRAINT pk_formar PRIMARY KEY (id_gestor, id_grupo)
);


DELIMITER $$

CREATE TRIGGER trg_validar_dni
BEFORE INSERT ON datos_clientes
FOR EACH ROW
BEGIN
  DECLARE dni_num INT;
  DECLARE dni_letra CHAR(1);
  DECLARE letras CHAR(23) DEFAULT 'TRWAGMYFPDXBNJZSQVHLCKE';
  DECLARE letra_correcta CHAR(1);

  -- Validar formato básico con expresión regular
  IF NEW.dni NOT REGEXP '^[0-9]{8}[A-Z]$' THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'DNI formato incorrecto';
  ELSE
    SET dni_num = CAST(SUBSTRING(NEW.dni, 1, 8) AS UNSIGNED);
    SET dni_letra = SUBSTRING(NEW.dni, 9, 1);
    SET letra_correcta = SUBSTRING(letras, (dni_num % 23) + 1, 1);

    IF dni_letra != letra_correcta THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'DNI letra incorrecta';
    END IF;
  END IF;
END$$

DELIMITER ;



DELIMITER $$

CREATE TRIGGER chk_no_solapamiento_horarios
BEFORE INSERT ON horarios
FOR EACH ROW
BEGIN
    -- Comprobar si el cuidador tiene un horario solapado por hora dentro de un mismo rango de fechas
    IF EXISTS (
        SELECT 1
        FROM horarios h
        WHERE h.id_cuidador = NEW.id_cuidador
        AND (
            -- Comprobamos si el nuevo horario se solapa con un horario existente solo por horas dentro de las mismas fechas
            (
                NEW.fecha_inicio = h.fecha_inicio AND NEW.fecha_fin = h.fecha_fin AND
                (
                    (NEW.hora_inicio BETWEEN h.hora_inicio AND h.hora_fin) OR
                    (NEW.hora_fin BETWEEN h.hora_inicio AND h.hora_fin) OR
                    (h.hora_inicio BETWEEN NEW.hora_inicio AND NEW.hora_fin) OR
                    (h.hora_fin BETWEEN NEW.hora_inicio AND NEW.hora_fin)
                )
            )
            OR
            -- El nuevo horario se solapa con el horario existente solo por horas, pero las fechas no son estrictamente las mismas
            (
                NEW.fecha_inicio <= h.fecha_fin AND NEW.fecha_fin >= h.fecha_inicio AND
                (
                    (NEW.hora_inicio BETWEEN h.hora_inicio AND h.hora_fin) OR
                    (NEW.hora_fin BETWEEN h.hora_inicio AND h.hora_fin) OR
                    (h.hora_inicio BETWEEN NEW.hora_inicio AND NEW.hora_fin) OR
                    (h.hora_fin BETWEEN NEW.hora_inicio AND NEW.hora_fin)
                )
            )
        )
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'No se puede insertar el horario porque se solapa con otro horario del cuidador en la misma franja horaria.';
    END IF;
END$$

DELIMITER ;




CREATE OR REPLACE VIEW Cuidadores_hogares AS
SELECT DISTINCT
    cuidadores.id_cuidador AS id_cuidador,
    trabajadores.nombre AS nombre_cuidador,
    hogares.id_hogar AS id_hogar,
    hogares.direccion AS direccion_hogar,
    hogares.codigo_postal AS codigo_postal,
    hogares.provincia AS provincia
FROM horarios
JOIN cuidadores ON horarios.id_cuidador = cuidadores.id_cuidador
JOIN trabajadores ON cuidadores.id_cuidador = trabajadores.id_trabajador
JOIN hogares ON horarios.id_cliente = hogares.id_hogar;

CREATE OR REPLACE VIEW Horarios_cuidadores AS
SELECT
    horarios.id_horario AS id_horario,
    cuidadores.id_cuidador AS id_cuidador,
    trabajadores.nombre AS nombre_cuidador,
    hogares.direccion AS direccion_hogar,
    horarios.tipo_horario AS tipo,
    horarios.fecha AS fecha_individual,
    horarios.fecha_inicio AS fecha_inicio_rango,
    horarios.fecha_fin AS fecha_fin_rango,
    horarios.hora_inicio AS hora_inicio,
    horarios.hora_fin AS hora_fin,
    horarios.descripcion AS descripcion
FROM horarios
JOIN cuidadores ON horarios.id_cuidador = cuidadores.id_cuidador
JOIN trabajadores ON cuidadores.id_cuidador = trabajadores.id_trabajador
JOIN hogares ON horarios.id_cliente = hogares.id_hogar;


CREATE OR REPLACE VIEW Horarios_detallados AS
SELECT
    horarios.id_horario AS id_horario,
    trabajadores.nombre AS cuidador,
    hogares.direccion AS direccion_hogar,
    horarios.tipo_horario AS tipo,
    IFNULL(horarios.fecha, CONCAT(horarios.fecha_inicio, ' a ', horarios.fecha_fin)) AS fechas,
    horarios.hora_inicio AS hora_inicio,
    horarios.hora_fin AS hora_fin,
    horarios.descripcion AS descripcion
FROM horarios
JOIN cuidadores ON horarios.id_cuidador = cuidadores.id_cuidador
JOIN trabajadores ON cuidadores.id_cuidador = trabajadores.id_trabajador
JOIN hogares ON horarios.id_cliente = hogares.id_hogar;

CREATE OR REPLACE VIEW Cuidadores_inactivos AS
SELECT
    cuidadores.id_cuidador AS id_cuidador,
    trabajadores.nombre AS nombre,
    trabajadores.apellido1 AS apellido1,
    trabajadores.apellido2 AS apellido2,
    trabajadores.activo AS estado
FROM cuidadores
JOIN trabajadores ON cuidadores.id_cuidador = trabajadores.id_trabajador
WHERE trabajadores.activo = 'inactivo';












insert into trabajadores (id_trabajador, nombre_usuario, contraseña, nombre, apellido1, apellido2, activo)
    VALUE
( 1, 'Super', '123', 'Gestor', '1', null, activo);

insert into gestores (id_gestor, color) value
(1,'#e1de0c');








