-- Tabla horarios (versión completa)
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
    
    -- Claves foráneas
    FOREIGN KEY (id_cuidador) REFERENCES cuidadores(id_cuidador),
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
    FOREIGN KEY (parent_id) REFERENCES horarios(id_horario),
    
    -- Restricciones para validar los datos según el tipo
    CONSTRAINT chk_tipo_horario CHECK (tipo_horario IN ('R', 'I')),
    CONSTRAINT chk_fechas_rango CHECK (
        (tipo_horario = 'R' AND fecha IS NULL AND fecha_inicio IS NOT NULL AND fecha_fin IS NOT NULL AND fecha_inicio <= fecha_fin) OR
        (tipo_horario = 'I' AND fecha IS NOT NULL AND fecha_inicio IS NULL AND fecha_fin IS NULL)
    ),
    CONSTRAINT chk_horarios_validos CHECK (hora_inicio < hora_fin)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT="Tabla de horarios para cuidadores";

-- Índices para mejorar el rendimiento
CREATE INDEX idx_horarios_cuidador ON horarios(id_cuidador);
CREATE INDEX idx_horarios_cliente ON horarios(id_cliente);
CREATE INDEX idx_horarios_fecha ON horarios(fecha);
CREATE INDEX idx_horarios_rango ON horarios(fecha_inicio, fecha_fin);
CREATE INDEX idx_horarios_parent ON horarios(parent_id);
