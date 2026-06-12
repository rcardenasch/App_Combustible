-- cambiar zona horaria para las fechas
SHOW timezone;

-- Para la sesión actual
SET TIMEZONE='America/Lima';

-- Para la base de datos completa (recomendado)
ALTER DATABASE App_BD SET timezone TO 'America/Lima';


	alter table clientes add column direccion varchar(200);
	commit;


