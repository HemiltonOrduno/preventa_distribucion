-- =============================================================
-- SCRIPT DE INSERCIÓN DE DATOS DE SIMULACIÓN
-- Fecha de generación: 2026-07-22
-- Sistema: Preventa y Distribución - Sabritas Tijuana
-- =============================================================

USE inpredis_db;

-- ==========================================
-- CATÁLOGOS BASE
-- ==========================================

INSERT INTO EDO_USUARIO (codigo, nombre, descripcion) VALUES
('EU001', 'Activo', 'La cuenta de usuario se encuentra habilitada para iniciar sesión en el sistema'),
('EU002', 'Inactivo', 'La cuenta de usuario ha sido deshabilitada y no puede iniciar sesión en el sistema');

INSERT INTO EDO_EMPLEADO (codigo, nombre, descripcion) VALUES
('EE001', 'Activo', 'El empleado se encuentra laborando actualmente en la empresa'),
('EE002', 'Inactivo', 'El empleado ya no forma parte de la operación de la empresa');

INSERT INTO ROL (codigo, nombre, descripcion) VALUES
('R001', 'Administrador', 'Tiene acceso completo al sistema, gestiona usuarios y genera reportes'),
('R002', 'Coordinador', 'Genera y asigna las rutas de visita y de entrega a vendedores y repartidores'),
('R003', 'Vendedor', 'Realiza las rutas de visita a los establecimientos y levanta los pedidos de preventa'),
('R004', 'Almacenista', 'Valida el inventario disponible, ajusta pedidos y registra la carga de los camiones'),
('R005', 'Repartidor', 'Realiza las rutas de entrega, confirma pedidos, registra devoluciones y cobra al cliente');

INSERT INTO TIPO_LICENCIA (codigo, nombre, descripcion) VALUES
('A1', 'Automovilista', 'Licencia para conducir vehículos particulares, aplica para vendedores'),
('B1', 'Tipo B', 'Licencia para conducir camiones urbanos y de carga menor a 8 toneladas, aplica para repartidores con camiones'),
('C1', 'Tipo C', 'Licencia para conducir vehículos de carga ligera, aplica para repartidores con unidades pequeñas'),
('DC1', 'Montacarguista', 'Licencia para operar cargas internas en almacén, aplica para almacenistas');

INSERT INTO EDO_VEHICULO (codigo, nombre, descripcion) VALUES
('EV001', 'Disponible', 'El vehículo se encuentra disponible para ser cargado y asignado a una ruta'),
('EV002', 'En ruta', 'El vehículo se encuentra actualmente realizando una ruta'),
('EV003', 'En mantenimiento', 'El vehículo se encuentra en mantenimiento y no puede ser asignado'),
('EV004', 'Fuera de servicio', 'El vehículo no se encuentra operativo por daño o baja definitiva');

INSERT INTO MARCA (codigo, nombre) VALUES
('M001', 'Nissan'),
('M002', 'Chevrolet'),
('M003', 'Ford'),
('M004', 'Isuzu'),
('M005', 'Freightliner');

INSERT INTO TIPO_VEHICULO (codigo, nombre, descripcion) VALUES
('TV001', 'Automóvil', 'Vehículo particular utilizado por vendedores para rutas de visita'),
('TV002', 'Camioneta de reparto', 'Vehículo de carga ligera para rutas de entrega urbanas'),
('TV003', 'Camión Torton', 'Vehículo de carga media para rutas de entrega de mayor volumen');

INSERT INTO EDO_ESTABLECIMIENTO (codigo, nombre, descripcion) VALUES
('EST001', 'Activo', 'El establecimiento se encuentra activo y puede recibir visitas y pedidos'),
('EST002', 'Inactivo', 'El establecimiento ha sido dado de baja del sistema');

INSERT INTO EDO_REP_ESTABLECIMIENTO (codigo, nombre, descripcion) VALUES
('ERE001', 'Activo', 'El cliente representante del establecimiento se encuentra activo'),
('ERE002', 'Inactivo', 'El cliente representante del establecimiento ha sido dado de baja');

INSERT INTO EDO_RUTA_VISITA (codigo, nombre, descripcion) VALUES
('ERV001', 'Activa', 'La ruta de visita se encuentra vigente y en operación'),
('ERV002', 'Inactiva', 'La ruta de visita no se encuentra en operación actualmente'),
('ERV003', 'Iniciada', 'El vendedor ya comenzó su jornada de visitas'),
('ERV004', 'Completada', 'La ruta de visita fue completada en su totalidad'),
('ERV005', 'Pausada', 'La ruta de visita fue pausada por una incidencia en campo');

INSERT INTO EDO_VISITA (codigo, nombre, descripcion) VALUES
('EVI001', 'Pendiente', 'La visita aún no ha iniciado'),
('EVI002', 'En camino', 'El vendedor se encuentra en camino hacia el establecimiento'),
('EVI003', 'En proceso', 'El vendedor se encuentra realizando la visita en el establecimiento'),
('EVI004', 'Completada', 'La visita concluyó y se registró un pedido'),
('EVI005', 'Completada sin pedido', 'La visita concluyó sin pedido porque el establecimiento estaba cerrado');

INSERT INTO EDO_PEDIDO (codigo, nombre, descripcion) VALUES
('EPD001', 'Pendiente de validación', 'El pedido fue levantado por el vendedor y espera validación del almacenista'),
('EPD002', 'En proceso', 'El almacenista se encuentra validando el inventario del pedido'),
('EPD003', 'Registrado', 'El pedido fue validado y confirmado por el almacenista'),
('EPD004', 'Surtido', 'El pedido fue cargado en el camión correspondiente'),
('EPD005', 'Entregado', 'El pedido fue entregado exitosamente al cliente'),
('EPD006', 'Cancelado', 'El pedido fue cancelado por falta de existencias u otro motivo');

INSERT INTO EDO_RUTA_ENTREGA (codigo, nombre, descripcion) VALUES
('ERET001', 'Creada', 'El coordinador generó la ruta de entrega'),
('ERET002', 'En camino', 'El repartidor ya salió a realizar las entregas'),
('ERET003', 'Entregada', 'El repartidor completó todas las entregas de la ruta'),
('ERET004', 'Pausada', 'La ruta de entrega fue pausada por una incidencia en campo');

INSERT INTO EDO_ENTREGA (codigo, nombre, descripcion) VALUES
('EEN001', 'Creada', 'El almacenista registró la entrega con los pedidos asignados'),
('EEN002', 'En proceso', 'El almacenista está cargando el camión con los pedidos'),
('EEN003', 'Cargada', 'El camión ya está listo con todos los pedidos'),
('EEN004', 'Completada', 'Todos los pedidos de la entrega fueron distribuidos exitosamente');

INSERT INTO TIPO_PAGO (codigo, nombre, descripcion) VALUES
('TP001', 'Efectivo', 'Pago realizado en efectivo al momento de la entrega'),
('TP002', 'Tarjeta', 'Pago realizado con tarjeta de débito o crédito al momento de la entrega');

INSERT INTO TIPO_MOVIMIENTO (codigo, nombre, descripcion) VALUES
('TM001', 'Entrada', 'Ingreso de producto al inventario del almacén'),
('TM002', 'Salida por pedido', 'Salida de producto del inventario debido a que un pedido fue surtido'),
('TM003', 'Salida por merma', 'Salida de producto del inventario debido a merma'),
('TM004', 'Entrada por devolución', 'Ingreso de producto al inventario generado por una devolución aceptada');


-- ==========================================
-- LICENCIAS
-- ==========================================

INSERT INTO LICENCIA (codigo, numlicencia, vigencia, tipo_licencia) VALUES
('L001', 'BC2021007', '2027-02-15', 'A1'),
('L002', 'BC2022014', '2027-03-15', 'A1'),
('L003', 'BC2023021', '2027-04-15', 'A1'),
('L004', 'BC2024028', '2027-05-15', 'A1'),
('L005', 'BC2025035', '2027-06-15', 'A1'),
('L006', 'BC2026042', '2027-07-15', 'A1'),
('L007', 'BC2027049', '2027-08-15', 'A1'),
('L008', 'BC2028056', '2027-09-15', 'A1'),
('L009', 'BC2029063', '2027-10-15', 'A1'),
('L010', 'BC2030070', '2027-11-15', 'A1'),
('L011', 'BC2031077', '2027-12-15', 'A1'),
('L012', 'BC2032084', '2027-01-15', 'A1'),
('L013', 'BC2033091', '2027-02-15', 'A1'),
('L014', 'BC2034098', '2027-03-15', 'A1'),
('L015', 'BC2035105', '2027-04-15', 'A1'),
('L016', 'BC2036112', '2027-05-15', 'A1'),
('L017', 'BC2037119', '2027-06-15', 'A1'),
('L018', 'BC2038126', '2027-07-15', 'A1'),
('L019', 'BC2039133', '2027-08-15', 'A1'),
('L020', 'BC2040140', '2027-09-15', 'A1'),
('L021', 'BC2041147', '2027-10-15', 'C1'),
('L022', 'BC2042154', '2027-11-15', 'B1'),
('L023', 'BC2043161', '2027-12-15', 'C1'),
('L024', 'BC2044168', '2027-01-15', 'B1'),
('L025', 'BC2045175', '2027-02-15', 'C1'),
('L026', 'BC2046182', '2027-03-15', 'B1'),
('L027', 'BC2047189', '2027-04-15', 'C1'),
('L028', 'BC2048196', '2027-05-15', 'B1'),
('L029', 'BC2049203', '2027-06-15', 'C1'),
('L030', 'BC2050210', '2027-07-15', 'B1'),
('L031', 'BC2051217', '2027-08-15', 'C1'),
('L032', 'BC2052224', '2027-09-15', 'B1'),
('L033', 'BC2053231', '2027-10-15', 'C1'),
('L034', 'BC2054238', '2027-11-15', 'B1'),
('L035', 'BC2055245', '2027-12-15', 'C1'),
('L036', 'BC2056252', '2027-01-15', 'B1'),
('L037', 'BC2057259', '2027-02-15', 'C1'),
('L038', 'BC2058266', '2027-03-15', 'B1'),
('L039', 'BC2059273', '2027-04-15', 'C1'),
('L040', 'BC2060280', '2027-05-15', 'B1'),
('L041', 'BC2061287', '2027-06-15', 'DC1'),
('L042', 'BC2062294', '2027-07-15', 'DC1'),
('L043', 'BC2063301', '2027-08-15', 'DC1'),
('L044', 'BC2064308', '2027-09-15', 'DC1'),
('L045', 'BC2065315', '2027-10-15', 'DC1'),
('L046', 'BC2066322', '2027-11-15', 'DC1'),
('L047', 'BC2067329', '2027-12-15', 'DC1'),
('L048', 'BC2068336', '2027-01-15', 'DC1'),
('L049', 'BC2069343', '2027-02-15', 'DC1'),
('L050', 'BC2070350', '2027-03-15', 'DC1'),
('L051', 'BC2071357', '2027-04-15', 'DC1'),
('L052', 'BC2072364', '2027-05-15', 'DC1'),
('L053', 'BC2073371', '2027-06-15', 'DC1'),
('L054', 'BC2074378', '2027-07-15', 'DC1'),
('L055', 'BC2075385', '2027-08-15', 'DC1'),
('L056', 'BC2076392', '2027-09-15', 'DC1'),
('L057', 'BC2077399', '2027-10-15', 'DC1'),
('L058', 'BC2078406', '2027-11-15', 'DC1'),
('L059', 'BC2079413', '2027-12-15', 'DC1'),
('L060', 'BC2080420', '2027-01-15', 'DC1');

-- ==========================================
-- EMPLEADOS Y USUARIOS
-- ==========================================

INSERT INTO EMPLEADO (num, empNombre, empApellPat, empApellMa, fecha_nacimiento, telefono, email, edo_empleado, rol, licencia) VALUES
(1, 'Roberto', 'Administrador', 'Sistema', '1980-01-01', '(664)0000001', 'admin@sabritas-tij.com.mx', 'EE001', 'R001', NULL),
(2, 'Juan', 'Hernández', 'Ramírez', '1985-01-15', '(664)0000002', 'juan.hernández@sabritas-tij.com.mx', 'EE001', 'R002', NULL),
(3, 'María', 'López', 'Cortés', '1985-02-15', '(664)0000003', 'maría.lópez@sabritas-tij.com.mx', 'EE001', 'R002', NULL),
(4, 'Juan', 'Hernández', 'Ramírez', '1990-01-01', '(664)0000004', 'v1.hernández@sabritas-tij.com.mx', 'EE001', 'R003', 'L001'),
(5, 'María', 'López', 'Cortés', '1991-02-02', '(664)0000005', 'v2.lópez@sabritas-tij.com.mx', 'EE001', 'R003', 'L002'),
(6, 'Carlos', 'Martínez', 'Solano', '1992-03-03', '(664)0000006', 'v3.martínez@sabritas-tij.com.mx', 'EE001', 'R003', 'L003'),
(7, 'Ana', 'García', 'Valdez', '1993-04-04', '(664)0000007', 'v4.garcía@sabritas-tij.com.mx', 'EE001', 'R003', 'L004'),
(8, 'Luis', 'Rodríguez', 'Peña', '1994-05-05', '(664)0000008', 'v5.rodríguez@sabritas-tij.com.mx', 'EE001', 'R003', 'L005'),
(9, 'Sofía', 'Torres', 'Núñez', '1995-06-06', '(664)0000009', 'v6.torres@sabritas-tij.com.mx', 'EE001', 'R003', 'L006'),
(10, 'Jorge', 'Ramírez', 'Aguilar', '1996-07-07', '(664)0000010', 'v7.ramírez@sabritas-tij.com.mx', 'EE001', 'R003', 'L007'),
(11, 'Daniela', 'Flores', 'Medina', '1997-08-08', '(664)0000011', 'v8.flores@sabritas-tij.com.mx', 'EE001', 'R003', 'L008'),
(12, 'Ricardo', 'Morales', 'Castro', '1998-09-09', '(664)0000012', 'v9.morales@sabritas-tij.com.mx', 'EE001', 'R003', 'L009'),
(13, 'Patricia', 'Jiménez', 'Rivas', '1999-10-10', '(664)0000013', 'v10.jiménez@sabritas-tij.com.mx', 'EE001', 'R003', 'L010'),
(14, 'Fernando', 'Castro', 'Ochoa', '1990-11-11', '(664)0000014', 'v11.castro@sabritas-tij.com.mx', 'EE001', 'R003', 'L011'),
(15, 'Gabriela', 'Ortiz', 'Reyes', '1991-12-12', '(664)0000015', 'v12.ortiz@sabritas-tij.com.mx', 'EE001', 'R003', 'L012'),
(16, 'Miguel', 'Vázquez', 'Domínguez', '1992-01-13', '(664)0000016', 'v13.vázquez@sabritas-tij.com.mx', 'EE001', 'R003', 'L013'),
(17, 'Alejandra', 'Mendoza', 'Guerrero', '1993-02-14', '(664)0000017', 'v14.mendoza@sabritas-tij.com.mx', 'EE001', 'R003', 'L014'),
(18, 'Roberto', 'Silva', 'Bracamontes', '1994-03-15', '(664)0000018', 'v15.silva@sabritas-tij.com.mx', 'EE001', 'R003', 'L015'),
(19, 'Cecilia', 'Guerrero', 'Zavala', '1995-04-16', '(664)0000019', 'v16.guerrero@sabritas-tij.com.mx', 'EE001', 'R003', 'L016'),
(20, 'Andrés', 'Padilla', 'Manzano', '1996-05-17', '(664)0000020', 'v17.padilla@sabritas-tij.com.mx', 'EE001', 'R003', 'L017'),
(21, 'Beatriz', 'Salgado', 'Franco', '1997-06-18', '(664)0000021', 'v18.salgado@sabritas-tij.com.mx', 'EE001', 'R003', 'L018'),
(22, 'Ernesto', 'Ríos', 'Muñoz', '1998-07-19', '(664)0000022', 'v19.ríos@sabritas-tij.com.mx', 'EE001', 'R003', 'L019'),
(23, 'Claudia', 'Vargas', 'Espinoza', '1999-08-20', '(664)0000023', 'v20.vargas@sabritas-tij.com.mx', 'EE001', 'R003', 'L020'),
(24, 'Juan', 'Hernández', 'Ramírez', '1990-01-01', '(664)0000024', 'a1.hernández@sabritas-tij.com.mx', 'EE001', 'R004', 'L041'),
(25, 'María', 'López', 'Cortés', '1991-02-02', '(664)0000025', 'a2.lópez@sabritas-tij.com.mx', 'EE001', 'R004', 'L042'),
(26, 'Carlos', 'Martínez', 'Solano', '1992-03-03', '(664)0000026', 'a3.martínez@sabritas-tij.com.mx', 'EE001', 'R004', 'L043'),
(27, 'Ana', 'García', 'Valdez', '1993-04-04', '(664)0000027', 'a4.garcía@sabritas-tij.com.mx', 'EE001', 'R004', 'L044'),
(28, 'Luis', 'Rodríguez', 'Peña', '1994-05-05', '(664)0000028', 'a5.rodríguez@sabritas-tij.com.mx', 'EE001', 'R004', 'L045'),
(29, 'Sofía', 'Torres', 'Núñez', '1995-06-06', '(664)0000029', 'a6.torres@sabritas-tij.com.mx', 'EE001', 'R004', 'L046'),
(30, 'Jorge', 'Ramírez', 'Aguilar', '1996-07-07', '(664)0000030', 'a7.ramírez@sabritas-tij.com.mx', 'EE001', 'R004', 'L047'),
(31, 'Daniela', 'Flores', 'Medina', '1997-08-08', '(664)0000031', 'a8.flores@sabritas-tij.com.mx', 'EE001', 'R004', 'L048'),
(32, 'Ricardo', 'Morales', 'Castro', '1998-09-09', '(664)0000032', 'a9.morales@sabritas-tij.com.mx', 'EE001', 'R004', 'L049'),
(33, 'Patricia', 'Jiménez', 'Rivas', '1999-10-10', '(664)0000033', 'a10.jiménez@sabritas-tij.com.mx', 'EE001', 'R004', 'L050'),
(34, 'Fernando', 'Castro', 'Ochoa', '1990-11-11', '(664)0000034', 'a11.castro@sabritas-tij.com.mx', 'EE001', 'R004', 'L051'),
(35, 'Gabriela', 'Ortiz', 'Reyes', '1991-12-12', '(664)0000035', 'a12.ortiz@sabritas-tij.com.mx', 'EE001', 'R004', 'L052'),
(36, 'Miguel', 'Vázquez', 'Domínguez', '1992-01-13', '(664)0000036', 'a13.vázquez@sabritas-tij.com.mx', 'EE001', 'R004', 'L053'),
(37, 'Alejandra', 'Mendoza', 'Guerrero', '1993-02-14', '(664)0000037', 'a14.mendoza@sabritas-tij.com.mx', 'EE001', 'R004', 'L054'),
(38, 'Roberto', 'Silva', 'Bracamontes', '1994-03-15', '(664)0000038', 'a15.silva@sabritas-tij.com.mx', 'EE001', 'R004', 'L055'),
(39, 'Cecilia', 'Guerrero', 'Zavala', '1995-04-16', '(664)0000039', 'a16.guerrero@sabritas-tij.com.mx', 'EE001', 'R004', 'L056'),
(40, 'Andrés', 'Padilla', 'Manzano', '1996-05-17', '(664)0000040', 'a17.padilla@sabritas-tij.com.mx', 'EE001', 'R004', 'L057'),
(41, 'Beatriz', 'Salgado', 'Franco', '1997-06-18', '(664)0000041', 'a18.salgado@sabritas-tij.com.mx', 'EE001', 'R004', 'L058'),
(42, 'Ernesto', 'Ríos', 'Muñoz', '1998-07-19', '(664)0000042', 'a19.ríos@sabritas-tij.com.mx', 'EE001', 'R004', 'L059'),
(43, 'Claudia', 'Vargas', 'Espinoza', '1999-08-20', '(664)0000043', 'a20.vargas@sabritas-tij.com.mx', 'EE001', 'R004', 'L060'),
(44, 'Juan', 'Hernández', 'Ramírez', '1990-01-01', '(664)0000044', 'r1.hernández@sabritas-tij.com.mx', 'EE001', 'R005', 'L021'),
(45, 'María', 'López', 'Cortés', '1991-02-02', '(664)0000045', 'r2.lópez@sabritas-tij.com.mx', 'EE001', 'R005', 'L022'),
(46, 'Carlos', 'Martínez', 'Solano', '1992-03-03', '(664)0000046', 'r3.martínez@sabritas-tij.com.mx', 'EE001', 'R005', 'L023'),
(47, 'Ana', 'García', 'Valdez', '1993-04-04', '(664)0000047', 'r4.garcía@sabritas-tij.com.mx', 'EE001', 'R005', 'L024'),
(48, 'Luis', 'Rodríguez', 'Peña', '1994-05-05', '(664)0000048', 'r5.rodríguez@sabritas-tij.com.mx', 'EE001', 'R005', 'L025'),
(49, 'Sofía', 'Torres', 'Núñez', '1995-06-06', '(664)0000049', 'r6.torres@sabritas-tij.com.mx', 'EE001', 'R005', 'L026'),
(50, 'Jorge', 'Ramírez', 'Aguilar', '1996-07-07', '(664)0000050', 'r7.ramírez@sabritas-tij.com.mx', 'EE001', 'R005', 'L027'),
(51, 'Daniela', 'Flores', 'Medina', '1997-08-08', '(664)0000051', 'r8.flores@sabritas-tij.com.mx', 'EE001', 'R005', 'L028'),
(52, 'Ricardo', 'Morales', 'Castro', '1998-09-09', '(664)0000052', 'r9.morales@sabritas-tij.com.mx', 'EE001', 'R005', 'L029'),
(53, 'Patricia', 'Jiménez', 'Rivas', '1999-10-10', '(664)0000053', 'r10.jiménez@sabritas-tij.com.mx', 'EE001', 'R005', 'L030'),
(54, 'Fernando', 'Castro', 'Ochoa', '1990-11-11', '(664)0000054', 'r11.castro@sabritas-tij.com.mx', 'EE001', 'R005', 'L031'),
(55, 'Gabriela', 'Ortiz', 'Reyes', '1991-12-12', '(664)0000055', 'r12.ortiz@sabritas-tij.com.mx', 'EE001', 'R005', 'L032'),
(56, 'Miguel', 'Vázquez', 'Domínguez', '1992-01-13', '(664)0000056', 'r13.vázquez@sabritas-tij.com.mx', 'EE001', 'R005', 'L033'),
(57, 'Alejandra', 'Mendoza', 'Guerrero', '1993-02-14', '(664)0000057', 'r14.mendoza@sabritas-tij.com.mx', 'EE001', 'R005', 'L034'),
(58, 'Roberto', 'Silva', 'Bracamontes', '1994-03-15', '(664)0000058', 'r15.silva@sabritas-tij.com.mx', 'EE001', 'R005', 'L035'),
(59, 'Cecilia', 'Guerrero', 'Zavala', '1995-04-16', '(664)0000059', 'r16.guerrero@sabritas-tij.com.mx', 'EE001', 'R005', 'L036'),
(60, 'Andrés', 'Padilla', 'Manzano', '1996-05-17', '(664)0000060', 'r17.padilla@sabritas-tij.com.mx', 'EE001', 'R005', 'L037'),
(61, 'Beatriz', 'Salgado', 'Franco', '1997-06-18', '(664)0000061', 'r18.salgado@sabritas-tij.com.mx', 'EE001', 'R005', 'L038'),
(62, 'Ernesto', 'Ríos', 'Muñoz', '1998-07-19', '(664)0000062', 'r19.ríos@sabritas-tij.com.mx', 'EE001', 'R005', 'L039'),
(63, 'Claudia', 'Vargas', 'Espinoza', '1999-08-20', '(664)0000063', 'r20.vargas@sabritas-tij.com.mx', 'EE001', 'R005', 'L040');

INSERT INTO USUARIO (num, usuario, contraseña, edo_usuario, empleado) VALUES
(1, 'admin', '$2b$12$hashAdmin', 'EU001', 1),
(2, 'jhernández', '$2b$12$hashCoord1', 'EU001', 2),
(3, 'mlópez', '$2b$12$hashCoord2', 'EU001', 3),
(4, 'vend01', '$2b$12$hashVend1', 'EU001', 4),
(5, 'vend02', '$2b$12$hashVend2', 'EU001', 5),
(6, 'vend03', '$2b$12$hashVend3', 'EU001', 6),
(7, 'vend04', '$2b$12$hashVend4', 'EU001', 7),
(8, 'vend05', '$2b$12$hashVend5', 'EU001', 8),
(9, 'vend06', '$2b$12$hashVend6', 'EU001', 9),
(10, 'vend07', '$2b$12$hashVend7', 'EU001', 10),
(11, 'vend08', '$2b$12$hashVend8', 'EU001', 11),
(12, 'vend09', '$2b$12$hashVend9', 'EU001', 12),
(13, 'vend10', '$2b$12$hashVend10', 'EU001', 13),
(14, 'vend11', '$2b$12$hashVend11', 'EU001', 14),
(15, 'vend12', '$2b$12$hashVend12', 'EU001', 15),
(16, 'vend13', '$2b$12$hashVend13', 'EU001', 16),
(17, 'vend14', '$2b$12$hashVend14', 'EU001', 17),
(18, 'vend15', '$2b$12$hashVend15', 'EU001', 18),
(19, 'vend16', '$2b$12$hashVend16', 'EU001', 19),
(20, 'vend17', '$2b$12$hashVend17', 'EU001', 20),
(21, 'vend18', '$2b$12$hashVend18', 'EU001', 21),
(22, 'vend19', '$2b$12$hashVend19', 'EU001', 22),
(23, 'vend20', '$2b$12$hashVend20', 'EU001', 23),
(24, 'alm01', '$2b$12$hashAlm1', 'EU001', 24),
(25, 'alm02', '$2b$12$hashAlm2', 'EU001', 25),
(26, 'alm03', '$2b$12$hashAlm3', 'EU001', 26),
(27, 'alm04', '$2b$12$hashAlm4', 'EU001', 27),
(28, 'alm05', '$2b$12$hashAlm5', 'EU001', 28),
(29, 'alm06', '$2b$12$hashAlm6', 'EU001', 29),
(30, 'alm07', '$2b$12$hashAlm7', 'EU001', 30),
(31, 'alm08', '$2b$12$hashAlm8', 'EU001', 31),
(32, 'alm09', '$2b$12$hashAlm9', 'EU001', 32),
(33, 'alm10', '$2b$12$hashAlm10', 'EU001', 33),
(34, 'alm11', '$2b$12$hashAlm11', 'EU001', 34),
(35, 'alm12', '$2b$12$hashAlm12', 'EU001', 35),
(36, 'alm13', '$2b$12$hashAlm13', 'EU001', 36),
(37, 'alm14', '$2b$12$hashAlm14', 'EU001', 37),
(38, 'alm15', '$2b$12$hashAlm15', 'EU001', 38),
(39, 'alm16', '$2b$12$hashAlm16', 'EU001', 39),
(40, 'alm17', '$2b$12$hashAlm17', 'EU001', 40),
(41, 'alm18', '$2b$12$hashAlm18', 'EU001', 41),
(42, 'alm19', '$2b$12$hashAlm19', 'EU001', 42),
(43, 'alm20', '$2b$12$hashAlm20', 'EU001', 43),
(44, 'rep01', '$2b$12$hashRep1', 'EU001', 44),
(45, 'rep02', '$2b$12$hashRep2', 'EU001', 45),
(46, 'rep03', '$2b$12$hashRep3', 'EU001', 46),
(47, 'rep04', '$2b$12$hashRep4', 'EU001', 47),
(48, 'rep05', '$2b$12$hashRep5', 'EU001', 48),
(49, 'rep06', '$2b$12$hashRep6', 'EU001', 49),
(50, 'rep07', '$2b$12$hashRep7', 'EU001', 50),
(51, 'rep08', '$2b$12$hashRep8', 'EU001', 51),
(52, 'rep09', '$2b$12$hashRep9', 'EU001', 52),
(53, 'rep10', '$2b$12$hashRep10', 'EU001', 53),
(54, 'rep11', '$2b$12$hashRep11', 'EU001', 54),
(55, 'rep12', '$2b$12$hashRep12', 'EU001', 55),
(56, 'rep13', '$2b$12$hashRep13', 'EU001', 56),
(57, 'rep14', '$2b$12$hashRep14', 'EU001', 57),
(58, 'rep15', '$2b$12$hashRep15', 'EU001', 58),
(59, 'rep16', '$2b$12$hashRep16', 'EU001', 59),
(60, 'rep17', '$2b$12$hashRep17', 'EU001', 60),
(61, 'rep18', '$2b$12$hashRep18', 'EU001', 61),
(62, 'rep19', '$2b$12$hashRep19', 'EU001', 62),
(63, 'rep20', '$2b$12$hashRep20', 'EU001', 63);


-- ==========================================
-- ZONAS GEOGRÁFICAS DE TIJUANA
-- ==========================================

-- Nota: Los límites de coordenadas de cada zona se configuran en el sistema
-- para la asignación automática al registrar establecimientos
INSERT INTO ZONA (num, nombre, descripcion, empleado) VALUES
(1, 'Noroeste', 'Zona que cubre el área noroeste de Tijuana incluyendo Playas y Libertad', 2),
(2, 'Norte 1', 'Zona que cubre el área norte de Tijuana lado poniente incluyendo Centro y San Ysidro', 2),
(3, 'Norte 2', 'Zona que cubre el área norte de Tijuana lado oriente incluyendo La Mesa Norte', 3),
(4, 'Poniente', 'Zona que cubre el área poniente de Tijuana incluyendo Otay Poniente', 3),
(5, 'Centro', 'Zona que cubre el área central de Tijuana incluyendo Cacho y Agua Caliente', 2),
(6, 'Oriente 1', 'Zona que cubre el área oriente de Tijuana incluyendo Otay y Mesa de Otay', 3),
(7, 'Oriente 2', 'Zona que cubre el área oriente de Tijuana incluyendo El Florido y Villa del Campo', 2),
(8, 'Sureste 1', 'Zona que cubre el área sureste de Tijuana incluyendo Cerro Colorado', 3),
(9, 'Sureste 2', 'Zona que cubre el área sureste de Tijuana incluyendo San Antonio de los Buenos', 2),
(10, 'Sur', 'Zona que cubre el área sur de Tijuana incluyendo Camino Verde y Mariano Matamoros', 3);


-- ==========================================
-- MODELOS Y VEHÍCULOS
-- ==========================================

INSERT INTO MODELO (numero, nombre, ano, capacidad, marca) VALUES
(1, 'Tsuru', 2018, 0, 'M001'),
(2, 'Versa', 2020, 0, 'M001'),
(3, 'NP300', 2021, 1200, 'M001'),
(4, 'Frontier', 2022, 1500, 'M001'),
(5, 'Silverado 3500', 2021, 3500, 'M002'),
(6, 'F-350', 2022, 3200, 'M003'),
(7, 'NPR', 2020, 4500, 'M004'),
(8, 'NQR', 2022, 6000, 'M004'),
(9, 'M2 106', 2021, 8000, 'M005'),
(10, 'Estafeta', 2023, 900, 'M002');

INSERT INTO VEHICULO (numero, serie_vin, placas, tipo_vehiculo, modelo, edo_vehiculo, empleado, entrega) VALUES
(1, '3N1AB7AP0005000', 'BC100A00', 'TV001', 1, 'EV001', 4, NULL),
(2, '3N1AB7AP0005001', 'BC101A01', 'TV001', 2, 'EV001', 5, NULL),
(3, '3N1AB7AP0005002', 'BC102A02', 'TV001', 1, 'EV001', 6, NULL),
(4, '3N1AB7AP0005003', 'BC103A03', 'TV001', 2, 'EV001', 7, NULL),
(5, '3N1AB7AP0005004', 'BC104A04', 'TV001', 1, 'EV001', 8, NULL),
(6, '3N1AB7AP0005005', 'BC105A05', 'TV001', 2, 'EV001', 9, NULL),
(7, '3N1AB7AP0005006', 'BC106A06', 'TV001', 1, 'EV001', 10, NULL),
(8, '3N1AB7AP0005007', 'BC107A07', 'TV001', 2, 'EV001', 11, NULL),
(9, '3N1AB7AP0005008', 'BC108A08', 'TV001', 1, 'EV001', 12, NULL),
(10, '3N1AB7AP0005009', 'BC109A09', 'TV001', 2, 'EV001', 13, NULL),
(11, '3N1AB7AP0005010', 'BC110A10', 'TV001', 1, 'EV001', 14, NULL),
(12, '3N1AB7AP0005011', 'BC111A11', 'TV001', 2, 'EV001', 15, NULL),
(13, '3N1AB7AP0005012', 'BC112A12', 'TV001', 1, 'EV001', 16, NULL),
(14, '3N1AB7AP0005013', 'BC113A13', 'TV001', 2, 'EV001', 17, NULL),
(15, '3N1AB7AP0005014', 'BC114A14', 'TV001', 1, 'EV001', 18, NULL),
(16, '3N1AB7AP0005015', 'BC115A15', 'TV001', 2, 'EV001', 19, NULL),
(17, '3N1AB7AP0005016', 'BC116A16', 'TV001', 1, 'EV001', 20, NULL),
(18, '3N1AB7AP0005017', 'BC117A17', 'TV001', 2, 'EV001', 21, NULL),
(19, '3N1AB7AP0005018', 'BC118A18', 'TV001', 1, 'EV001', 22, NULL),
(20, '3N1AB7AP0005019', 'BC119A19', 'TV001', 2, 'EV001', 23, NULL),
(21, '3N1AB7AP0006000', 'BC200B00', 'TV002', 3, 'EV001', 44, NULL),
(22, '3N1AB7AP0006001', 'BC201B01', 'TV002', 4, 'EV001', 45, NULL),
(23, '3N1AB7AP0006002', 'BC202B02', 'TV002', 5, 'EV001', 46, NULL),
(24, '3N1AB7AP0006003', 'BC203B03', 'TV002', 6, 'EV001', 47, NULL),
(25, '3N1AB7AP0006004', 'BC204B04', 'TV003', 7, 'EV001', 48, NULL),
(26, '3N1AB7AP0006005', 'BC205B05', 'TV003', 8, 'EV001', 49, NULL),
(27, '3N1AB7AP0006006', 'BC206B06', 'TV003', 9, 'EV001', 50, NULL),
(28, '3N1AB7AP0006007', 'BC207B07', 'TV003', 10, 'EV001', 51, NULL),
(29, '3N1AB7AP0006008', 'BC208B08', 'TV002', 3, 'EV001', 52, NULL),
(30, '3N1AB7AP0006009', 'BC209B09', 'TV002', 4, 'EV001', 53, NULL),
(31, '3N1AB7AP0006010', 'BC210B10', 'TV002', 5, 'EV001', 54, NULL),
(32, '3N1AB7AP0006011', 'BC211B11', 'TV002', 6, 'EV001', 55, NULL),
(33, '3N1AB7AP0006012', 'BC212B12', 'TV003', 7, 'EV001', 56, NULL),
(34, '3N1AB7AP0006013', 'BC213B13', 'TV003', 8, 'EV001', 57, NULL),
(35, '3N1AB7AP0006014', 'BC214B14', 'TV003', 9, 'EV001', 58, NULL),
(36, '3N1AB7AP0006015', 'BC215B15', 'TV003', 10, 'EV001', 59, NULL),
(37, '3N1AB7AP0006016', 'BC216B16', 'TV002', 3, 'EV001', 60, NULL),
(38, '3N1AB7AP0006017', 'BC217B17', 'TV002', 4, 'EV001', 61, NULL),
(39, '3N1AB7AP0006018', 'BC218B18', 'TV002', 5, 'EV001', 62, NULL),
(40, '3N1AB7AP0006019', 'BC219B19', 'TV002', 6, 'EV001', 63, NULL);

-- ==========================================
-- REPRESENTANTES DE ESTABLECIMIENTO
-- ==========================================

INSERT INTO REP_ESTABLECIMIENTO (numero, rfc, repNombre, repApellPat, repApellMa, telefono, email, fecha_registro, empleado, edo_rep_establecimiento) VALUES
(1, 'GINA500001', 'Gina', 'Córdoba', 'Liszt', '(664)6000001', 'gina.córdoba1@gmail.com', '2026-07-21', 4, 'ERE001'),
(2, 'JOAN500002', 'Joana', 'Mar', 'Ríos', '(664)6000002', 'joana.mar2@gmail.com', '2026-07-21', 4, 'ERE001'),
(3, 'MANU500003', 'Manuel', 'Méndez', 'Hernández', '(664)6000003', 'manuel.méndez3@gmail.com', '2026-07-21', 4, 'ERE001'),
(4, 'JOSÉ500004', 'José', 'Pérez', 'Salas', '(664)6000004', 'josé.pérez4@gmail.com', '2026-07-21', 4, 'ERE001'),
(5, 'JESÚ500005', 'Jesús', 'Vázquez', 'Arce', '(664)6000005', 'jesús.vázquez5@gmail.com', '2026-07-21', 4, 'ERE001'),
(6, 'PAOL500006', 'Paola', 'Marín', 'Ceballos', '(664)6000006', 'paola.marín6@gmail.com', '2026-07-21', 5, 'ERE001'),
(7, 'MART500007', 'Martha', 'Castro', 'Carreño', '(664)6000007', 'martha.castro7@gmail.com', '2026-07-21', 5, 'ERE001'),
(8, 'JORG500008', 'Jorge', 'Carrasco', 'Martínez', '(664)6000008', 'jorge.carrasco8@gmail.com', '2026-07-21', 5, 'ERE001'),
(9, 'JUAN500009', 'Juan', 'López', 'García', '(664)6000009', 'juan.lópez9@gmail.com', '2026-07-21', 5, 'ERE001'),
(10, 'MARC500010', 'Marco', 'Solano', 'Fernández', '(664)6000010', 'marco.solano10@gmail.com', '2026-07-21', 5, 'ERE001'),
(11, 'RAÚL500011', 'Raúl', 'Lucio', 'Valdez', '(664)6000011', 'raúl.lucio11@gmail.com', '2026-07-21', 6, 'ERE001'),
(12, 'YADI500012', 'Yadira', 'Valdez', 'Medina', '(664)6000012', 'yadira.valdez12@gmail.com', '2026-07-21', 6, 'ERE001'),
(13, 'ISRA500013', 'Israel', 'González', 'Niebla', '(664)6000013', 'israel.gonzález13@gmail.com', '2026-07-21', 6, 'ERE001'),
(14, 'NOER500014', 'Noe', 'Rivas', 'Gutiérrez', '(664)6000014', 'noe.rivas14@gmail.com', '2026-07-21', 6, 'ERE001'),
(15, 'ANDR500015', 'Andrés', 'Espinoza', 'Manzano', '(664)6000015', 'andrés.espinoza15@gmail.com', '2026-07-21', 6, 'ERE001'),
(16, 'SELE500016', 'Selene', 'Orozco', 'Bracamontes', '(664)6000016', 'selene.orozco16@gmail.com', '2026-07-21', 7, 'ERE001'),
(17, 'ROGE500017', 'Rogelio', 'Velazco', 'Campos', '(664)6000017', 'rogelio.velazco17@gmail.com', '2026-07-21', 7, 'ERE001'),
(18, 'ÁNGE500018', 'Ángeles', 'Mayén', 'Padua', '(664)6000018', 'ángeles.mayén18@gmail.com', '2026-07-21', 7, 'ERE001'),
(19, 'JONA500019', 'Jonathan', 'Rabelero', 'Aguilar', '(664)6000019', 'jonathan.rabelero19@gmail.com', '2026-07-21', 7, 'ERE001'),
(20, 'ENRI500020', 'Enrique', 'Díaz', 'Zavala', '(664)6000020', 'enrique.díaz20@gmail.com', '2026-07-21', 7, 'ERE001'),
(21, 'SAND500021', 'Sandra', 'Fuentes', 'Mora', '(664)6000021', 'sandra.fuentes21@gmail.com', '2026-07-21', 8, 'ERE001'),
(22, 'PABL500022', 'Pablo', 'Ibarra', 'Soto', '(664)6000022', 'pablo.ibarra22@gmail.com', '2026-07-21', 8, 'ERE001'),
(23, 'LAUR500023', 'Laura', 'Montes', 'Villa', '(664)6000023', 'laura.montes23@gmail.com', '2026-07-21', 8, 'ERE001'),
(24, 'DIEG500024', 'Diego', 'Reyes', 'Cruz', '(664)6000024', 'diego.reyes24@gmail.com', '2026-07-21', 8, 'ERE001'),
(25, 'CARM500025', 'Carmen', 'Salinas', 'Vega', '(664)6000025', 'carmen.salinas25@gmail.com', '2026-07-21', 8, 'ERE001'),
(26, 'HÉCT500026', 'Héctor', 'Ponce', 'Luna', '(664)6000026', 'héctor.ponce26@gmail.com', '2026-07-21', 9, 'ERE001'),
(27, 'IRMA500027', 'Irma', 'Delgado', 'Ríos', '(664)6000027', 'irma.delgado27@gmail.com', '2026-07-21', 9, 'ERE001'),
(28, 'OSCA500028', 'Oscar', 'Cabrera', 'Flores', '(664)6000028', 'oscar.cabrera28@gmail.com', '2026-07-21', 9, 'ERE001'),
(29, 'YOLA500029', 'Yolanda', 'Meza', 'Trejo', '(664)6000029', 'yolanda.meza29@gmail.com', '2026-07-21', 9, 'ERE001'),
(30, 'ARTU500030', 'Arturo', 'Serrano', 'Pérez', '(664)6000030', 'arturo.serrano30@gmail.com', '2026-07-21', 9, 'ERE001'),
(31, 'NORM500031', 'Norma', 'Cisneros', 'Alba', '(664)6000031', 'norma.cisneros31@gmail.com', '2026-07-21', 10, 'ERE001'),
(32, 'FELI500032', 'Felipe', 'Guerrero', 'Ruiz', '(664)6000032', 'felipe.guerrero32@gmail.com', '2026-07-21', 10, 'ERE001'),
(33, 'BLAN500033', 'Blanca', 'Navarro', 'Sanz', '(664)6000033', 'blanca.navarro33@gmail.com', '2026-07-21', 10, 'ERE001'),
(34, 'RAÚL500034', 'Raúl', 'Espino', 'Díaz', '(664)6000034', 'raúl.espino34@gmail.com', '2026-07-21', 10, 'ERE001'),
(35, 'ALMA500035', 'Alma', 'Herrera', 'Mora', '(664)6000035', 'alma.herrera35@gmail.com', '2026-07-21', 10, 'ERE001'),
(36, 'VÍCT500036', 'Víctor', 'Pacheco', 'León', '(664)6000036', 'víctor.pacheco36@gmail.com', '2026-07-21', 11, 'ERE001'),
(37, 'ROSA500037', 'Rosa', 'Cárdenas', 'Gil', '(664)6000037', 'rosa.cárdenas37@gmail.com', '2026-07-21', 11, 'ERE001'),
(38, 'TOMÁ500038', 'Tomás', 'Aguilar', 'Vega', '(664)6000038', 'tomás.aguilar38@gmail.com', '2026-07-21', 11, 'ERE001'),
(39, 'ELEN500039', 'Elena', 'Domínguez', 'Ramos', '(664)6000039', 'elena.domínguez39@gmail.com', '2026-07-21', 11, 'ERE001'),
(40, 'JAVI500040', 'Javier', 'Ortega', 'Muñoz', '(664)6000040', 'javier.ortega40@gmail.com', '2026-07-21', 11, 'ERE001'),
(41, 'SILV500041', 'Silvia', 'Barrera', 'Nava', '(664)6000041', 'silvia.barrera41@gmail.com', '2026-07-21', 12, 'ERE001'),
(42, 'RAMÓ500042', 'Ramón', 'Fuentes', 'Mora', '(664)6000042', 'ramón.fuentes42@gmail.com', '2026-07-21', 12, 'ERE001'),
(43, 'LUPI500043', 'Lupita', 'Reyes', 'Soto', '(664)6000043', 'lupita.reyes43@gmail.com', '2026-07-21', 12, 'ERE001'),
(44, 'GERA500044', 'Gerardo', 'Ávila', 'Cruz', '(664)6000044', 'gerardo.ávila44@gmail.com', '2026-07-21', 12, 'ERE001'),
(45, 'PILA500045', 'Pilar', 'Méndez', 'Vega', '(664)6000045', 'pilar.méndez45@gmail.com', '2026-07-21', 12, 'ERE001'),
(46, 'ABEL500046', 'Abel', 'Cano', 'Luna', '(664)6000046', 'abel.cano46@gmail.com', '2026-07-21', 13, 'ERE001'),
(47, 'VERÓ500047', 'Verónica', 'Palacios', 'Ríos', '(664)6000047', 'verónica.palacios47@gmail.com', '2026-07-21', 13, 'ERE001'),
(48, 'MARI500048', 'Mario', 'Soto', 'Flores', '(664)6000048', 'mario.soto48@gmail.com', '2026-07-21', 13, 'ERE001'),
(49, 'GRAC500049', 'Graciela', 'Mora', 'Trejo', '(664)6000049', 'graciela.mora49@gmail.com', '2026-07-21', 13, 'ERE001'),
(50, 'IGNA500050', 'Ignacio', 'Ramos', 'Pérez', '(664)6000050', 'ignacio.ramos50@gmail.com', '2026-07-21', 13, 'ERE001');

INSERT INTO ESTABLECIMIENTO (numero, nombre, estCalle, estNumero, estColonia, telefono, latitud, longitud, fecha_registro, zona, empleado, entrega, rep_establecimiento, edo_establecimiento) VALUES
(1, 'Abarrotes Córdoba', 'Av. Revolución', '101', 'Playas de Tijuana', '(664)7000001', 32.5288, -117.1244, '2026-07-21', 1, 4, NULL, 1, 'EST001'),
(2, 'Minisuper Mar', 'Blvd. Insurgentes', '102', 'Playas de Tijuana', '(664)7000002', 32.532, -117.118, '2026-07-21', 1, 4, NULL, 2, 'EST001'),
(3, 'Tienda Méndez', 'Calle Segunda', '103', 'Playas de Tijuana', '(664)7000003', 32.535, -117.13, '2026-07-21', 1, 4, NULL, 3, 'EST001'),
(4, 'Miscelánea Pérez', 'Av. Constitución', '104', 'Playas de Tijuana', '(664)7000004', 32.525, -117.135, '2026-07-21', 1, 4, NULL, 4, 'EST001'),
(5, 'Papelería Vázquez', 'Blvd. Díaz Ordaz', '105', 'Playas de Tijuana', '(664)7000005', 32.52, -117.12, '2026-07-21', 1, 4, NULL, 5, 'EST001'),
(6, 'Farmacia Marín', 'Calle Benito Juárez', '106', 'Centro', '(664)7000006', 32.53, -117.038, '2026-07-21', 2, 5, NULL, 6, 'EST001'),
(7, 'Ferretería Castro', 'Av. Internacional', '107', 'Centro', '(664)7000007', 32.525, -117.045, '2026-07-21', 2, 5, NULL, 7, 'EST001'),
(8, 'Tortillería Carrasco', 'Blvd. Agua Caliente', '108', 'Centro', '(664)7000008', 32.535, -117.03, '2026-07-21', 2, 5, NULL, 8, 'EST001'),
(9, 'Carnicería López', 'Av. Padre Kino', '109', 'Centro', '(664)7000009', 32.528, -117.05, '2026-07-21', 2, 5, NULL, 9, 'EST001'),
(10, 'Dulcería Solano', 'Blvd. Las Torres', '110', 'Centro', '(664)7000010', 32.522, -117.042, '2026-07-21', 2, 5, NULL, 10, 'EST001'),
(11, 'Abarrotes Lucio', 'Av. Rodríguez', '111', 'La Mesa Norte', '(664)7000011', 32.51, -117.02, '2026-07-21', 3, 6, NULL, 11, 'EST001'),
(12, 'Minisuper Valdez', 'Calle Ensenada', '112', 'La Mesa Norte', '(664)7000012', 32.515, -117.015, '2026-07-21', 3, 6, NULL, 12, 'EST001'),
(13, 'Tienda González', 'Blvd. Cuauhtémoc', '113', 'La Mesa Norte', '(664)7000013', 32.505, -117.025, '2026-07-21', 3, 6, NULL, 13, 'EST001'),
(14, 'Miscelánea Rivas', 'Av. Río Tijuana', '114', 'La Mesa Norte', '(664)7000014', 32.512, -117.01, '2026-07-21', 3, 6, NULL, 14, 'EST001'),
(15, 'Papelería Espinoza', 'Calle Morelos', '115', 'La Mesa Norte', '(664)7000015', 32.508, -117.03, '2026-07-21', 3, 6, NULL, 15, 'EST001'),
(16, 'Farmacia Orozco', 'Blvd. Fundadores', '116', 'Otay Poniente', '(664)7000016', 32.49, -117.06, '2026-07-21', 4, 7, NULL, 16, 'EST001'),
(17, 'Ferretería Velazco', 'Av. Via Rápida', '117', 'Otay Poniente', '(664)7000017', 32.495, -117.055, '2026-07-21', 4, 7, NULL, 17, 'EST001'),
(18, 'Tortillería Mayén', 'Calle Guadalupe Victoria', '118', 'Otay Poniente', '(664)7000018', 32.485, -117.065, '2026-07-21', 4, 7, NULL, 18, 'EST001'),
(19, 'Carnicería Rabelero', 'Blvd. Colosio', '119', 'Otay Poniente', '(664)7000019', 32.488, -117.07, '2026-07-21', 4, 7, NULL, 19, 'EST001'),
(20, 'Dulcería Díaz', 'Av. Tecnológico', '120', 'Otay Poniente', '(664)7000020', 32.492, -117.05, '2026-07-21', 4, 7, NULL, 20, 'EST001'),
(21, 'Abarrotes Fuentes', 'Av. Revolución', '121', 'Cacho', '(664)7000021', 32.505, -117.045, '2026-07-21', 5, 8, NULL, 21, 'EST001'),
(22, 'Minisuper Ibarra', 'Blvd. Insurgentes', '122', 'Cacho', '(664)7000022', 32.5, -117.05, '2026-07-21', 5, 8, NULL, 22, 'EST001'),
(23, 'Tienda Montes', 'Calle Segunda', '123', 'Cacho', '(664)7000023', 32.51, -117.04, '2026-07-21', 5, 8, NULL, 23, 'EST001'),
(24, 'Miscelánea Reyes', 'Av. Constitución', '124', 'Cacho', '(664)7000024', 32.502, -117.055, '2026-07-21', 5, 8, NULL, 24, 'EST001'),
(25, 'Papelería Salinas', 'Blvd. Díaz Ordaz', '125', 'Cacho', '(664)7000025', 32.498, -117.04, '2026-07-21', 5, 8, NULL, 25, 'EST001'),
(26, 'Farmacia Ponce', 'Calle Benito Juárez', '126', 'Mesa de Otay', '(664)7000026', 32.495, -116.98, '2026-07-21', 6, 9, NULL, 26, 'EST001'),
(27, 'Ferretería Delgado', 'Av. Internacional', '127', 'Mesa de Otay', '(664)7000027', 32.5, -116.975, '2026-07-21', 6, 9, NULL, 27, 'EST001'),
(28, 'Tortillería Cabrera', 'Blvd. Agua Caliente', '128', 'Mesa de Otay', '(664)7000028', 32.49, -116.985, '2026-07-21', 6, 9, NULL, 28, 'EST001'),
(29, 'Carnicería Meza', 'Av. Padre Kino', '129', 'Mesa de Otay', '(664)7000029', 32.492, -116.99, '2026-07-21', 6, 9, NULL, 29, 'EST001'),
(30, 'Dulcería Serrano', 'Blvd. Las Torres', '130', 'Mesa de Otay', '(664)7000030', 32.498, -116.97, '2026-07-21', 6, 9, NULL, 30, 'EST001'),
(31, 'Abarrotes Cisneros', 'Av. Rodríguez', '131', 'El Florido', '(664)7000031', 32.47, -116.94, '2026-07-21', 7, 10, NULL, 31, 'EST001'),
(32, 'Minisuper Guerrero', 'Calle Ensenada', '132', 'El Florido', '(664)7000032', 32.475, -116.935, '2026-07-21', 7, 10, NULL, 32, 'EST001'),
(33, 'Tienda Navarro', 'Blvd. Cuauhtémoc', '133', 'El Florido', '(664)7000033', 32.465, -116.945, '2026-07-21', 7, 10, NULL, 33, 'EST001'),
(34, 'Miscelánea Espino', 'Av. Río Tijuana', '134', 'El Florido', '(664)7000034', 32.468, -116.95, '2026-07-21', 7, 10, NULL, 34, 'EST001'),
(35, 'Papelería Herrera', 'Calle Morelos', '135', 'El Florido', '(664)7000035', 32.472, -116.93, '2026-07-21', 7, 10, NULL, 35, 'EST001'),
(36, 'Farmacia Pacheco', 'Blvd. Fundadores', '136', 'Cerro Colorado', '(664)7000036', 32.45, -117.02, '2026-07-21', 8, 11, NULL, 36, 'EST001'),
(37, 'Ferretería Cárdenas', 'Av. Via Rápida', '137', 'Cerro Colorado', '(664)7000037', 32.455, -117.015, '2026-07-21', 8, 11, NULL, 37, 'EST001'),
(38, 'Tortillería Aguilar', 'Calle Guadalupe Victoria', '138', 'Cerro Colorado', '(664)7000038', 32.445, -117.025, '2026-07-21', 8, 11, NULL, 38, 'EST001'),
(39, 'Carnicería Domínguez', 'Blvd. Colosio', '139', 'Cerro Colorado', '(664)7000039', 32.448, -117.03, '2026-07-21', 8, 11, NULL, 39, 'EST001'),
(40, 'Dulcería Ortega', 'Av. Tecnológico', '140', 'Cerro Colorado', '(664)7000040', 32.452, -117.01, '2026-07-21', 8, 11, NULL, 40, 'EST001'),
(41, 'Abarrotes Barrera', 'Av. Revolución', '141', 'San Antonio de los Buenos', '(664)7000041', 32.43, -116.96, '2026-07-21', 9, 12, NULL, 41, 'EST001'),
(42, 'Minisuper Fuentes', 'Blvd. Insurgentes', '142', 'San Antonio de los Buenos', '(664)7000042', 32.435, -116.955, '2026-07-21', 9, 12, NULL, 42, 'EST001'),
(43, 'Tienda Reyes', 'Calle Segunda', '143', 'San Antonio de los Buenos', '(664)7000043', 32.425, -116.965, '2026-07-21', 9, 12, NULL, 43, 'EST001'),
(44, 'Miscelánea Ávila', 'Av. Constitución', '144', 'San Antonio de los Buenos', '(664)7000044', 32.428, -116.97, '2026-07-21', 9, 12, NULL, 44, 'EST001'),
(45, 'Papelería Méndez', 'Blvd. Díaz Ordaz', '145', 'San Antonio de los Buenos', '(664)7000045', 32.432, -116.95, '2026-07-21', 9, 12, NULL, 45, 'EST001'),
(46, 'Farmacia Cano', 'Calle Benito Juárez', '146', 'Camino Verde', '(664)7000046', 32.41, -117.0, '2026-07-21', 10, 13, NULL, 46, 'EST001'),
(47, 'Ferretería Palacios', 'Av. Internacional', '147', 'Camino Verde', '(664)7000047', 32.415, -116.995, '2026-07-21', 10, 13, NULL, 47, 'EST001'),
(48, 'Tortillería Soto', 'Blvd. Agua Caliente', '148', 'Camino Verde', '(664)7000048', 32.405, -117.005, '2026-07-21', 10, 13, NULL, 48, 'EST001'),
(49, 'Carnicería Mora', 'Av. Padre Kino', '149', 'Camino Verde', '(664)7000049', 32.408, -117.01, '2026-07-21', 10, 13, NULL, 49, 'EST001'),
(50, 'Dulcería Ramos', 'Blvd. Las Torres', '150', 'Camino Verde', '(664)7000050', 32.412, -116.99, '2026-07-21', 10, 13, NULL, 50, 'EST001');

-- ==========================================
-- PRODUCTOS
-- ==========================================

INSERT INTO PRODUCTO (codigo, nombre, descripcion, imagen, precio, fecha_caducidad, stock, peso) VALUES
('P001', 'Sabritas Original 45g', 'Papas fritas sabor natural', '/img/sabritas_original.jpg', 13.50, '2026-09-01', 2000, 150),
('P002', 'Sabritas Adobadas 45g', 'Papas fritas sabor adobadas', '/img/sabritas_adobadas.jpg', 13.50, '2026-12-20', 1800, 150),
('P003', 'Doritos Nacho 62g', 'Totopos de maíz sabor queso nacho', '/img/doritos_nacho.jpg', 17.00, '2026-09-03', 2200, 180),
('P004', 'Doritos Flamas 62g', 'Totopos de maíz sabor flamas', '/img/doritos_flamas.jpg', 17.00, '2026-10-17', 1600, 180),
('P005', 'Cheetos Torciditos 60g', 'Botana de maíz sabor queso', '/img/cheetos_torciditos.jpg', 15.50, '2026-11-05', 1900, 180),
('P006', 'Ruffles Queso 62g', 'Papas onduladas sabor queso', '/img/ruffles_queso.jpg', 17.50, '2026-11-03', 1500, 150),
('P007', 'Rancheritos 55g', 'Totopos de maíz sabor salsa verde', '/img/rancheritos.jpg', 14.50, '2026-10-12', 1700, 180),
('P008', 'Cheetos Flamin Hot 60g', 'Botana de maíz sabor picante', '/img/cheetos_hot.jpg', 15.50, '2026-11-06', 1650, 180),
('P009', 'Sabritones Fuego 55g', 'Chicharrón de harina sabor picante', '/img/sabritones.jpg', 14.00, '2026-12-27', 1400, 150),
('P010', 'Fritos Limón y Sal 58g', 'Botana de maíz sabor limón y sal', '/img/fritos.jpg', 14.00, '2026-11-20', 1500, 180),
('P011', 'Crujitos 52g', 'Botana de trigo sabor queso', '/img/crujitos.jpg', 13.00, '2026-09-22', 1300, 150),
('P012', 'Runners 45g', 'Palitos de papa sabor natural', '/img/runners.jpg', 13.50, '2026-11-22', 1200, 150),
('P013', 'Chips Fuego 60g', 'Totopos de maíz estilo tortilla sabor fuego', '/img/chips_fuego.jpg', 16.00, '2026-09-05', 1100, 180),
('P014', 'Nachos Sabritas 60g', 'Totopos de maíz sabor queso nachos', '/img/nachos.jpg', 16.00, '2026-11-04', 1200, 180),
('P015', 'Sabritas Rancheras 45g', 'Papas fritas sabor ranchero', '/img/sabritas_rancheras.jpg', 13.50, '2026-09-24', 1300, 150),
('P016', 'Emperador Cacahuate 40g', 'Cacahuate japonés cubierto', '/img/emperador.jpg', 12.50, '2026-10-09', 1100, 240);

-- ==========================================
-- RUTAS DE VISITA
-- ==========================================

INSERT INTO RUTA_VISITA (numero, nombre, descripcion, zona, empleado, edo_ruta_visita) VALUES
(1, 'Ruta Visita Noroeste', 'Recorrido de visita a establecimientos de Zona Noroeste', 1, 4, 'ERV001'),
(2, 'Ruta Visita Norte 1', 'Recorrido de visita a establecimientos de Zona Norte 1', 2, 5, 'ERV001'),
(3, 'Ruta Visita Norte 2', 'Recorrido de visita a establecimientos de Zona Norte 2', 3, 6, 'ERV001'),
(4, 'Ruta Visita Poniente', 'Recorrido de visita a establecimientos de Zona Poniente', 4, 7, 'ERV001'),
(5, 'Ruta Visita Centro', 'Recorrido de visita a establecimientos de Zona Centro', 5, 8, 'ERV001'),
(6, 'Ruta Visita Oriente 1', 'Recorrido de visita a establecimientos de Zona Oriente 1', 6, 9, 'ERV001'),
(7, 'Ruta Visita Oriente 2', 'Recorrido de visita a establecimientos de Zona Oriente 2', 7, 10, 'ERV001'),
(8, 'Ruta Visita Sureste 1', 'Recorrido de visita a establecimientos de Zona Sureste 1', 8, 11, 'ERV001'),
(9, 'Ruta Visita Sureste 2', 'Recorrido de visita a establecimientos de Zona Sureste 2', 9, 12, 'ERV001'),
(10, 'Ruta Visita Sur', 'Recorrido de visita a establecimientos de Zona Sur', 10, 13, 'ERV001');

-- ==========================================
-- VISITAS DE AYER (completadas)
-- ==========================================

INSERT INTO VISITA (numero, observaciones, fecha, ruta_visita, establecimiento, empleado, edo_visita) VALUES
(1, NULL, '2026-07-21 08:00:00', 1, 1, 4, 'EVI004'),
(2, NULL, '2026-07-21 09:00:00', 1, 2, 4, 'EVI004'),
(3, NULL, '2026-07-21 10:00:00', 1, 3, 4, 'EVI004'),
(4, NULL, '2026-07-21 11:00:00', 1, 4, 4, 'EVI004'),
(5, NULL, '2026-07-21 12:00:00', 1, 5, 4, 'EVI004'),
(6, NULL, '2026-07-21 08:00:00', 2, 6, 5, 'EVI004'),
(7, NULL, '2026-07-21 09:00:00', 2, 7, 5, 'EVI004'),
(8, NULL, '2026-07-21 10:00:00', 2, 8, 5, 'EVI004'),
(9, NULL, '2026-07-21 11:00:00', 2, 9, 5, 'EVI004'),
(10, NULL, '2026-07-21 12:00:00', 2, 10, 5, 'EVI004'),
(11, NULL, '2026-07-21 08:00:00', 3, 11, 6, 'EVI004'),
(12, NULL, '2026-07-21 09:00:00', 3, 12, 6, 'EVI004'),
(13, NULL, '2026-07-21 10:00:00', 3, 13, 6, 'EVI004'),
(14, NULL, '2026-07-21 11:00:00', 3, 14, 6, 'EVI004'),
(15, NULL, '2026-07-21 12:00:00', 3, 15, 6, 'EVI004'),
(16, NULL, '2026-07-21 08:00:00', 4, 16, 7, 'EVI004'),
(17, NULL, '2026-07-21 09:00:00', 4, 17, 7, 'EVI004'),
(18, NULL, '2026-07-21 10:00:00', 4, 18, 7, 'EVI004'),
(19, NULL, '2026-07-21 11:00:00', 4, 19, 7, 'EVI004'),
(20, NULL, '2026-07-21 12:00:00', 4, 20, 7, 'EVI004'),
(21, NULL, '2026-07-21 08:00:00', 5, 21, 8, 'EVI004'),
(22, NULL, '2026-07-21 09:00:00', 5, 22, 8, 'EVI004'),
(23, NULL, '2026-07-21 10:00:00', 5, 23, 8, 'EVI004'),
(24, NULL, '2026-07-21 11:00:00', 5, 24, 8, 'EVI004'),
(25, NULL, '2026-07-21 12:00:00', 5, 25, 8, 'EVI004'),
(26, NULL, '2026-07-21 08:00:00', 6, 26, 9, 'EVI004'),
(27, NULL, '2026-07-21 09:00:00', 6, 27, 9, 'EVI004'),
(28, NULL, '2026-07-21 10:00:00', 6, 28, 9, 'EVI004'),
(29, NULL, '2026-07-21 11:00:00', 6, 29, 9, 'EVI004'),
(30, NULL, '2026-07-21 12:00:00', 6, 30, 9, 'EVI004'),
(31, NULL, '2026-07-21 08:00:00', 7, 31, 10, 'EVI004'),
(32, NULL, '2026-07-21 09:00:00', 7, 32, 10, 'EVI004'),
(33, NULL, '2026-07-21 10:00:00', 7, 33, 10, 'EVI004'),
(34, NULL, '2026-07-21 11:00:00', 7, 34, 10, 'EVI004'),
(35, NULL, '2026-07-21 12:00:00', 7, 35, 10, 'EVI004'),
(36, NULL, '2026-07-21 08:00:00', 8, 36, 11, 'EVI004'),
(37, NULL, '2026-07-21 09:00:00', 8, 37, 11, 'EVI004'),
(38, NULL, '2026-07-21 10:00:00', 8, 38, 11, 'EVI004'),
(39, NULL, '2026-07-21 11:00:00', 8, 39, 11, 'EVI004'),
(40, NULL, '2026-07-21 12:00:00', 8, 40, 11, 'EVI004'),
(41, NULL, '2026-07-21 08:00:00', 9, 41, 12, 'EVI004'),
(42, NULL, '2026-07-21 09:00:00', 9, 42, 12, 'EVI004'),
(43, NULL, '2026-07-21 10:00:00', 9, 43, 12, 'EVI004'),
(44, NULL, '2026-07-21 11:00:00', 9, 44, 12, 'EVI004'),
(45, NULL, '2026-07-21 12:00:00', 9, 45, 12, 'EVI004'),
(46, NULL, '2026-07-21 08:00:00', 10, 46, 13, 'EVI004'),
(47, NULL, '2026-07-21 09:00:00', 10, 47, 13, 'EVI004'),
(48, NULL, '2026-07-21 10:00:00', 10, 48, 13, 'EVI004'),
(49, NULL, '2026-07-21 11:00:00', 10, 49, 13, 'EVI004'),
(50, NULL, '2026-07-21 12:00:00', 10, 50, 13, 'EVI004');

-- ==========================================
-- PEDIDOS DE AYER
-- ==========================================

INSERT INTO PEDIDO (num, observaciones, fecha, subtotal, visita, entrega, edo_pedido) VALUES
(1, NULL, '2026-07-21 09:30:00', 1219.0, 1, NULL, 'EPD005'),
(2, NULL, '2026-07-21 10:30:00', 545, 2, NULL, 'EPD005'),
(3, NULL, '2026-07-21 11:30:00', 731, 3, NULL, 'EPD005'),
(4, NULL, '2026-07-21 12:30:00', 1622.5, 4, NULL, 'EPD005'),
(5, NULL, '2026-07-21 13:30:00', 733.0, 5, NULL, 'EPD005'),
(6, NULL, '2026-07-21 14:30:00', 672.5, 6, NULL, 'EPD005'),
(7, NULL, '2026-07-21 15:30:00', 723.0, 7, NULL, 'EPD005'),
(8, NULL, '2026-07-21 16:30:00', 1152.5, 8, NULL, 'EPD005'),
(9, NULL, '2026-07-21 17:30:00', 721.5, 9, NULL, 'EPD005'),
(10, NULL, '2026-07-21 08:30:00', 1481.5, 10, NULL, 'EPD005'),
(11, NULL, '2026-07-21 09:30:00', 807.5, 11, NULL, 'EPD005'),
(12, NULL, '2026-07-21 10:30:00', 1211, 12, NULL, 'EPD005'),
(13, NULL, '2026-07-21 11:30:00', 814.5, 13, NULL, 'EPD005'),
(14, NULL, '2026-07-21 12:30:00', 1451.5, 14, NULL, 'EPD005'),
(15, NULL, '2026-07-21 13:30:00', 1329.5, 15, NULL, 'EPD005'),
(16, NULL, '2026-07-21 14:30:00', 1151.5, 16, NULL, 'EPD005'),
(17, NULL, '2026-07-21 15:30:00', 1139.5, 17, NULL, 'EPD005'),
(18, NULL, '2026-07-21 16:30:00', 1400.5, 18, NULL, 'EPD005'),
(19, NULL, '2026-07-21 17:30:00', 1884.5, 19, NULL, 'EPD005'),
(20, NULL, '2026-07-21 08:30:00', 1135.0, 20, NULL, 'EPD005'),
(21, NULL, '2026-07-21 09:30:00', 1522.5, 21, NULL, 'EPD005'),
(22, NULL, '2026-07-21 10:30:00', 555.5, 22, NULL, 'EPD005'),
(23, NULL, '2026-07-21 11:30:00', 765, 23, NULL, 'EPD005'),
(24, NULL, '2026-07-21 12:30:00', 1459.0, 24, NULL, 'EPD005'),
(25, NULL, '2026-07-21 13:30:00', 1091.5, 25, NULL, 'EPD005'),
(26, NULL, '2026-07-21 14:30:00', 1047.5, 26, NULL, 'EPD005'),
(27, NULL, '2026-07-21 15:30:00', 1053.0, 27, NULL, 'EPD005'),
(28, NULL, '2026-07-21 16:30:00', 814, 28, NULL, 'EPD005'),
(29, NULL, '2026-07-21 17:30:00', 1920.5, 29, NULL, 'EPD005'),
(30, NULL, '2026-07-21 08:30:00', 1325.0, 30, NULL, 'EPD005'),
(31, NULL, '2026-07-21 09:30:00', 1647.0, 31, NULL, 'EPD005'),
(32, NULL, '2026-07-21 10:30:00', 911.0, 32, NULL, 'EPD005'),
(33, NULL, '2026-07-21 11:30:00', 905.5, 33, NULL, 'EPD005'),
(34, NULL, '2026-07-21 12:30:00', 1792.5, 34, NULL, 'EPD005'),
(35, NULL, '2026-07-21 13:30:00', 1480.0, 35, NULL, 'EPD005'),
(36, NULL, '2026-07-21 14:30:00', 1050.0, 36, NULL, 'EPD005'),
(37, NULL, '2026-07-21 15:30:00', 1292.5, 37, NULL, 'EPD005'),
(38, NULL, '2026-07-21 16:30:00', 686.5, 38, NULL, 'EPD005'),
(39, NULL, '2026-07-21 17:30:00', 1165, 39, NULL, 'EPD005'),
(40, NULL, '2026-07-21 08:30:00', 1117.5, 40, NULL, 'EPD005'),
(41, NULL, '2026-07-21 09:30:00', 1286.0, 41, NULL, 'EPD005'),
(42, NULL, '2026-07-21 10:30:00', 770.5, 42, NULL, 'EPD005'),
(43, NULL, '2026-07-21 11:30:00', 722.5, 43, NULL, 'EPD005'),
(44, NULL, '2026-07-21 12:30:00', 697, 44, NULL, 'EPD005'),
(45, NULL, '2026-07-21 13:30:00', 565.5, 45, NULL, 'EPD005'),
(46, NULL, '2026-07-21 14:30:00', 1114.5, 46, NULL, 'EPD005'),
(47, NULL, '2026-07-21 15:30:00', 1449.0, 47, NULL, 'EPD005'),
(48, NULL, '2026-07-21 16:30:00', 800.0, 48, NULL, 'EPD005'),
(49, NULL, '2026-07-21 17:30:00', 378.5, 49, NULL, 'EPD005'),
(50, NULL, '2026-07-21 08:30:00', 1576.5, 50, NULL, 'EPD005');

-- ==========================================
-- HOY: VISITAS EN DIFERENTES ESTADOS
-- ==========================================

INSERT INTO VISITA (numero, observaciones, fecha, ruta_visita, establecimiento, empleado, edo_visita) VALUES
(51, NULL, '2026-07-22 08:00:00', 1, 1, 4, 'EVI004'),
(52, NULL, '2026-07-22 09:00:00', 1, 2, 4, 'EVI004'),
(53, NULL, '2026-07-22 10:00:00', 1, 3, 4, 'EVI004'),
(54, NULL, '2026-07-22 11:00:00', 1, 4, 4, 'EVI004'),
(55, NULL, '2026-07-22 12:00:00', 1, 5, 4, 'EVI004'),
(56, NULL, '2026-07-22 08:00:00', 2, 6, 5, 'EVI004'),
(57, NULL, '2026-07-22 09:00:00', 2, 7, 5, 'EVI004'),
(58, NULL, '2026-07-22 10:00:00', 2, 8, 5, 'EVI004'),
(59, NULL, '2026-07-22 11:00:00', 2, 9, 5, 'EVI004'),
(60, NULL, '2026-07-22 12:00:00', 2, 10, 5, 'EVI004'),
(61, NULL, '2026-07-22 08:00:00', 3, 11, 6, 'EVI004'),
(62, NULL, '2026-07-22 09:00:00', 3, 12, 6, 'EVI004'),
(63, NULL, '2026-07-22 10:00:00', 3, 13, 6, 'EVI004'),
(64, NULL, '2026-07-22 11:00:00', 3, 14, 6, 'EVI004'),
(65, NULL, '2026-07-22 12:00:00', 3, 15, 6, 'EVI004'),
(66, NULL, '2026-07-22 08:00:00', 4, 16, 7, 'EVI004'),
(67, NULL, '2026-07-22 09:00:00', 4, 17, 7, 'EVI004'),
(68, NULL, '2026-07-22 10:00:00', 4, 18, 7, 'EVI004'),
(69, NULL, '2026-07-22 11:00:00', 4, 19, 7, 'EVI004'),
(70, NULL, '2026-07-22 12:00:00', 4, 20, 7, 'EVI004'),
(71, NULL, '2026-07-22 08:00:00', 5, 21, 8, 'EVI004'),
(72, NULL, '2026-07-22 09:00:00', 5, 22, 8, 'EVI004'),
(73, NULL, '2026-07-22 10:00:00', 5, 23, 8, 'EVI004'),
(74, NULL, '2026-07-22 11:00:00', 5, 24, 8, 'EVI004'),
(75, NULL, '2026-07-22 12:00:00', 5, 25, 8, 'EVI004'),
(76, NULL, '2026-07-22 10:00:00', 6, 26, 9, 'EVI003'),
(77, NULL, '2026-07-22 10:00:00', 6, 27, 9, 'EVI003'),
(78, NULL, '2026-07-22 10:00:00', 6, 28, 9, 'EVI003'),
(79, NULL, '2026-07-22 10:00:00', 7, 31, 10, 'EVI003'),
(80, NULL, '2026-07-22 10:00:00', 7, 32, 10, 'EVI003'),
(81, NULL, '2026-07-22 10:00:00', 7, 33, 10, 'EVI003'),
(82, NULL, '2026-07-22 10:00:00', 8, 36, 11, 'EVI003'),
(83, NULL, '2026-07-22 10:00:00', 8, 37, 11, 'EVI003'),
(84, NULL, '2026-07-22 10:00:00', 8, 38, 11, 'EVI003'),
(85, NULL, '2026-07-22 14:00:00', 9, 41, 12, 'EVI001'),
(86, NULL, '2026-07-22 14:00:00', 9, 42, 12, 'EVI001'),
(87, NULL, '2026-07-22 14:00:00', 9, 43, 12, 'EVI001'),
(88, NULL, '2026-07-22 14:00:00', 9, 44, 12, 'EVI001'),
(89, NULL, '2026-07-22 14:00:00', 9, 45, 12, 'EVI001'),
(90, NULL, '2026-07-22 14:00:00', 10, 46, 13, 'EVI001'),
(91, NULL, '2026-07-22 14:00:00', 10, 47, 13, 'EVI001'),
(92, NULL, '2026-07-22 14:00:00', 10, 48, 13, 'EVI001'),
(93, NULL, '2026-07-22 14:00:00', 10, 49, 13, 'EVI001'),
(94, NULL, '2026-07-22 14:00:00', 10, 50, 13, 'EVI001');

INSERT INTO PEDIDO (num, observaciones, fecha, subtotal, visita, entrega, edo_pedido) VALUES
(51, NULL, '2026-07-22 08:30:00', 1511.0, 51, NULL, 'EPD001'),
(52, NULL, '2026-07-22 09:30:00', 1501.0, 52, NULL, 'EPD001'),
(53, NULL, '2026-07-22 10:30:00', 1315.0, 53, NULL, 'EPD001'),
(54, NULL, '2026-07-22 11:30:00', 1409.5, 54, NULL, 'EPD001'),
(55, NULL, '2026-07-22 12:30:00', 781.5, 55, NULL, 'EPD001'),
(56, NULL, '2026-07-22 08:30:00', 1346.5, 56, NULL, 'EPD001'),
(57, NULL, '2026-07-22 09:30:00', 1434.0, 57, NULL, 'EPD001'),
(58, NULL, '2026-07-22 10:30:00', 1115, 58, NULL, 'EPD001'),
(59, NULL, '2026-07-22 11:30:00', 1072.5, 59, NULL, 'EPD001'),
(60, NULL, '2026-07-22 12:30:00', 457.0, 60, NULL, 'EPD001'),
(61, NULL, '2026-07-22 08:30:00', 868.5, 61, NULL, 'EPD001'),
(62, NULL, '2026-07-22 09:30:00', 905.0, 62, NULL, 'EPD001'),
(63, NULL, '2026-07-22 10:30:00', 1498.0, 63, NULL, 'EPD001'),
(64, NULL, '2026-07-22 11:30:00', 648.0, 64, NULL, 'EPD001'),
(65, NULL, '2026-07-22 12:30:00', 970.0, 65, NULL, 'EPD001'),
(66, NULL, '2026-07-22 08:30:00', 1763.5, 66, NULL, 'EPD001'),
(67, NULL, '2026-07-22 09:30:00', 425.5, 67, NULL, 'EPD001'),
(68, NULL, '2026-07-22 10:30:00', 662, 68, NULL, 'EPD001'),
(69, NULL, '2026-07-22 11:30:00', 1261.0, 69, NULL, 'EPD001'),
(70, NULL, '2026-07-22 12:30:00', 1215.0, 70, NULL, 'EPD001'),
(71, NULL, '2026-07-22 08:30:00', 803.0, 71, NULL, 'EPD001'),
(72, NULL, '2026-07-22 09:30:00', 707.5, 72, NULL, 'EPD001'),
(73, NULL, '2026-07-22 10:30:00', 2067.5, 73, NULL, 'EPD001'),
(74, NULL, '2026-07-22 11:30:00', 1916.0, 74, NULL, 'EPD001'),
(75, NULL, '2026-07-22 12:30:00', 1339.0, 75, NULL, 'EPD001');

-- ==========================================
-- DETALLE_PEDIDO
-- ==========================================

INSERT INTO DETALLE_PEDIDO (num_pedido, cod_producto, cantidad, precioUnitario, importe) VALUES
(1, 'P004', 17, 17, 289),
(1, 'P001', 17, 13.5, 229.5),
(1, 'P012', 14, 13.5, 189.0),
(1, 'P005', 33, 15.5, 511.5),
(2, 'P003', 23, 17, 391),
(2, 'P010', 11, 14, 154),
(3, 'P003', 17, 17, 289),
(3, 'P004', 26, 17, 442),
(4, 'P001', 30, 13.5, 405.0),
(4, 'P009', 32, 14, 448),
(4, 'P004', 27, 17, 459),
(4, 'P012', 23, 13.5, 310.5),
(5, 'P015', 18, 13.5, 243.0),
(5, 'P010', 35, 14, 490),
(6, 'P006', 23, 17.5, 402.5),
(6, 'P012', 20, 13.5, 270.0),
(7, 'P005', 20, 15.5, 310.0),
(7, 'P004', 13, 17, 221),
(7, 'P013', 12, 16, 192),
(8, 'P004', 21, 17, 357),
(8, 'P006', 29, 17.5, 507.5),
(8, 'P014', 18, 16, 288),
(9, 'P015', 13, 13.5, 175.5),
(9, 'P009', 39, 14, 546),
(10, 'P003', 36, 17, 612),
(10, 'P009', 30, 14, 420),
(10, 'P005', 29, 15.5, 449.5),
(11, 'P007', 11, 14.5, 159.5),
(11, 'P012', 31, 13.5, 418.5),
(11, 'P002', 17, 13.5, 229.5),
(12, 'P003', 37, 17, 629),
(12, 'P014', 13, 16, 208),
(12, 'P004', 22, 17, 374),
(13, 'P015', 21, 13.5, 283.5),
(13, 'P011', 15, 13, 195),
(13, 'P014', 21, 16, 336),
(14, 'P007', 32, 14.5, 464.0),
(14, 'P011', 39, 13, 507),
(14, 'P005', 31, 15.5, 480.5),
(15, 'P003', 27, 17, 459),
(15, 'P010', 33, 14, 462),
(15, 'P011', 17, 13, 221),
(15, 'P016', 15, 12.5, 187.5),
(16, 'P013', 32, 16, 512),
(16, 'P005', 27, 15.5, 418.5),
(16, 'P011', 17, 13, 221),
(17, 'P011', 11, 13, 143),
(17, 'P014', 17, 16, 272),
(17, 'P013', 36, 16, 576),
(17, 'P015', 11, 13.5, 148.5),
(18, 'P013', 16, 16, 256),
(18, 'P005', 39, 15.5, 604.5),
(18, 'P002', 40, 13.5, 540.0),
(19, 'P011', 22, 13, 286),
(19, 'P004', 38, 17, 646),
(19, 'P016', 39, 12.5, 487.5),
(19, 'P008', 30, 15.5, 465.0),
(20, 'P005', 17, 15.5, 263.5),
(20, 'P016', 33, 12.5, 412.5),
(20, 'P003', 27, 17, 459),
(21, 'P009', 38, 14, 532),
(21, 'P012', 28, 13.5, 378.0),
(21, 'P010', 22, 14, 308),
(21, 'P007', 21, 14.5, 304.5),
(22, 'P005', 25, 15.5, 387.5),
(22, 'P009', 12, 14, 168),
(23, 'P004', 30, 17, 510),
(23, 'P003', 15, 17, 255),
(24, 'P014', 22, 16, 352),
(24, 'P010', 29, 14, 406),
(24, 'P002', 24, 13.5, 324.0),
(24, 'P007', 26, 14.5, 377.0),
(25, 'P001', 13, 13.5, 175.5),
(25, 'P011', 31, 13, 403),
(25, 'P012', 38, 13.5, 513.0),
(26, 'P009', 13, 14, 182),
(26, 'P013', 19, 16, 304),
(26, 'P011', 23, 13, 299),
(26, 'P006', 15, 17.5, 262.5),
(27, 'P001', 18, 13.5, 243.0),
(27, 'P012', 26, 13.5, 351.0),
(27, 'P015', 34, 13.5, 459.0),
(28, 'P004', 30, 17, 510),
(28, 'P014', 19, 16, 304),
(29, 'P007', 15, 14.5, 217.5),
(29, 'P003', 27, 17, 459),
(29, 'P006', 40, 17.5, 700.0),
(29, 'P013', 34, 16, 544),
(30, 'P001', 10, 13.5, 135.0),
(30, 'P010', 13, 14, 182),
(30, 'P006', 39, 17.5, 682.5),
(30, 'P008', 21, 15.5, 325.5),
(31, 'P008', 38, 15.5, 589.0),
(31, 'P001', 28, 13.5, 378.0),
(31, 'P004', 40, 17, 680),
(32, 'P003', 25, 17, 425),
(32, 'P012', 36, 13.5, 486.0),
(33, 'P005', 31, 15.5, 480.5),
(33, 'P003', 25, 17, 425),
(34, 'P006', 23, 17.5, 402.5),
(34, 'P005', 40, 15.5, 620.0),
(34, 'P009', 16, 14, 224),
(34, 'P010', 39, 14, 546),
(35, 'P007', 31, 14.5, 449.5),
(35, 'P012', 30, 13.5, 405.0),
(35, 'P005', 21, 15.5, 325.5),
(35, 'P016', 24, 12.5, 300.0),
(36, 'P015', 12, 13.5, 162.0),
(36, 'P002', 20, 13.5, 270.0),
(36, 'P004', 10, 17, 170),
(36, 'P014', 28, 16, 448),
(37, 'P008', 12, 15.5, 186.0),
(37, 'P010', 32, 14, 448),
(37, 'P004', 30, 17, 510),
(37, 'P001', 11, 13.5, 148.5),
(38, 'P003', 11, 17, 187),
(38, 'P015', 37, 13.5, 499.5),
(39, 'P003', 18, 17, 306),
(39, 'P009', 31, 14, 434),
(39, 'P004', 25, 17, 425),
(40, 'P005', 39, 15.5, 604.5),
(40, 'P012', 38, 13.5, 513.0),
(41, 'P016', 35, 12.5, 437.5),
(41, 'P004', 23, 17, 391),
(41, 'P013', 16, 16, 256),
(41, 'P008', 13, 15.5, 201.5),
(42, 'P014', 23, 16, 368),
(42, 'P006', 23, 17.5, 402.5),
(43, 'P002', 30, 13.5, 405.0),
(43, 'P011', 13, 13, 169),
(43, 'P015', 11, 13.5, 148.5),
(44, 'P011', 13, 13, 169),
(44, 'P013', 17, 16, 272),
(44, 'P014', 16, 16, 256),
(45, 'P015', 23, 13.5, 310.5),
(45, 'P003', 15, 17, 255),
(46, 'P015', 39, 13.5, 526.5),
(46, 'P004', 12, 17, 204),
(46, 'P014', 24, 16, 384),
(47, 'P004', 36, 17, 612),
(47, 'P001', 10, 13.5, 135.0),
(47, 'P011', 12, 13, 156),
(47, 'P009', 39, 14, 546),
(48, 'P006', 25, 17.5, 437.5),
(48, 'P007', 25, 14.5, 362.5),
(49, 'P013', 11, 16, 176),
(49, 'P015', 15, 13.5, 202.5),
(50, 'P001', 39, 13.5, 526.5),
(50, 'P007', 35, 14.5, 507.5),
(50, 'P005', 35, 15.5, 542.5),
(51, 'P010', 40, 14, 560),
(51, 'P007', 33, 14.5, 478.5),
(51, 'P012', 35, 13.5, 472.5),
(52, 'P016', 16, 12.5, 200.0),
(52, 'P003', 40, 17, 680),
(52, 'P004', 11, 17, 187),
(52, 'P005', 28, 15.5, 434.0),
(53, 'P002', 11, 13.5, 148.5),
(53, 'P012', 28, 13.5, 378.0),
(53, 'P006', 25, 17.5, 437.5),
(53, 'P001', 26, 13.5, 351.0),
(54, 'P006', 37, 17.5, 647.5),
(54, 'P001', 15, 13.5, 202.5),
(54, 'P009', 12, 14, 168),
(54, 'P002', 29, 13.5, 391.5),
(55, 'P008', 13, 15.5, 201.5),
(55, 'P007', 40, 14.5, 580.0),
(56, 'P008', 29, 15.5, 449.5),
(56, 'P010', 12, 14, 168),
(56, 'P015', 23, 13.5, 310.5),
(56, 'P001', 31, 13.5, 418.5),
(57, 'P011', 31, 13, 403),
(57, 'P015', 32, 13.5, 432.0),
(57, 'P005', 20, 15.5, 310.0),
(57, 'P004', 17, 17, 289),
(58, 'P013', 30, 16, 480),
(58, 'P003', 19, 17, 323),
(58, 'P011', 24, 13, 312),
(59, 'P003', 29, 17, 493),
(59, 'P001', 28, 13.5, 378.0),
(59, 'P008', 13, 15.5, 201.5),
(60, 'P007', 18, 14.5, 261.0),
(60, 'P009', 14, 14, 196),
(61, 'P003', 21, 17, 357),
(61, 'P015', 19, 13.5, 256.5),
(61, 'P004', 15, 17, 255),
(62, 'P010', 30, 14, 420),
(62, 'P016', 26, 12.5, 325.0),
(62, 'P013', 10, 16, 160),
(63, 'P010', 40, 14, 560),
(63, 'P015', 38, 13.5, 513.0),
(63, 'P011', 14, 13, 182),
(63, 'P002', 18, 13.5, 243.0),
(64, 'P004', 27, 17, 459),
(64, 'P012', 14, 13.5, 189.0),
(65, 'P010', 32, 14, 448),
(65, 'P016', 20, 12.5, 250.0),
(65, 'P004', 16, 17, 272),
(66, 'P009', 38, 14, 532),
(66, 'P016', 39, 12.5, 487.5),
(66, 'P008', 37, 15.5, 573.5),
(66, 'P005', 11, 15.5, 170.5),
(67, 'P014', 18, 16, 288),
(67, 'P016', 11, 12.5, 137.5),
(68, 'P011', 14, 13, 182),
(68, 'P013', 30, 16, 480),
(69, 'P006', 27, 17.5, 472.5),
(69, 'P012', 32, 13.5, 432.0),
(69, 'P008', 23, 15.5, 356.5),
(70, 'P001', 38, 13.5, 513.0),
(70, 'P002', 14, 13.5, 189.0),
(70, 'P015', 27, 13.5, 364.5),
(70, 'P012', 11, 13.5, 148.5),
(71, 'P005', 11, 15.5, 170.5),
(71, 'P007', 19, 14.5, 275.5),
(71, 'P003', 21, 17, 357),
(72, 'P012', 31, 13.5, 418.5),
(72, 'P004', 17, 17, 289),
(73, 'P004', 38, 17, 646),
(73, 'P006', 37, 17.5, 647.5),
(73, 'P013', 23, 16, 368),
(73, 'P009', 29, 14, 406),
(74, 'P005', 35, 15.5, 542.5),
(74, 'P015', 35, 13.5, 472.5),
(74, 'P004', 15, 17, 255),
(74, 'P003', 38, 17, 646),
(75, 'P001', 39, 13.5, 526.5),
(75, 'P003', 20, 17, 340),
(75, 'P012', 35, 13.5, 472.5);

-- ==========================================
-- ENTREGAS DE AYER (completadas)
-- ==========================================

INSERT INTO ENTREGA (numero, fecha_creacion, fecha_entrega, empleado, edo_entrega) VALUES
(1, '2026-07-21', '2026-07-21 17:00:00', 44, 'EEN004'),
(2, '2026-07-21', '2026-07-21 17:00:00', 45, 'EEN004'),
(3, '2026-07-21', '2026-07-21 17:00:00', 46, 'EEN004'),
(4, '2026-07-21', '2026-07-21 17:00:00', 47, 'EEN004'),
(5, '2026-07-21', '2026-07-21 17:00:00', 48, 'EEN004'),
(6, '2026-07-21', '2026-07-21 17:00:00', 49, 'EEN004'),
(7, '2026-07-21', '2026-07-21 17:00:00', 50, 'EEN004'),
(8, '2026-07-21', '2026-07-21 17:00:00', 51, 'EEN004'),
(9, '2026-07-21', '2026-07-21 17:00:00', 52, 'EEN004'),
(10, '2026-07-21', '2026-07-21 17:00:00', 53, 'EEN004');

-- Asignar entregas a pedidos de ayer
UPDATE PEDIDO SET entrega = 1, edo_pedido = 'EPD005' WHERE num = 1;
UPDATE PEDIDO SET entrega = 1, edo_pedido = 'EPD005' WHERE num = 2;
UPDATE PEDIDO SET entrega = 1, edo_pedido = 'EPD005' WHERE num = 3;
UPDATE PEDIDO SET entrega = 1, edo_pedido = 'EPD005' WHERE num = 4;
UPDATE PEDIDO SET entrega = 1, edo_pedido = 'EPD005' WHERE num = 5;
UPDATE PEDIDO SET entrega = 2, edo_pedido = 'EPD005' WHERE num = 6;
UPDATE PEDIDO SET entrega = 2, edo_pedido = 'EPD005' WHERE num = 7;
UPDATE PEDIDO SET entrega = 2, edo_pedido = 'EPD005' WHERE num = 8;
UPDATE PEDIDO SET entrega = 2, edo_pedido = 'EPD005' WHERE num = 9;
UPDATE PEDIDO SET entrega = 2, edo_pedido = 'EPD005' WHERE num = 10;
UPDATE PEDIDO SET entrega = 3, edo_pedido = 'EPD005' WHERE num = 11;
UPDATE PEDIDO SET entrega = 3, edo_pedido = 'EPD005' WHERE num = 12;
UPDATE PEDIDO SET entrega = 3, edo_pedido = 'EPD005' WHERE num = 13;
UPDATE PEDIDO SET entrega = 3, edo_pedido = 'EPD005' WHERE num = 14;
UPDATE PEDIDO SET entrega = 3, edo_pedido = 'EPD005' WHERE num = 15;
UPDATE PEDIDO SET entrega = 4, edo_pedido = 'EPD005' WHERE num = 16;
UPDATE PEDIDO SET entrega = 4, edo_pedido = 'EPD005' WHERE num = 17;
UPDATE PEDIDO SET entrega = 4, edo_pedido = 'EPD005' WHERE num = 18;
UPDATE PEDIDO SET entrega = 4, edo_pedido = 'EPD005' WHERE num = 19;
UPDATE PEDIDO SET entrega = 4, edo_pedido = 'EPD005' WHERE num = 20;
UPDATE PEDIDO SET entrega = 5, edo_pedido = 'EPD005' WHERE num = 21;
UPDATE PEDIDO SET entrega = 5, edo_pedido = 'EPD005' WHERE num = 22;
UPDATE PEDIDO SET entrega = 5, edo_pedido = 'EPD005' WHERE num = 23;
UPDATE PEDIDO SET entrega = 5, edo_pedido = 'EPD005' WHERE num = 24;
UPDATE PEDIDO SET entrega = 5, edo_pedido = 'EPD005' WHERE num = 25;
UPDATE PEDIDO SET entrega = 6, edo_pedido = 'EPD005' WHERE num = 26;
UPDATE PEDIDO SET entrega = 6, edo_pedido = 'EPD005' WHERE num = 27;
UPDATE PEDIDO SET entrega = 6, edo_pedido = 'EPD005' WHERE num = 28;
UPDATE PEDIDO SET entrega = 6, edo_pedido = 'EPD005' WHERE num = 29;
UPDATE PEDIDO SET entrega = 6, edo_pedido = 'EPD005' WHERE num = 30;
UPDATE PEDIDO SET entrega = 7, edo_pedido = 'EPD005' WHERE num = 31;
UPDATE PEDIDO SET entrega = 7, edo_pedido = 'EPD005' WHERE num = 32;
UPDATE PEDIDO SET entrega = 7, edo_pedido = 'EPD005' WHERE num = 33;
UPDATE PEDIDO SET entrega = 7, edo_pedido = 'EPD005' WHERE num = 34;
UPDATE PEDIDO SET entrega = 7, edo_pedido = 'EPD005' WHERE num = 35;
UPDATE PEDIDO SET entrega = 8, edo_pedido = 'EPD005' WHERE num = 36;
UPDATE PEDIDO SET entrega = 8, edo_pedido = 'EPD005' WHERE num = 37;
UPDATE PEDIDO SET entrega = 8, edo_pedido = 'EPD005' WHERE num = 38;
UPDATE PEDIDO SET entrega = 8, edo_pedido = 'EPD005' WHERE num = 39;
UPDATE PEDIDO SET entrega = 8, edo_pedido = 'EPD005' WHERE num = 40;
UPDATE PEDIDO SET entrega = 9, edo_pedido = 'EPD005' WHERE num = 41;
UPDATE PEDIDO SET entrega = 9, edo_pedido = 'EPD005' WHERE num = 42;
UPDATE PEDIDO SET entrega = 9, edo_pedido = 'EPD005' WHERE num = 43;
UPDATE PEDIDO SET entrega = 9, edo_pedido = 'EPD005' WHERE num = 44;
UPDATE PEDIDO SET entrega = 9, edo_pedido = 'EPD005' WHERE num = 45;
UPDATE PEDIDO SET entrega = 10, edo_pedido = 'EPD005' WHERE num = 46;
UPDATE PEDIDO SET entrega = 10, edo_pedido = 'EPD005' WHERE num = 47;
UPDATE PEDIDO SET entrega = 10, edo_pedido = 'EPD005' WHERE num = 48;
UPDATE PEDIDO SET entrega = 10, edo_pedido = 'EPD005' WHERE num = 49;
UPDATE PEDIDO SET entrega = 10, edo_pedido = 'EPD005' WHERE num = 50;

UPDATE ESTABLECIMIENTO SET entrega = 1 WHERE numero = 1;
UPDATE ESTABLECIMIENTO SET entrega = 1 WHERE numero = 2;
UPDATE ESTABLECIMIENTO SET entrega = 1 WHERE numero = 3;
UPDATE ESTABLECIMIENTO SET entrega = 1 WHERE numero = 4;
UPDATE ESTABLECIMIENTO SET entrega = 1 WHERE numero = 5;
UPDATE ESTABLECIMIENTO SET entrega = 2 WHERE numero = 6;
UPDATE ESTABLECIMIENTO SET entrega = 2 WHERE numero = 7;
UPDATE ESTABLECIMIENTO SET entrega = 2 WHERE numero = 8;
UPDATE ESTABLECIMIENTO SET entrega = 2 WHERE numero = 9;
UPDATE ESTABLECIMIENTO SET entrega = 2 WHERE numero = 10;
UPDATE ESTABLECIMIENTO SET entrega = 3 WHERE numero = 11;
UPDATE ESTABLECIMIENTO SET entrega = 3 WHERE numero = 12;
UPDATE ESTABLECIMIENTO SET entrega = 3 WHERE numero = 13;
UPDATE ESTABLECIMIENTO SET entrega = 3 WHERE numero = 14;
UPDATE ESTABLECIMIENTO SET entrega = 3 WHERE numero = 15;
UPDATE ESTABLECIMIENTO SET entrega = 4 WHERE numero = 16;
UPDATE ESTABLECIMIENTO SET entrega = 4 WHERE numero = 17;
UPDATE ESTABLECIMIENTO SET entrega = 4 WHERE numero = 18;
UPDATE ESTABLECIMIENTO SET entrega = 4 WHERE numero = 19;
UPDATE ESTABLECIMIENTO SET entrega = 4 WHERE numero = 20;
UPDATE ESTABLECIMIENTO SET entrega = 5 WHERE numero = 21;
UPDATE ESTABLECIMIENTO SET entrega = 5 WHERE numero = 22;
UPDATE ESTABLECIMIENTO SET entrega = 5 WHERE numero = 23;
UPDATE ESTABLECIMIENTO SET entrega = 5 WHERE numero = 24;
UPDATE ESTABLECIMIENTO SET entrega = 5 WHERE numero = 25;
UPDATE ESTABLECIMIENTO SET entrega = 6 WHERE numero = 26;
UPDATE ESTABLECIMIENTO SET entrega = 6 WHERE numero = 27;
UPDATE ESTABLECIMIENTO SET entrega = 6 WHERE numero = 28;
UPDATE ESTABLECIMIENTO SET entrega = 6 WHERE numero = 29;
UPDATE ESTABLECIMIENTO SET entrega = 6 WHERE numero = 30;
UPDATE ESTABLECIMIENTO SET entrega = 7 WHERE numero = 31;
UPDATE ESTABLECIMIENTO SET entrega = 7 WHERE numero = 32;
UPDATE ESTABLECIMIENTO SET entrega = 7 WHERE numero = 33;
UPDATE ESTABLECIMIENTO SET entrega = 7 WHERE numero = 34;
UPDATE ESTABLECIMIENTO SET entrega = 7 WHERE numero = 35;
UPDATE ESTABLECIMIENTO SET entrega = 8 WHERE numero = 36;
UPDATE ESTABLECIMIENTO SET entrega = 8 WHERE numero = 37;
UPDATE ESTABLECIMIENTO SET entrega = 8 WHERE numero = 38;
UPDATE ESTABLECIMIENTO SET entrega = 8 WHERE numero = 39;
UPDATE ESTABLECIMIENTO SET entrega = 8 WHERE numero = 40;
UPDATE ESTABLECIMIENTO SET entrega = 9 WHERE numero = 41;
UPDATE ESTABLECIMIENTO SET entrega = 9 WHERE numero = 42;
UPDATE ESTABLECIMIENTO SET entrega = 9 WHERE numero = 43;
UPDATE ESTABLECIMIENTO SET entrega = 9 WHERE numero = 44;
UPDATE ESTABLECIMIENTO SET entrega = 9 WHERE numero = 45;
UPDATE ESTABLECIMIENTO SET entrega = 10 WHERE numero = 46;
UPDATE ESTABLECIMIENTO SET entrega = 10 WHERE numero = 47;
UPDATE ESTABLECIMIENTO SET entrega = 10 WHERE numero = 48;
UPDATE ESTABLECIMIENTO SET entrega = 10 WHERE numero = 49;
UPDATE ESTABLECIMIENTO SET entrega = 10 WHERE numero = 50;

-- ==========================================
-- ENTREGA_ESTABLE DE AYER
-- ==========================================

INSERT INTO ENTREGA_ESTABLE (entrega, establecimiento, fecha_entrega, hora_entrega) VALUES
(1, 1, '2026-07-21', '10:30:00'),
(1, 2, '2026-07-21', '11:30:00'),
(1, 3, '2026-07-21', '12:30:00'),
(1, 4, '2026-07-21', '13:30:00'),
(1, 5, '2026-07-21', '14:30:00'),
(2, 6, '2026-07-21', '10:30:00'),
(2, 7, '2026-07-21', '11:30:00'),
(2, 8, '2026-07-21', '12:30:00'),
(2, 9, '2026-07-21', '13:30:00'),
(2, 10, '2026-07-21', '14:30:00'),
(3, 11, '2026-07-21', '10:30:00'),
(3, 12, '2026-07-21', '11:30:00'),
(3, 13, '2026-07-21', '12:30:00'),
(3, 14, '2026-07-21', '13:30:00'),
(3, 15, '2026-07-21', '14:30:00'),
(4, 16, '2026-07-21', '10:30:00'),
(4, 17, '2026-07-21', '11:30:00'),
(4, 18, '2026-07-21', '12:30:00'),
(4, 19, '2026-07-21', '13:30:00'),
(4, 20, '2026-07-21', '14:30:00'),
(5, 21, '2026-07-21', '10:30:00'),
(5, 22, '2026-07-21', '11:30:00'),
(5, 23, '2026-07-21', '12:30:00'),
(5, 24, '2026-07-21', '13:30:00'),
(5, 25, '2026-07-21', '14:30:00'),
(6, 26, '2026-07-21', '10:30:00'),
(6, 27, '2026-07-21', '11:30:00'),
(6, 28, '2026-07-21', '12:30:00'),
(6, 29, '2026-07-21', '13:30:00'),
(6, 30, '2026-07-21', '14:30:00'),
(7, 31, '2026-07-21', '10:30:00'),
(7, 32, '2026-07-21', '11:30:00'),
(7, 33, '2026-07-21', '12:30:00'),
(7, 34, '2026-07-21', '13:30:00'),
(7, 35, '2026-07-21', '14:30:00'),
(8, 36, '2026-07-21', '10:30:00'),
(8, 37, '2026-07-21', '11:30:00'),
(8, 38, '2026-07-21', '12:30:00'),
(8, 39, '2026-07-21', '13:30:00'),
(8, 40, '2026-07-21', '14:30:00'),
(9, 41, '2026-07-21', '10:30:00'),
(9, 42, '2026-07-21', '11:30:00'),
(9, 43, '2026-07-21', '12:30:00'),
(9, 44, '2026-07-21', '13:30:00'),
(9, 45, '2026-07-21', '14:30:00'),
(10, 46, '2026-07-21', '10:30:00'),
(10, 47, '2026-07-21', '11:30:00'),
(10, 48, '2026-07-21', '12:30:00'),
(10, 49, '2026-07-21', '13:30:00'),
(10, 50, '2026-07-21', '14:30:00');

-- ==========================================
-- RUTAS DE ENTREGA DE AYER
-- ==========================================

INSERT INTO RUTA_ENTREGA (numero, nombre, descripcion, empleado, entrega, edo_ruta_entrega) VALUES
(1, 'Ruta Entrega Noroeste', 'Recorrido de entrega de pedidos surtidos en Zona Noroeste', 44, 1, 'ERET003'),
(2, 'Ruta Entrega Norte 1', 'Recorrido de entrega de pedidos surtidos en Zona Norte 1', 45, 2, 'ERET003'),
(3, 'Ruta Entrega Norte 2', 'Recorrido de entrega de pedidos surtidos en Zona Norte 2', 46, 3, 'ERET003'),
(4, 'Ruta Entrega Poniente', 'Recorrido de entrega de pedidos surtidos en Zona Poniente', 47, 4, 'ERET003'),
(5, 'Ruta Entrega Centro', 'Recorrido de entrega de pedidos surtidos en Zona Centro', 48, 5, 'ERET003'),
(6, 'Ruta Entrega Oriente 1', 'Recorrido de entrega de pedidos surtidos en Zona Oriente 1', 49, 6, 'ERET003'),
(7, 'Ruta Entrega Oriente 2', 'Recorrido de entrega de pedidos surtidos en Zona Oriente 2', 50, 7, 'ERET003'),
(8, 'Ruta Entrega Sureste 1', 'Recorrido de entrega de pedidos surtidos en Zona Sureste 1', 51, 8, 'ERET003'),
(9, 'Ruta Entrega Sureste 2', 'Recorrido de entrega de pedidos surtidos en Zona Sureste 2', 52, 9, 'ERET003'),
(10, 'Ruta Entrega Sur', 'Recorrido de entrega de pedidos surtidos en Zona Sur', 53, 10, 'ERET003');

-- ==========================================
-- PAGOS DE AYER
-- ==========================================

INSERT INTO PAGO (codigo, monto, fecha, tipo_pago, empleado, establecimiento, pedido) VALUES
(1, 1696.22, '2026-07-21 10:45:00', 'TP002', 44, 1, 1),
(2, 1503.35, '2026-07-21 11:45:00', 'TP001', 44, 2, 2),
(3, 1596.1, '2026-07-21 12:45:00', 'TP001', 44, 3, 3),
(4, 1516.12, '2026-07-21 13:45:00', 'TP002', 44, 4, 4),
(5, 700.21, '2026-07-21 14:45:00', 'TP001', 44, 5, 5),
(6, 1481.06, '2026-07-21 10:45:00', 'TP001', 45, 6, 6),
(7, 462.14, '2026-07-21 11:45:00', 'TP002', 45, 7, 7),
(8, 1608.25, '2026-07-21 12:45:00', 'TP001', 45, 8, 8),
(9, 1587.89, '2026-07-21 13:45:00', 'TP001', 45, 9, 9),
(10, 633.65, '2026-07-21 14:45:00', 'TP002', 45, 10, 10),
(11, 1524.88, '2026-07-21 10:45:00', 'TP001', 46, 11, 11),
(12, 990.45, '2026-07-21 11:45:00', 'TP001', 46, 12, 12),
(13, 757.79, '2026-07-21 12:45:00', 'TP002', 46, 13, 13),
(14, 1493.02, '2026-07-21 13:45:00', 'TP001', 46, 14, 14),
(15, 641.39, '2026-07-21 14:45:00', 'TP001', 46, 15, 15),
(16, 335.5, '2026-07-21 10:45:00', 'TP002', 47, 16, 16),
(17, 589.69, '2026-07-21 11:45:00', 'TP001', 47, 17, 17),
(18, 792.39, '2026-07-21 12:45:00', 'TP001', 47, 18, 18),
(19, 1596.53, '2026-07-21 13:45:00', 'TP002', 47, 19, 19),
(20, 1750.33, '2026-07-21 14:45:00', 'TP001', 47, 20, 20),
(21, 718.69, '2026-07-21 10:45:00', 'TP001', 48, 21, 21),
(22, 1262.22, '2026-07-21 11:45:00', 'TP002', 48, 22, 22),
(23, 899.52, '2026-07-21 12:45:00', 'TP001', 48, 23, 23),
(24, 1771.72, '2026-07-21 13:45:00', 'TP001', 48, 24, 24),
(25, 1104.32, '2026-07-21 14:45:00', 'TP002', 48, 25, 25),
(26, 1708.86, '2026-07-21 10:45:00', 'TP001', 49, 26, 26),
(27, 473.01, '2026-07-21 11:45:00', 'TP001', 49, 27, 27),
(28, 1755.6, '2026-07-21 12:45:00', 'TP002', 49, 28, 28),
(29, 567.85, '2026-07-21 13:45:00', 'TP001', 49, 29, 29),
(30, 1743.8, '2026-07-21 14:45:00', 'TP001', 49, 30, 30),
(31, 698.2, '2026-07-21 10:45:00', 'TP002', 50, 31, 31),
(32, 462.6, '2026-07-21 11:45:00', 'TP001', 50, 32, 32),
(33, 951.85, '2026-07-21 12:45:00', 'TP001', 50, 33, 33),
(34, 1392.82, '2026-07-21 13:45:00', 'TP002', 50, 34, 34),
(35, 770.52, '2026-07-21 14:45:00', 'TP001', 50, 35, 35),
(36, 1209.31, '2026-07-21 10:45:00', 'TP001', 51, 36, 36),
(37, 1067.13, '2026-07-21 11:45:00', 'TP002', 51, 37, 37),
(38, 877.79, '2026-07-21 12:45:00', 'TP001', 51, 38, 38),
(39, 1164.88, '2026-07-21 13:45:00', 'TP001', 51, 39, 39),
(40, 682.08, '2026-07-21 14:45:00', 'TP002', 51, 40, 40),
(41, 1363.18, '2026-07-21 10:45:00', 'TP001', 52, 41, 41),
(42, 302.54, '2026-07-21 11:45:00', 'TP001', 52, 42, 42),
(43, 1688.36, '2026-07-21 12:45:00', 'TP002', 52, 43, 43),
(44, 1107.68, '2026-07-21 13:45:00', 'TP001', 52, 44, 44),
(45, 1379.14, '2026-07-21 14:45:00', 'TP001', 52, 45, 45),
(46, 1412.93, '2026-07-21 10:45:00', 'TP002', 53, 46, 46),
(47, 1305.94, '2026-07-21 11:45:00', 'TP001', 53, 47, 47),
(48, 846.33, '2026-07-21 12:45:00', 'TP001', 53, 48, 48),
(49, 404.96, '2026-07-21 13:45:00', 'TP002', 53, 49, 49),
(50, 1296.36, '2026-07-21 14:45:00', 'TP001', 53, 50, 50);

-- ==========================================
-- DEVOLUCIONES DE AYER
-- ==========================================

INSERT INTO DEVOLUCION (codigo, fecha, cantidad, motivo, descripcion, entrega) VALUES
(1, '2026-07-21', 3, 'Producto dañado con sustitución', 'El empaque llegó dañado durante el transporte', 1),
(2, '2026-07-21', 5, 'Devolución completa sin reemplazo', 'El cliente rechazó el pedido por diferencia en el pedido original', 2),
(3, '2026-07-21', 3, 'Producto dañado con sustitución', 'El empaque llegó dañado durante el transporte', 3),
(4, '2026-07-21', 6, 'Devolución completa sin reemplazo', 'El cliente rechazó el pedido por diferencia en el pedido original', 4),
(5, '2026-07-21', 1, 'Producto dañado con sustitución', 'El empaque llegó dañado durante el transporte', 5);

-- ==========================================
-- MOVIMIENTOS DE INVENTARIO
-- ==========================================

INSERT INTO MOVIMIENTOS (codigo, observaciones, fecha, tipo_movimiento, devolucion, empleado) VALUES
(1, 'Entrada por reabastecimiento semanal', '2026-07-21 07:00:00', 'TM001', NULL, 24),
(2, 'Entrada por reabastecimiento semanal', '2026-07-21 07:00:00', 'TM001', NULL, 25),
(3, 'Entrada por reabastecimiento semanal', '2026-07-21 07:00:00', 'TM001', NULL, 26),
(4, 'Entrada por reabastecimiento semanal', '2026-07-21 07:00:00', 'TM001', NULL, 27),
(5, 'Entrada por reabastecimiento semanal', '2026-07-21 07:00:00', 'TM001', NULL, 28),
(6, 'Salida por surtido de pedidos zona 1', '2026-07-21 12:00:00', 'TM002', NULL, 24),
(7, 'Salida por surtido de pedidos zona 2', '2026-07-21 12:00:00', 'TM002', NULL, 25),
(8, 'Salida por surtido de pedidos zona 3', '2026-07-21 12:00:00', 'TM002', NULL, 26),
(9, 'Salida por surtido de pedidos zona 4', '2026-07-21 12:00:00', 'TM002', NULL, 27),
(10, 'Salida por surtido de pedidos zona 5', '2026-07-21 12:00:00', 'TM002', NULL, 28),
(11, 'Salida por surtido de pedidos zona 6', '2026-07-21 12:00:00', 'TM002', NULL, 29),
(12, 'Salida por surtido de pedidos zona 7', '2026-07-21 12:00:00', 'TM002', NULL, 30),
(13, 'Salida por surtido de pedidos zona 8', '2026-07-21 12:00:00', 'TM002', NULL, 31),
(14, 'Salida por surtido de pedidos zona 9', '2026-07-21 12:00:00', 'TM002', NULL, 32),
(15, 'Salida por surtido de pedidos zona 10', '2026-07-21 12:00:00', 'TM002', NULL, 33),
(16, 'Entrada por devolución de entrega 1', '2026-07-21 18:00:00', 'TM004', 1, 24),
(17, 'Entrada por devolución de entrega 2', '2026-07-21 18:00:00', 'TM004', 2, 25),
(18, 'Entrada por devolución de entrega 3', '2026-07-21 18:00:00', 'TM004', 3, 26),
(19, 'Entrada por devolución de entrega 4', '2026-07-21 18:00:00', 'TM004', 4, 27),
(20, 'Entrada por devolución de entrega 5', '2026-07-21 18:00:00', 'TM004', 5, 28),
(21, 'Entrada por reabastecimiento matutino', '2026-07-22 07:00:00', 'TM001', NULL, 24),
(22, 'Entrada por reabastecimiento matutino', '2026-07-22 07:00:00', 'TM001', NULL, 25),
(23, 'Entrada por reabastecimiento matutino', '2026-07-22 07:00:00', 'TM001', NULL, 26);

INSERT INTO DETALLE_MOVIMIENTO (cod_movimientos, cod_producto, cantidad, precioUnitario, subtotal) VALUES
(1, 'P010', 409, 14, 5726),
(1, 'P009', 367, 14, 5138),
(1, 'P005', 406, 15.5, 6293.0),
(2, 'P010', 298, 14, 4172),
(2, 'P009', 415, 14, 5810),
(2, 'P003', 394, 17, 6698),
(3, 'P006', 354, 17.5, 6195.0),
(3, 'P010', 407, 14, 5698),
(3, 'P015', 480, 13.5, 6480.0),
(4, 'P001', 307, 13.5, 4144.5),
(4, 'P005', 420, 15.5, 6510.0),
(4, 'P015', 496, 13.5, 6696.0),
(5, 'P011', 426, 13, 5538),
(5, 'P008', 309, 15.5, 4789.5),
(5, 'P015', 461, 13.5, 6223.5),
(6, 'P016', 144, 12.5, 1800.0),
(6, 'P013', 71, 16, 1136),
(6, 'P015', 134, 13.5, 1809.0),
(7, 'P003', 134, 17, 2278),
(7, 'P005', 131, 15.5, 2030.5),
(7, 'P009', 129, 14, 1806),
(8, 'P011', 146, 13, 1898),
(8, 'P002', 80, 13.5, 1080.0),
(8, 'P014', 136, 16, 2176),
(9, 'P010', 75, 14, 1050),
(9, 'P004', 68, 17, 1156),
(9, 'P013', 53, 16, 848),
(10, 'P002', 128, 13.5, 1728.0),
(10, 'P004', 148, 17, 2516),
(10, 'P008', 59, 15.5, 914.5),
(11, 'P015', 123, 13.5, 1660.5),
(11, 'P007', 74, 14.5, 1073.0),
(11, 'P011', 141, 13, 1833),
(12, 'P013', 81, 16, 1296),
(12, 'P008', 68, 15.5, 1054.0),
(12, 'P007', 133, 14.5, 1928.5),
(13, 'P001', 148, 13.5, 1998.0),
(13, 'P015', 63, 13.5, 850.5),
(13, 'P013', 149, 16, 2384),
(14, 'P014', 139, 16, 2224),
(14, 'P004', 116, 17, 1972),
(14, 'P003', 109, 17, 1853),
(15, 'P002', 65, 13.5, 877.5),
(15, 'P009', 108, 14, 1512),
(15, 'P004', 67, 17, 1139),
(16, 'P015', 6, 13.5, 81.0),
(17, 'P011', 4, 13, 52),
(18, 'P014', 5, 16, 80),
(19, 'P015', 2, 13.5, 27.0),
(20, 'P016', 4, 12.5, 50.0),
(21, 'P009', 341, 14, 4774),
(21, 'P013', 466, 16, 7456),
(21, 'P004', 448, 17, 7616),
(21, 'P011', 322, 13, 4186),
(22, 'P009', 346, 14, 4844),
(22, 'P008', 320, 15.5, 4960.0),
(22, 'P002', 339, 13.5, 4576.5),
(22, 'P012', 371, 13.5, 5008.5),
(23, 'P011', 270, 13, 3510),
(23, 'P015', 277, 13.5, 3739.5),
(23, 'P009', 318, 14, 4452),
(23, 'P002', 396, 13.5, 5346.0);

-- ==========================================
-- ENTREGAS DE HOY (en proceso y cargadas)
-- ==========================================

INSERT INTO ENTREGA (numero, fecha_creacion, fecha_entrega, empleado, edo_entrega) VALUES
(11, '2026-07-22', '2026-07-22 18:00:00', 54, 'EEN004'),
(12, '2026-07-22', '2026-07-22 18:00:00', 55, 'EEN004'),
(13, '2026-07-22', NULL, 56, 'EEN003'),
(14, '2026-07-22', NULL, 57, 'EEN002'),
(15, '2026-07-22', NULL, 58, 'EEN002');

-- Asignar entregas a pedidos de hoy zonas 1-2 (completadas)
UPDATE PEDIDO SET entrega = 11, edo_pedido = 'EPD005' WHERE num = 51;
UPDATE PEDIDO SET entrega = 11, edo_pedido = 'EPD005' WHERE num = 52;
UPDATE PEDIDO SET entrega = 11, edo_pedido = 'EPD005' WHERE num = 53;
UPDATE PEDIDO SET entrega = 11, edo_pedido = 'EPD005' WHERE num = 54;
UPDATE PEDIDO SET entrega = 11, edo_pedido = 'EPD005' WHERE num = 55;
UPDATE PEDIDO SET entrega = 12, edo_pedido = 'EPD005' WHERE num = 56;
UPDATE PEDIDO SET entrega = 12, edo_pedido = 'EPD005' WHERE num = 57;
UPDATE PEDIDO SET entrega = 12, edo_pedido = 'EPD005' WHERE num = 58;
UPDATE PEDIDO SET entrega = 12, edo_pedido = 'EPD005' WHERE num = 59;
UPDATE PEDIDO SET entrega = 12, edo_pedido = 'EPD005' WHERE num = 60;
-- Asignar entregas a pedidos de hoy zonas 3-5 (en camino/cargada)
UPDATE PEDIDO SET entrega = 13, edo_pedido = 'EPD004' WHERE num = 61;
UPDATE PEDIDO SET entrega = 13, edo_pedido = 'EPD004' WHERE num = 62;
UPDATE PEDIDO SET entrega = 13, edo_pedido = 'EPD004' WHERE num = 63;
UPDATE PEDIDO SET entrega = 13, edo_pedido = 'EPD004' WHERE num = 64;
UPDATE PEDIDO SET entrega = 13, edo_pedido = 'EPD004' WHERE num = 65;
UPDATE PEDIDO SET entrega = 14, edo_pedido = 'EPD004' WHERE num = 66;
UPDATE PEDIDO SET entrega = 14, edo_pedido = 'EPD004' WHERE num = 67;
UPDATE PEDIDO SET entrega = 14, edo_pedido = 'EPD004' WHERE num = 68;
UPDATE PEDIDO SET entrega = 14, edo_pedido = 'EPD004' WHERE num = 69;
UPDATE PEDIDO SET entrega = 14, edo_pedido = 'EPD004' WHERE num = 70;
UPDATE PEDIDO SET entrega = 15, edo_pedido = 'EPD004' WHERE num = 71;
UPDATE PEDIDO SET entrega = 15, edo_pedido = 'EPD004' WHERE num = 72;
UPDATE PEDIDO SET entrega = 15, edo_pedido = 'EPD004' WHERE num = 73;
UPDATE PEDIDO SET entrega = 15, edo_pedido = 'EPD004' WHERE num = 74;
UPDATE PEDIDO SET entrega = 15, edo_pedido = 'EPD004' WHERE num = 75;

INSERT INTO ENTREGA_ESTABLE (entrega, establecimiento, fecha_entrega, hora_entrega) VALUES
(11, 1, '2026-07-22', '10:30:00'),
(11, 2, '2026-07-22', '11:30:00'),
(11, 3, '2026-07-22', '12:30:00'),
(11, 4, '2026-07-22', '13:30:00'),
(11, 5, '2026-07-22', '14:30:00'),
(12, 6, '2026-07-22', '10:30:00'),
(12, 7, '2026-07-22', '11:30:00'),
(12, 8, '2026-07-22', '12:30:00'),
(12, 9, '2026-07-22', '13:30:00'),
(12, 10, '2026-07-22', '14:30:00');

INSERT INTO RUTA_ENTREGA (numero, nombre, descripcion, empleado, entrega, edo_ruta_entrega) VALUES
(11, 'Ruta Entrega Hoy Noroeste', 'Recorrido de entrega del día de hoy en Zona Noroeste', 54, 11, 'ERET003'),
(12, 'Ruta Entrega Hoy Norte 1', 'Recorrido de entrega del día de hoy en Zona Norte 1', 55, 12, 'ERET003'),
(13, 'Ruta Entrega Hoy Norte 2', 'Recorrido de entrega del día de hoy en Zona Norte 2', 56, 13, 'ERET002'),
(14, 'Ruta Entrega Hoy Poniente', 'Recorrido de entrega del día de hoy en Zona Poniente', 57, 14, 'ERET002'),
(15, 'Ruta Entrega Hoy Centro', 'Recorrido de entrega del día de hoy en Zona Centro', 58, 15, 'ERET001');

INSERT INTO PAGO (codigo, monto, fecha, tipo_pago, empleado, establecimiento, pedido) VALUES
(51, 1340.92, '2026-07-22 10:45:00', 'TP002', 54, 1, 51),
(52, 1359.63, '2026-07-22 11:45:00', 'TP001', 54, 2, 52),
(53, 396.34, '2026-07-22 12:45:00', 'TP001', 54, 3, 53),
(54, 911.4, '2026-07-22 13:45:00', 'TP002', 54, 4, 54),
(55, 1113.92, '2026-07-22 14:45:00', 'TP001', 54, 5, 55),
(56, 923.66, '2026-07-22 10:45:00', 'TP001', 55, 6, 56),
(57, 610.25, '2026-07-22 11:45:00', 'TP002', 55, 7, 57),
(58, 930.22, '2026-07-22 12:45:00', 'TP001', 55, 8, 58),
(59, 1657.26, '2026-07-22 13:45:00', 'TP001', 55, 9, 59),
(60, 1176.12, '2026-07-22 14:45:00', 'TP002', 55, 10, 60);

---- primero de hoy
INSERT INTO EMP_VEHICULO (empleado, vehiculo, fecha_cargo) VALUES
(24, 21, '2026-07-21'),
(25, 22, '2026-07-21'),
(26, 23, '2026-07-21'),
(27, 24, '2026-07-21'),
(28, 25, '2026-07-21'),
(29, 26, '2026-07-21'),
(30, 27, '2026-07-21'),
(31, 28, '2026-07-21'),
(32, 29, '2026-07-21'),
(33, 30, '2026-07-21');

--ahora de ayer
INSERT INTO EMP_VEHICULO (empleado, vehiculo, fecha_cargo) VALUES
(24, 21, '2026-07-20'),
(25, 22, '2026-07-20'),
(26, 23, '2026-07-20'),
(27, 24, '2026-07-20'),
(28, 25, '2026-07-20'),
(29, 26, '2026-07-20'),
(30, 27, '2026-07-20'),
(31, 28, '2026-07-20'),
(32, 29, '2026-07-20'),
(33, 30, '2026-07-20');