-- Active: 1772565691688@@127.0.0.1@3306@inpredis_db
-- =============================================================
-- INPREDIS — Estructura de base de datos
-- Sistema de Preventa y Distribución — Sabritas Tijuana
-- Incluye los cambios aplicados durante el desarrollo
-- =============================================================
CREATE DATABASE inpredis_db;
USE inpredis_db;

-- -------------------------------------------------------------
-- CATÁLOGOS DE USUARIOS Y EMPLEADOS
-- -------------------------------------------------------------

CREATE TABLE EDO_USUARIO(
    codigo VARCHAR(10) PRIMARY KEY,
    nombre VARCHAR(20) UNIQUE NOT NULL,
    descripcion VARCHAR(100)
);

CREATE TABLE EDO_EMPLEADO(
    codigo VARCHAR(10) PRIMARY KEY,
    nombre VARCHAR(20) UNIQUE NOT NULL,
    descripcion VARCHAR(100)
);

CREATE TABLE ROL(
    codigo VARCHAR(10) PRIMARY KEY,
    nombre VARCHAR(20) UNIQUE NOT NULL,
    descripcion VARCHAR(100)
);

CREATE TABLE TIPO_LICENCIA(
    codigo VARCHAR(10) PRIMARY KEY,
    nombre VARCHAR(20) UNIQUE NOT NULL,
    descripcion VARCHAR(150)
);

CREATE TABLE LICENCIA(
    codigo VARCHAR(10) PRIMARY KEY,
    numlicencia VARCHAR(20) UNIQUE NOT NULL,
    vigencia DATE NOT NULL,
    tipo_licencia VARCHAR(10) NOT NULL,
    FOREIGN KEY (tipo_licencia) REFERENCES TIPO_LICENCIA(codigo)
);

CREATE TABLE EMPLEADO(
    num INT PRIMARY KEY AUTO_INCREMENT,
    empNombre VARCHAR(25) NOT NULL,
    empApellPat VARCHAR(25) NOT NULL,
    empApellMa VARCHAR(25),
    fecha_nacimiento DATE NOT NULL,
    telefono VARCHAR(15) NOT NULL,
    email VARCHAR(50) UNIQUE NOT NULL,
    edo_empleado VARCHAR(10) NOT NULL,
    rol VARCHAR(10) NOT NULL,
    licencia VARCHAR(10),
    FOREIGN KEY (rol) REFERENCES ROL(codigo),
    FOREIGN KEY (edo_empleado) REFERENCES EDO_EMPLEADO(codigo),
    FOREIGN KEY (licencia) REFERENCES LICENCIA(codigo)
);

CREATE TABLE USUARIO(
    num INT PRIMARY KEY AUTO_INCREMENT,
    usuario VARCHAR(20) UNIQUE NOT NULL,
    contraseña VARCHAR(255) NOT NULL,
    edo_usuario VARCHAR(10) NOT NULL,
    empleado INT NOT NULL,
    FOREIGN KEY (edo_usuario) REFERENCES EDO_USUARIO(codigo),
    FOREIGN KEY (empleado) REFERENCES EMPLEADO(num)
);

-- -------------------------------------------------------------
-- VEHÍCULOS Y ENTREGAS
-- -------------------------------------------------------------

CREATE TABLE EDO_VEHICULO(
    codigo VARCHAR(10) PRIMARY KEY,
    nombre VARCHAR(20) UNIQUE NOT NULL,
    descripcion VARCHAR(100)
);

CREATE TABLE MARCA(
    codigo VARCHAR(10) PRIMARY KEY,
    nombre VARCHAR(20) UNIQUE NOT NULL
);

CREATE TABLE TIPO_VEHICULO(
    codigo VARCHAR(10) PRIMARY KEY,
    nombre VARCHAR(20) UNIQUE NOT NULL,
    descripcion VARCHAR(150)
);

CREATE TABLE MODELO(
    numero INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(20) UNIQUE NOT NULL,
    ano INT NOT NULL,
    capacidad DECIMAL(10,2) NOT NULL,
    marca VARCHAR(10) NOT NULL,
    FOREIGN KEY (marca) REFERENCES MARCA(codigo)
);

CREATE TABLE EDO_ENTREGA(
    codigo VARCHAR(10) PRIMARY KEY,
    nombre VARCHAR(20) UNIQUE NOT NULL,
    descripcion VARCHAR(100)
);

CREATE TABLE ENTREGA(
    numero INT PRIMARY KEY AUTO_INCREMENT,
    fecha_creacion DATE NOT NULL,
    fecha_entrega DATETIME NULL,
    empleado INT NOT NULL,
    edo_entrega VARCHAR(10) NOT NULL,
    FOREIGN KEY (empleado) REFERENCES EMPLEADO(num),
    FOREIGN KEY (edo_entrega) REFERENCES EDO_ENTREGA(codigo)
);

CREATE TABLE VEHICULO(
    numero INT PRIMARY KEY AUTO_INCREMENT,
    serie_vin VARCHAR(20) UNIQUE NOT NULL,
    placas VARCHAR(10) UNIQUE NOT NULL,
    tipo_vehiculo VARCHAR(10) NOT NULL,
    modelo INT NOT NULL,
    edo_vehiculo VARCHAR(10) NOT NULL,
    empleado INT NOT NULL,
    entrega INT NULL,
    FOREIGN KEY (tipo_vehiculo) REFERENCES TIPO_VEHICULO(codigo),
    FOREIGN KEY (modelo) REFERENCES MODELO(numero),
    FOREIGN KEY (edo_vehiculo) REFERENCES EDO_VEHICULO(codigo),
    FOREIGN KEY (empleado) REFERENCES EMPLEADO(num),
    FOREIGN KEY (entrega) REFERENCES ENTREGA(numero)
);

CREATE TABLE EMP_VEHICULO(
    empleado INT NOT NULL,
    vehiculo INT NOT NULL,
    fecha_cargo DATE NOT NULL,
    PRIMARY KEY (empleado, vehiculo, fecha_cargo),
    FOREIGN KEY (empleado) REFERENCES EMPLEADO(num),
    FOREIGN KEY (vehiculo) REFERENCES VEHICULO(numero)
);

-- -------------------------------------------------------------
-- ZONAS Y ESTABLECIMIENTOS
-- -------------------------------------------------------------

-- Los límites de latitud y longitud permiten asignar automáticamente
-- la zona de un establecimiento a partir de su ubicación (RF03)
CREATE TABLE ZONA(
    num INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(20) UNIQUE NOT NULL,
    descripcion VARCHAR(100),
    empleado INT NOT NULL,
    poligono TEXT NULL,
    lat_min DECIMAL(10,6),
    lat_max DECIMAL(10,6),
    lon_min DECIMAL(10,6),
    lon_max DECIMAL(10,6),
    FOREIGN KEY (empleado) REFERENCES EMPLEADO(num)
);

CREATE TABLE EDO_ESTABLECIMIENTO(
    codigo VARCHAR(10) PRIMARY KEY,
    nombre VARCHAR(20) UNIQUE NOT NULL,
    descripcion VARCHAR(100)
);

CREATE TABLE EDO_REP_ESTABLECIMIENTO(
    codigo VARCHAR(10) PRIMARY KEY,
    nombre VARCHAR(20) UNIQUE NOT NULL,
    descripcion VARCHAR(100)
);

CREATE TABLE REP_ESTABLECIMIENTO(
    numero INT PRIMARY KEY AUTO_INCREMENT,
    rfc VARCHAR(13) UNIQUE NOT NULL,
    repNombre VARCHAR(20) NOT NULL,
    repApellPat VARCHAR(20) NOT NULL,
    repApellMa VARCHAR(20),
    telefono VARCHAR(15) NOT NULL,
    email VARCHAR(60) UNIQUE NOT NULL,
    fecha_registro DATE NOT NULL,
    empleado INT NOT NULL,
    edo_rep_establecimiento VARCHAR(10) NOT NULL,
    FOREIGN KEY (empleado) REFERENCES EMPLEADO(num),
    FOREIGN KEY (edo_rep_establecimiento) REFERENCES EDO_REP_ESTABLECIMIENTO(codigo)
);

CREATE TABLE ESTABLECIMIENTO(
    numero INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(20) UNIQUE NOT NULL,
    estCalle VARCHAR(40) NOT NULL,
    estNumero VARCHAR(10) NOT NULL,
    estColonia VARCHAR(40) NOT NULL,
    telefono VARCHAR(15) NOT NULL,
    latitud DECIMAL(10,6) NOT NULL,
    longitud DECIMAL(10,6) NOT NULL,
    fecha_registro DATE NOT NULL,
    zona INT NOT NULL,
    empleado INT NOT NULL,
    entrega INT NULL,
    rep_establecimiento INT NOT NULL,
    edo_establecimiento VARCHAR(10) NOT NULL,
    FOREIGN KEY (zona) REFERENCES ZONA(num),
    FOREIGN KEY (empleado) REFERENCES EMPLEADO(num),
    FOREIGN KEY (entrega) REFERENCES ENTREGA(numero),
    FOREIGN KEY (rep_establecimiento) REFERENCES REP_ESTABLECIMIENTO(numero),
    FOREIGN KEY (edo_establecimiento) REFERENCES EDO_ESTABLECIMIENTO(codigo)
);

-- -------------------------------------------------------------
-- RUTAS DE VISITA
-- -------------------------------------------------------------

CREATE TABLE EDO_RUTA_VISITA(
    codigo VARCHAR(10) PRIMARY KEY,
    nombre VARCHAR(20) UNIQUE NOT NULL,
    descripcion VARCHAR(100)
);

-- 'dia' fija el día de la semana en que se recorre la ruta.
-- 'empleado' es NULL mientras el coordinador no asigne vendedor (RF31)
CREATE TABLE RUTA_VISITA(
    numero INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(20) NOT NULL,
    descripcion VARCHAR(150),
    dia VARCHAR(10) NOT NULL DEFAULT 'Lunes',
    zona INT NOT NULL,
    empleado INT NULL,
    edo_ruta_visita VARCHAR(10) NOT NULL,
    FOREIGN KEY (zona) REFERENCES ZONA(num),
    FOREIGN KEY (empleado) REFERENCES EMPLEADO(num),
    FOREIGN KEY (edo_ruta_visita) REFERENCES EDO_RUTA_VISITA(codigo)
);

-- Orden en que el vendedor debe recorrer los establecimientos
CREATE TABLE RUTA_VISITA_ORDEN(
    ruta_visita INT NOT NULL,
    establecimiento INT NOT NULL,
    orden INT NOT NULL,
    PRIMARY KEY (ruta_visita, establecimiento),
    FOREIGN KEY (ruta_visita) REFERENCES RUTA_VISITA(numero),
    FOREIGN KEY (establecimiento) REFERENCES ESTABLECIMIENTO(numero)
);

CREATE TABLE EDO_VISITA(
    codigo VARCHAR(10) PRIMARY KEY,
    nombre VARCHAR(25) UNIQUE NOT NULL,
    descripcion VARCHAR(150)
);

CREATE TABLE VISITA(
    numero INT PRIMARY KEY AUTO_INCREMENT,
    observaciones VARCHAR(200),
    fecha DATETIME NOT NULL,
    ruta_visita INT NOT NULL,
    establecimiento INT NOT NULL,
    empleado INT NOT NULL,
    edo_visita VARCHAR(10),
    FOREIGN KEY (ruta_visita) REFERENCES RUTA_VISITA(numero),
    FOREIGN KEY (establecimiento) REFERENCES ESTABLECIMIENTO(numero),
    FOREIGN KEY (edo_visita) REFERENCES EDO_VISITA(codigo),
    FOREIGN KEY (empleado) REFERENCES EMPLEADO(num)
);

-- -------------------------------------------------------------
-- PRODUCTOS Y PEDIDOS
-- -------------------------------------------------------------

CREATE TABLE EDO_PEDIDO(
    codigo VARCHAR(10) PRIMARY KEY,
    nombre VARCHAR(20) UNIQUE NOT NULL,
    descripcion VARCHAR(100)
);

CREATE TABLE PRODUCTO(
    codigo VARCHAR(10) PRIMARY KEY,
    nombre VARCHAR(60) NOT NULL,
    descripcion VARCHAR(100),
    imagen VARCHAR(255),
    precio DECIMAL(10,2),
    fecha_caducidad DATE NOT NULL,
    stock INT NOT NULL,
    peso DECIMAL(5,2)
);

CREATE TABLE PEDIDO(
    num INT PRIMARY KEY AUTO_INCREMENT,
    observaciones VARCHAR(200),
    iva DECIMAL(10,2) NOT NULL DEFAULT 0,
    total DECIMAL(10,2) NOT NULL DEFAULT 0,
    fecha DATETIME NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    visita INT NOT NULL,
    entrega INT NULL,
    edo_pedido VARCHAR(10) NOT NULL,
    FOREIGN KEY (visita) REFERENCES VISITA(numero),
    FOREIGN KEY (entrega) REFERENCES ENTREGA(numero),
    FOREIGN KEY (edo_pedido) REFERENCES EDO_PEDIDO(codigo)
);

CREATE TABLE DETALLE_PEDIDO(
    num_pedido INT NOT NULL,
    cod_producto VARCHAR(10) NOT NULL,
    cantidad INT NOT NULL,
    precioUnitario DECIMAL(10,2) NOT NULL,
    importe DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (num_pedido, cod_producto),
    FOREIGN KEY (num_pedido) REFERENCES PEDIDO(num),
    FOREIGN KEY (cod_producto) REFERENCES PRODUCTO(codigo)
);

-- Histórico de los productos que el almacenista canceló por falta de
-- stock, con la fecha estimada en que volverán a estar disponibles (RF20-21)
CREATE TABLE PRODUCTO_CANCELADO_PEDIDO(
    num_pedido INT NOT NULL,
    cod_producto VARCHAR(10) NOT NULL,
    cantidad_solicitada INT NOT NULL,
    fecha_cancelacion DATETIME NOT NULL,
    fecha_disponible_estimada DATE,
    motivo VARCHAR(200),
    PRIMARY KEY (num_pedido, cod_producto, fecha_cancelacion),
    FOREIGN KEY (num_pedido) REFERENCES PEDIDO(num),
    FOREIGN KEY (cod_producto) REFERENCES PRODUCTO(codigo)
);

-- -------------------------------------------------------------
-- RUTAS DE ENTREGA
-- -------------------------------------------------------------

CREATE TABLE EDO_RUTA_ENTREGA(
    codigo VARCHAR(10) PRIMARY KEY,
    nombre VARCHAR(20) UNIQUE NOT NULL,
    descripcion VARCHAR(100)
);

-- 'empleado' es NULL mientras el coordinador no asigne repartidor, o
-- cuando la ruta se deja disponible para que cualquiera la tome (RF33)
CREATE TABLE RUTA_ENTREGA(
    numero INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(40) NOT NULL,
    descripcion VARCHAR(150),
    empleado INT NULL,
    entrega INT NULL,
    edo_ruta_entrega VARCHAR(10) NOT NULL,
    FOREIGN KEY (empleado) REFERENCES EMPLEADO(num),
    FOREIGN KEY (entrega) REFERENCES ENTREGA(numero),
    FOREIGN KEY (edo_ruta_entrega) REFERENCES EDO_RUTA_ENTREGA(codigo)
);

-- Orden de las paradas: lo propone OSRM al crear la entrega y el
-- coordinador puede reordenarlo antes de liberar la ruta
CREATE TABLE RUTA_ENTREGA_ORDEN(
    ruta_entrega INT NOT NULL,
    establecimiento INT NOT NULL,
    orden INT NOT NULL,
    PRIMARY KEY (ruta_entrega, establecimiento),
    FOREIGN KEY (ruta_entrega) REFERENCES RUTA_ENTREGA(numero),
    FOREIGN KEY (establecimiento) REFERENCES ESTABLECIMIENTO(numero)
);

CREATE TABLE ENTREGA_ESTABLE(
    entrega INT NOT NULL,
    establecimiento INT NOT NULL,
    fecha_entrega DATE NOT NULL,
    hora_entrega TIME NOT NULL,
    PRIMARY KEY (entrega, establecimiento),
    FOREIGN KEY (entrega) REFERENCES ENTREGA(numero),
    FOREIGN KEY (establecimiento) REFERENCES ESTABLECIMIENTO(numero)
);

-- -------------------------------------------------------------
-- COBROS Y DEVOLUCIONES
-- -------------------------------------------------------------

CREATE TABLE TIPO_PAGO(
    codigo VARCHAR(10) PRIMARY KEY,
    nombre VARCHAR(20) UNIQUE NOT NULL,
    descripcion VARCHAR(100)
);

CREATE TABLE PAGO(
    codigo INT PRIMARY KEY AUTO_INCREMENT,
    monto DECIMAL(10,2) NOT NULL,
    fecha DATETIME NOT NULL,
    tipo_pago VARCHAR(10) NOT NULL,
    empleado INT NOT NULL,
    establecimiento INT NOT NULL,
    pedido INT NOT NULL,
    FOREIGN KEY (tipo_pago) REFERENCES TIPO_PAGO(codigo),
    FOREIGN KEY (empleado) REFERENCES EMPLEADO(num),
    FOREIGN KEY (establecimiento) REFERENCES ESTABLECIMIENTO(numero),
    FOREIGN KEY (pedido) REFERENCES PEDIDO(num)
);

-- 'cod_producto', 'pedido' e 'importe' identifican qué se devolvió y
-- cuánto representa, para poder descontarlo de la venta (RF38)
CREATE TABLE DEVOLUCION(
    codigo INT PRIMARY KEY AUTO_INCREMENT,
    fecha DATE NOT NULL,
    cantidad INT NOT NULL,
    motivo VARCHAR(40) NOT NULL,
    descripcion VARCHAR(150),
    entrega INT NOT NULL,
    cod_producto VARCHAR(10) NULL,
    pedido INT NULL,
    importe DECIMAL(10,2) NULL,
    FOREIGN KEY (entrega) REFERENCES ENTREGA(numero),
    FOREIGN KEY (cod_producto) REFERENCES PRODUCTO(codigo),
    FOREIGN KEY (pedido) REFERENCES PEDIDO(num)
);

-- -------------------------------------------------------------
-- MOVIMIENTOS DE INVENTARIO
-- -------------------------------------------------------------

CREATE TABLE TIPO_MOVIMIENTO(
    codigo VARCHAR(10) PRIMARY KEY,
    nombre VARCHAR(25) UNIQUE NOT NULL,
    descripcion VARCHAR(150)
);

CREATE TABLE MOVIMIENTOS(
    codigo INT PRIMARY KEY AUTO_INCREMENT,
    observaciones VARCHAR(150),
    fecha DATETIME NOT NULL,
    tipo_movimiento VARCHAR(10) NOT NULL,
    devolucion INT NULL,
    empleado INT NOT NULL,
    FOREIGN KEY (tipo_movimiento) REFERENCES TIPO_MOVIMIENTO(codigo),
    FOREIGN KEY (devolucion) REFERENCES DEVOLUCION(codigo),
    FOREIGN KEY (empleado) REFERENCES EMPLEADO(num)
);

CREATE TABLE DETALLE_MOVIMIENTO(
    cod_movimientos INT NOT NULL,
    cod_producto VARCHAR(10) NOT NULL,
    cantidad INT NOT NULL,
    precioUnitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (cod_movimientos, cod_producto),
    FOREIGN KEY (cod_movimientos) REFERENCES MOVIMIENTOS(codigo),
    FOREIGN KEY (cod_producto) REFERENCES PRODUCTO(codigo)
);

SHOW TABLES LIKE 'django_%';
SELECT app, name FROM django_migrations WHERE app IN ('contenttypes','auth','admin','sessions');

ALTER TABLE zona ADD COLUMN poligono TEXT NULL;

UPDATE zona SET lat_max = 32.560 WHERE nombre IN ('Noroeste 2', 'Noroeste', 'Noreste');

UPDATE zona SET lat_max = 32.560 WHERE nombre IN ('Noroeste 2', 'Noroeste', 'Noreste');

UPDATE zona SET poligono = '[[32.53902, -117.07002], [32.53435, -117.12425], [32.5259, -117.12435], [32.52033, -117.12392], [32.51446, -117.12427], [32.51171, -117.1247], [32.50961, -117.1247], [32.50869, -117.12444], [32.50841, -117.12451], [32.50816, -117.1245], [32.50802, -117.12452], [32.50802, -117.07003]]' WHERE nombre = 'Noroeste 2';

UPDATE zona SET poligono = '[[32.53903, -117.07], [32.50803, -117.07001], [32.50802, -116.99001], [32.54582, -116.99002]]' WHERE nombre = 'Noroeste';

UPDATE zona SET poligono = '[[32.54583, -116.99], [32.50803, -116.99001], [32.50802, -116.91001], [32.55262, -116.91002]]' WHERE nombre = 'Norte';

UPDATE zona SET poligono = '[[32.55262, -116.91], [32.50803, -116.91001], [32.50817, -116.82005], [32.56002, -116.82008]]' WHERE nombre = 'Noreste';

UPDATE zona SET poligono = '[[32.508, -117.06002], [32.50801, -117.12452], [32.50778, -117.12449], [32.50748, -117.12451], [32.5072, -117.12454], [32.50691, -117.12455], [32.50664, -117.12452], [32.50641, -117.12444], [32.50623, -117.12444], [32.50596, -117.12437], [32.50559, -117.12423], [32.50533, -117.12414], [32.50507, -117.12408], [32.50487, -117.12401], [32.50461, -117.12392], [32.5043, -117.12393], [32.50408, -117.12393], [32.5037, -117.12398], [32.50344, -117.12397], [32.5031, -117.12385], [32.50271, -117.12377], [32.50239, -117.12389], [32.50221, -117.12396], [32.50194, -117.12384], [32.50166, -117.12384], [32.5014, -117.12384], [32.50117, -117.12385], [32.50086, -117.12373], [32.50006, -117.12358], [32.49981, -117.12363], [32.49941, -117.1235], [32.49901, -117.12342], [32.49873, -117.12319], [32.49828, -117.12318], [32.49787, -117.12306], [32.49715, -117.12314], [32.4967, -117.12307], [32.49627, -117.1231], [32.49521, -117.12269], [32.49492, -117.12273], [32.49449, -117.12303], [32.49456, -117.1235], [32.49444, -117.12329], [32.49418, -117.1233], [32.49424, -117.1237], [32.49418, -117.12376], [32.49399, -117.12346], [32.49361, -117.12325], [32.49322, -117.12325], [32.49296, -117.12341], [32.49294, -117.12348], [32.49295, -117.12367], [32.49226, -117.12413], [32.49219, -117.12401], [32.49223, -117.12391], [32.49219, -117.12383], [32.49205, -117.12372], [32.49194, -117.12375], [32.49162, -117.12423], [32.49156, -117.12412], [32.49161, -117.12386], [32.49128, -117.12353], [32.48999, -117.12336], [32.48967, -117.12355], [32.48963, -117.12371], [32.48947, -117.12376], [32.48935, -117.12364], [32.48913, -117.1238], [32.48901, -117.12381], [32.48887, -117.12366], [32.48873, -117.12342], [32.48853, -117.12332], [32.4883, -117.1233], [32.48815, -117.12336], [32.48805, -117.12376], [32.48789, -117.12369], [32.48774, -117.12376], [32.48761, -117.12392], [32.4874, -117.1238], [32.48708, -117.12349], [32.48677, -117.12346], [32.48635, -117.12358], [32.48605, -117.12345], [32.48579, -117.12335], [32.4856, -117.12354], [32.48552, -117.124], [32.48532, -117.12404], [32.48527, -117.12386], [32.48518, -117.12372], [32.48499, -117.12362], [32.4846, -117.12358], [32.48426, -117.12332], [32.48415, -117.1233], [32.48404, -117.1234], [32.48404, -117.12352], [32.48381, -117.12352], [32.48359, -117.12287], [32.48338, -117.1228], [32.48322, -117.12287], [32.48286, -117.12295], [32.48275, -117.12241], [32.48274, -117.12213], [32.48253, -117.12192], [32.48238, -117.12185], [32.48227, -117.12187], [32.48222, -117.12207], [32.48216, -117.12201], [32.48215, -117.1218], [32.48183, -117.12173], [32.47867, -117.12081], [32.47795, -117.12099], [32.47614, -117.12013], [32.47454, -117.12004], [32.47422, -117.12047], [32.47374, -117.12021], [32.47333, -117.12029], [32.47325, -117.12047], [32.47239, -117.12022], [32.47188, -117.1203], [32.47094, -117.12018], [32.47028, -117.1198], [32.47008, -117.11989], [32.47001, -117.11988], [32.47002, -117.06002]]' WHERE nombre = 'Oeste 2';


CREATE TABLE RUTA_VISITA_SEMANA(
    numero INT PRIMARY KEY AUTO_INCREMENT,
    ruta_visita INT NOT NULL,
    fecha DATE NOT NULL,
    empleado INT NULL,
    edo_ruta_visita VARCHAR(10) NOT NULL,
    UNIQUE (ruta_visita, fecha),
    FOREIGN KEY (ruta_visita) REFERENCES RUTA_VISITA(numero),
    FOREIGN KEY (empleado) REFERENCES EMPLEADO(num),
    FOREIGN KEY (edo_ruta_visita) REFERENCES EDO_RUTA_VISITA(codigo)
);

INSERT INTO ruta_visita_semana (ruta_visita, fecha, empleado, edo_ruta_visita)
SELECT rv.numero,
       -- fecha del dia de la semana que le toca, dentro de la semana actual
       DATE_ADD(
           DATE_SUB(CURDATE(), INTERVAL WEEKDAY(CURDATE()) DAY),
           INTERVAL CASE rv.dia
               WHEN 'Lunes'     THEN 0
               WHEN 'Martes'    THEN 1
               WHEN 'Miércoles' THEN 2
               WHEN 'Jueves'    THEN 3
               WHEN 'Viernes'   THEN 4
               WHEN 'Sábado'    THEN 5
               ELSE 0 END DAY
       ),
       rv.empleado,
       rv.edo_ruta_visita
FROM ruta_visita rv
WHERE rv.edo_ruta_visita <> 'ERV001';

SELECT rvs.numero, rv.nombre, rv.dia, rvs.fecha, rvs.empleado, rvs.edo_ruta_visita
FROM ruta_visita_semana rvs
INNER JOIN ruta_visita rv ON rv.numero = rvs.ruta_visita
ORDER BY rvs.fecha;

ALTER TABLE ruta_visita DROP FOREIGN KEY ruta_visita_ibfk_2;
ALTER TABLE ruta_visita DROP FOREIGN KEY ruta_visita_ibfk_3;
ALTER TABLE ruta_visita DROP COLUMN empleado;
ALTER TABLE ruta_visita DROP COLUMN edo_ruta_visita;

-- Producto que el cliente pide a cambio del devuelto
ALTER TABLE devolucion ADD COLUMN cod_producto_cambio VARCHAR(10) NULL;
ALTER TABLE devolucion ADD FOREIGN KEY (cod_producto_cambio) REFERENCES producto(codigo);

-- Marca el pedido que nace de una devolución, para darle prioridad
ALTER TABLE pedido ADD COLUMN devolucion_origen INT NULL;
ALTER TABLE pedido ADD FOREIGN KEY (devolucion_origen) REFERENCES devolucion(codigo);

----Esta sera para poder mostrar que si se ejecutan los triggers ----
CREATE TABLE BITACORA_TRIGGER(
    numero INT PRIMARY KEY AUTO_INCREMENT,
    trigger_nombre VARCHAR(60) NOT NULL,
    detalle VARCHAR(200),
    fecha DATETIME NOT NULL
);

-- Bitacora de ejecucion de procedimientos almacenados. Permite verificar
-- que la logica de negocio en base de datos se esta usando de verdad.
CREATE TABLE BITACORA_PROCEDIMIENTO(
    numero INT PRIMARY KEY AUTO_INCREMENT,
    procedimiento VARCHAR(60) NOT NULL,
    detalle VARCHAR(200),
    resultado VARCHAR(20) NOT NULL,
    fecha DATETIME NOT NULL
);