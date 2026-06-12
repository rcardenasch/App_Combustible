-- =========================================
-- ALTER EXISTENTES
-- =========================================

ALTER TABLE productos
ADD COLUMN activo BOOLEAN DEFAULT TRUE;

ALTER TABLE compras
ADD COLUMN almacen_id INTEGER;

ALTER TABLE ventas
ADD COLUMN almacen_id INTEGER;

-- =========================================
-- TABLA ALMACENES
-- =========================================

CREATE TABLE almacenes (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    ubicacion VARCHAR(200),
    activo BOOLEAN DEFAULT TRUE
);

ALTER TABLE compras
ADD CONSTRAINT fk_compras_almacen
FOREIGN KEY (almacen_id) REFERENCES almacenes(id);

ALTER TABLE ventas
ADD CONSTRAINT fk_ventas_almacen
FOREIGN KEY (almacen_id) REFERENCES almacenes(id);

-- =========================================
-- STOCK POR ALMACEN
-- =========================================

CREATE TABLE stock_almacen (
    id SERIAL PRIMARY KEY,
    producto_id INTEGER NOT NULL REFERENCES productos(id),
    almacen_id INTEGER NOT NULL REFERENCES almacenes(id),
    stock FLOAT DEFAULT 0
);

-- =========================================
-- KARDEX MOVIMIENTOS
-- =========================================

CREATE TABLE kardex_movimientos (
    id SERIAL PRIMARY KEY,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    producto_id INTEGER NOT NULL REFERENCES productos(id),
    almacen_id INTEGER NOT NULL REFERENCES almacenes(id),

    tipo_movimiento VARCHAR(30) NOT NULL,
    cantidad FLOAT NOT NULL,

    stock_anterior FLOAT NOT NULL,
    stock_nuevo FLOAT NOT NULL,

    costo_unitario FLOAT DEFAULT 0,

    usuario_id INTEGER REFERENCES users(id),

    observacion TEXT,

    compra_id INTEGER NULL REFERENCES compras(id),
    venta_id INTEGER NULL REFERENCES ventas(id)
);

-- =========================================
-- TRANSFERENCIAS
-- =========================================

CREATE TABLE transferencias_almacen (
    id SERIAL PRIMARY KEY,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    almacen_origen_id INTEGER NOT NULL REFERENCES almacenes(id),
    almacen_destino_id INTEGER NOT NULL REFERENCES almacenes(id),

    usuario_id INTEGER REFERENCES users(id),
    observacion TEXT
);

-- =========================================
-- DETALLE TRANSFERENCIA
-- =========================================

CREATE TABLE transferencia_detalles (
    id SERIAL PRIMARY KEY,
    transferencia_id INTEGER NOT NULL REFERENCES transferencias_almacen(id),
    producto_id INTEGER NOT NULL REFERENCES productos(id),
    cantidad FLOAT NOT NULL,
    costo_unitario FLOAT NOT NULL
);


INSERT INTO almacenes(nombre, ubicacion, activo)
VALUES ('Principal', 'Central', TRUE);


-- modificar compras para kardex

ALTER TABLE compras
ADD COLUMN usuario_id INTEGER;

ALTER TABLE compras
ADD CONSTRAINT fk_compra_usuario
FOREIGN KEY (usuario_id) REFERENCES "user"(id);


ALTER TABLE compras
ALTER COLUMN usuario_id SET NOT NULL;

UPDATE compras
SET usuario_id = 1
WHERE usuario_id IS NULL;


select * from productos;
select * from ventas;


-- cambiar zona horaria para las fechas
SHOW timezone;

-- Para la sesión actual
SET TIMEZONE='America/Lima';

-- Para la base de datos completa (recomendado)
ALTER DATABASE App_BD SET timezone TO 'America/Lima';


	alter table clientes add column direccion varchar(200);
	commit;


