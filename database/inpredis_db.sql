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