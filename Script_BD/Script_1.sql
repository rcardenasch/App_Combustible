select * from tanques;

SELECT *
FROM kardex where activo=true and proyecto_id=1  order by fecha desc;

select * from usuarios order by 1 desc;



SELECT *
FROM vehiculos;

SELECT *
FROM proyectos;

SELECT
    id,
    username,
    proyecto_id
FROM usuarios;


    activo = db.Column(db.Boolean, default=True)
    anulado_por = db.Column(db.Integer)
    fecha_anulacion = db.Column(db.DateTime)
    motivo_anulacion = db.Column(db.String(500))

ALTER TABLE kardex
ADD COLUMN activo BOOLEAN DEFAULT TRUE;
ALTER TABLE kardex
ADD COLUMN anulado_por INT;
ALTER TABLE kardex
ADD CONSTRAINT fk_kardex_anulado_por
FOREIGN KEY (anulado_por)
REFERENCES usuarios(id);

ALTER TABLE kardex
ADD COLUMN fecha_anulacion Date;
ALTER TABLE kardex
ADD COLUMN motivo_anulacion VARCHAR(500);

-- cambios para costo de combustible
ALTER TABLE kardex
ADD COLUMN precio_unitario NUMERIC(12,2);

ALTER TABLE kardex
ADD COLUMN costo_total NUMERIC(12,2);
ALTER TABLE kardex
ADD COLUMN proveedor VARCHAR(150);
ALTER TABLE kardex
ADD COLUMN factura VARCHAR(50);

ALTER TABLE tanques
ADD COLUMN precio_promedio NUMERIC(12,2);

-- proyecto_id en kardex
ALTER TABLE kardex
ADD COLUMN proyecto_id INTEGER;

ALTER TABLE KARDEX
ADD CONSTRAINT FK_KARDEX_PROYECTO
FOREIGN KEY (PROYECTO_ID)
REFERENCES PROYECTOS(ID);

SELECT * FROM TANQUES;
SELECT * FROM proyectos;

SELECT * FROM kardex;

-- 





