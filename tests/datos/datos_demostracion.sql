SET NOCOUNT ON
SET DATEFORMAT ymd
GO

DISABLE TRIGGER ALL ON [dbo].[TblEmpleados];
DISABLE TRIGGER ALL ON [dbo].[TblUsuarios];
DISABLE TRIGGER ALL ON [dbo].[TblMesas];
DISABLE TRIGGER ALL ON [dbo].[TblProductos];
DISABLE TRIGGER ALL ON [dbo].[TblTickets];
DISABLE TRIGGER ALL ON [dbo].[TblDetalleTicket];
DISABLE TRIGGER ALL ON [dbo].[TblPagos];
DISABLE TRIGGER ALL ON [dbo].[TblHistorialProductos];
DISABLE TRIGGER ALL ON [dbo].[TblHistorialReservaciones];
DISABLE TRIGGER ALL ON [dbo].[TblHistorialDetalleTicket];
DISABLE TRIGGER ALL ON [dbo].[TblClientes];
DISABLE TRIGGER ALL ON [dbo].[TblReservaciones];
DISABLE TRIGGER ALL ON [dbo].[TblProduccion];
GO

DELETE FROM [dbo].[TblEmpleados] WHERE [esSistema] = 1 AND NOT EXISTS (SELECT 1 FROM [dbo].[TblUsuarios]);
GO

SET IDENTITY_INSERT [dbo].[TblEmpleados] ON
INSERT [dbo].[TblEmpleados] ([idEmpleado], [nombre], [puesto], [telefono], [fechaContratacion], [activo], [esSistema]) VALUES (1, N'Administrador General', N'Administrador', N'82322312', '2026-01-01', 1, 0)
INSERT [dbo].[TblEmpleados] ([idEmpleado], [nombre], [puesto], [telefono], [fechaContratacion], [activo], [esSistema]) VALUES (8, N'Sistema', N'Sistema', NULL, '2026-06-12', 1, 1)
INSERT [dbo].[TblEmpleados] ([idEmpleado], [nombre], [puesto], [telefono], [fechaContratacion], [activo], [esSistema]) VALUES (9, N'Cajero General', N'Cajero', N'82733212', '2026-06-12', 1, 0)
INSERT [dbo].[TblEmpleados] ([idEmpleado], [nombre], [puesto], [telefono], [fechaContratacion], [activo], [esSistema]) VALUES (10, N'Cocinero General', N'Cocinero', N'84223244', '2026-06-12', 1, 0)
INSERT [dbo].[TblEmpleados] ([idEmpleado], [nombre], [puesto], [telefono], [fechaContratacion], [activo], [esSistema]) VALUES (11, N'Mostrador General', N'Mostrador', N'83744323', '2026-06-12', 1, 0)
SET IDENTITY_INSERT [dbo].[TblEmpleados] OFF
GO

SET IDENTITY_INSERT [dbo].[TblUsuarios] ON
INSERT [dbo].[TblUsuarios] ([idUsuario], [correo], [passwordHash], [idRol], [idEmpleado], [activo], [debeCambiarPassword]) VALUES (1, N'admin@alma.com', N'!sin-acceso', 1, 1, 1, 0)
INSERT [dbo].[TblUsuarios] ([idUsuario], [correo], [passwordHash], [idRol], [idEmpleado], [activo], [debeCambiarPassword]) VALUES (6, N'luz@alma.com', N'!sin-acceso', 3, 9, 1, 0)
INSERT [dbo].[TblUsuarios] ([idUsuario], [correo], [passwordHash], [idRol], [idEmpleado], [activo], [debeCambiarPassword]) VALUES (7, N'sofi@alma.com', N'!sin-acceso', 4, 10, 1, 0)
INSERT [dbo].[TblUsuarios] ([idUsuario], [correo], [passwordHash], [idRol], [idEmpleado], [activo], [debeCambiarPassword]) VALUES (8, N'cris@alma.com', N'!sin-acceso', 2, 11, 1, 0)
SET IDENTITY_INSERT [dbo].[TblUsuarios] OFF
GO

SET IDENTITY_INSERT [dbo].[TblMesas] ON
INSERT [dbo].[TblMesas] ([idMesa], [numeroMesa], [capacidad], [activo]) VALUES (1, 1, 4, 1)
INSERT [dbo].[TblMesas] ([idMesa], [numeroMesa], [capacidad], [activo]) VALUES (2, 2, 4, 1)
INSERT [dbo].[TblMesas] ([idMesa], [numeroMesa], [capacidad], [activo]) VALUES (3, 3, 2, 1)
INSERT [dbo].[TblMesas] ([idMesa], [numeroMesa], [capacidad], [activo]) VALUES (4, 4, 6, 1)
INSERT [dbo].[TblMesas] ([idMesa], [numeroMesa], [capacidad], [activo]) VALUES (5, 5, 8, 1)
INSERT [dbo].[TblMesas] ([idMesa], [numeroMesa], [capacidad], [activo]) VALUES (6, 6, 8, 1)
SET IDENTITY_INSERT [dbo].[TblMesas] OFF
GO

SET IDENTITY_INSERT [dbo].[TblProductos] ON
INSERT [dbo].[TblProductos] ([idProducto], [nombre], [precioUnidad], [unidadMedida], [stockUnidades], [activo]) VALUES (38, N'Filete de pescado', 3500.00, N'Porción', 29, 1)
INSERT [dbo].[TblProductos] ([idProducto], [nombre], [precioUnidad], [unidadMedida], [stockUnidades], [activo]) VALUES (39, N'Pollo a la plancha', 2800.00, N'Porción', 30, 1)
INSERT [dbo].[TblProductos] ([idProducto], [nombre], [precioUnidad], [unidadMedida], [stockUnidades], [activo]) VALUES (40, N'Carne en salsa', 3200.00, N'Porción', 30, 1)
INSERT [dbo].[TblProductos] ([idProducto], [nombre], [precioUnidad], [unidadMedida], [stockUnidades], [activo]) VALUES (41, N'Cerdo BBQ', 3300.00, N'Porción', 30, 1)
INSERT [dbo].[TblProductos] ([idProducto], [nombre], [precioUnidad], [unidadMedida], [stockUnidades], [activo]) VALUES (42, N'Arroz blanco', 1000.00, N'Porción', 28, 1)
INSERT [dbo].[TblProductos] ([idProducto], [nombre], [precioUnidad], [unidadMedida], [stockUnidades], [activo]) VALUES (43, N'Frijoles', 900.00, N'Porción', 30, 1)
INSERT [dbo].[TblProductos] ([idProducto], [nombre], [precioUnidad], [unidadMedida], [stockUnidades], [activo]) VALUES (44, N'Ensalada rusa', 1200.00, N'Porción', 30, 1)
INSERT [dbo].[TblProductos] ([idProducto], [nombre], [precioUnidad], [unidadMedida], [stockUnidades], [activo]) VALUES (45, N'Picadillo de papa', 1200.00, N'Porción', 29, 1)
INSERT [dbo].[TblProductos] ([idProducto], [nombre], [precioUnidad], [unidadMedida], [stockUnidades], [activo]) VALUES (46, N'Plátano maduro', 1000.00, N'Porción', 30, 1)
INSERT [dbo].[TblProductos] ([idProducto], [nombre], [precioUnidad], [unidadMedida], [stockUnidades], [activo]) VALUES (47, N'Pasta con salsa', 1300.00, N'Porción', 30, 1)
INSERT [dbo].[TblProductos] ([idProducto], [nombre], [precioUnidad], [unidadMedida], [stockUnidades], [activo]) VALUES (48, N'Fresco de cas', 0.00, N'Vaso', 29, 1)
INSERT [dbo].[TblProductos] ([idProducto], [nombre], [precioUnidad], [unidadMedida], [stockUnidades], [activo]) VALUES (49, N'Fresco de tamarindo', 0.00, N'Vaso', 30, 1)
INSERT [dbo].[TblProductos] ([idProducto], [nombre], [precioUnidad], [unidadMedida], [stockUnidades], [activo]) VALUES (50, N'Fresco de mora', 0.00, N'Vaso', 30, 1)
INSERT [dbo].[TblProductos] ([idProducto], [nombre], [precioUnidad], [unidadMedida], [stockUnidades], [activo]) VALUES (51, N'Fresco de maracuyá', 0.00, N'Vaso', 30, 1)
INSERT [dbo].[TblProductos] ([idProducto], [nombre], [precioUnidad], [unidadMedida], [stockUnidades], [activo]) VALUES (52, N'Fresco de frutas', 0.00, N'Vaso', 30, 1)
INSERT [dbo].[TblProductos] ([idProducto], [nombre], [precioUnidad], [unidadMedida], [stockUnidades], [activo]) VALUES (53, N'Coca-Cola 600 ml', 1500.00, N'Botella', 29, 1)
INSERT [dbo].[TblProductos] ([idProducto], [nombre], [precioUnidad], [unidadMedida], [stockUnidades], [activo]) VALUES (54, N'Coca-Cola Zero 600 ml', 1500.00, N'Botella', 30, 1)
INSERT [dbo].[TblProductos] ([idProducto], [nombre], [precioUnidad], [unidadMedida], [stockUnidades], [activo]) VALUES (55, N'Fanta naranja 600 ml', 1500.00, N'Botella', 30, 1)
INSERT [dbo].[TblProductos] ([idProducto], [nombre], [precioUnidad], [unidadMedida], [stockUnidades], [activo]) VALUES (56, N'Sprite 600 ml', 1500.00, N'Botella', 30, 1)
INSERT [dbo].[TblProductos] ([idProducto], [nombre], [precioUnidad], [unidadMedida], [stockUnidades], [activo]) VALUES (57, N'Té frío 500 ml', 1400.00, N'Botella', 30, 1)
SET IDENTITY_INSERT [dbo].[TblProductos] OFF
GO

SET IDENTITY_INSERT [dbo].[TblTickets] ON
INSERT [dbo].[TblTickets] ([idTicket], [idMesa], [idUsuario], [fecha], [horaInicio], [fechaHoraFin], [estado]) VALUES (15, 2, 1, '2026-06-12', '22:37:40', '2026-06-12T22:55:54.000', N'Pagado')
INSERT [dbo].[TblTickets] ([idTicket], [idMesa], [idUsuario], [fecha], [horaInicio], [fechaHoraFin], [estado]) VALUES (16, 2, 1, '2026-06-13', '08:47:40', '2026-06-13T08:49:16.000', N'Pagado')
SET IDENTITY_INSERT [dbo].[TblTickets] OFF
GO

SET IDENTITY_INSERT [dbo].[TblDetalleTicket] ON
INSERT [dbo].[TblDetalleTicket] ([idDetalle], [idTicket], [idProducto], [cantidadUnidades], [precioUnidad], [subtotal]) VALUES (54, 15, 42, 1, 1000.00, 1000.00)
INSERT [dbo].[TblDetalleTicket] ([idDetalle], [idTicket], [idProducto], [cantidadUnidades], [precioUnidad], [subtotal]) VALUES (55, 15, 48, 1, 0.00, 0.00)
INSERT [dbo].[TblDetalleTicket] ([idDetalle], [idTicket], [idProducto], [cantidadUnidades], [precioUnidad], [subtotal]) VALUES (56, 16, 38, 1, 3500.00, 3500.00)
INSERT [dbo].[TblDetalleTicket] ([idDetalle], [idTicket], [idProducto], [cantidadUnidades], [precioUnidad], [subtotal]) VALUES (57, 16, 42, 1, 1000.00, 1000.00)
INSERT [dbo].[TblDetalleTicket] ([idDetalle], [idTicket], [idProducto], [cantidadUnidades], [precioUnidad], [subtotal]) VALUES (58, 16, 45, 1, 1200.00, 1200.00)
INSERT [dbo].[TblDetalleTicket] ([idDetalle], [idTicket], [idProducto], [cantidadUnidades], [precioUnidad], [subtotal]) VALUES (59, 16, 53, 1, 1500.00, 1500.00)
SET IDENTITY_INSERT [dbo].[TblDetalleTicket] OFF
GO

SET IDENTITY_INSERT [dbo].[TblPagos] ON
INSERT [dbo].[TblPagos] ([idPago], [idTicket], [montoTotal], [metodoPago], [fecha], [hora], [referencia]) VALUES (12, 15, 1130.00, N'SINPE', '2026-06-12', '22:37:57', N'kakakaka')
INSERT [dbo].[TblPagos] ([idPago], [idTicket], [montoTotal], [metodoPago], [fecha], [hora], [referencia]) VALUES (13, 16, 8136.00, N'Tarjeta', '2026-06-13', '08:48:19', N'DATA-62F50C090A')
SET IDENTITY_INSERT [dbo].[TblPagos] OFF
GO

SET IDENTITY_INSERT [dbo].[TblHistorialProductos] ON
INSERT [dbo].[TblHistorialProductos] ([idHistorialProducto], [idProducto], [idEmpleado], [fechaCambio], [accion], [nombre], [precioUnidad], [unidadMedida], [stockUnidades]) VALUES (89, 38, 1, '2026-06-12T22:30:29.000', N'INSERT', N'Filete de pescado', 3500.00, N'Porción', 30)
INSERT [dbo].[TblHistorialProductos] ([idHistorialProducto], [idProducto], [idEmpleado], [fechaCambio], [accion], [nombre], [precioUnidad], [unidadMedida], [stockUnidades]) VALUES (90, 39, 1, '2026-06-12T22:30:29.000', N'INSERT', N'Pollo a la plancha', 2800.00, N'Porción', 30)
INSERT [dbo].[TblHistorialProductos] ([idHistorialProducto], [idProducto], [idEmpleado], [fechaCambio], [accion], [nombre], [precioUnidad], [unidadMedida], [stockUnidades]) VALUES (91, 40, 1, '2026-06-12T22:30:29.000', N'INSERT', N'Carne en salsa', 3200.00, N'Porción', 30)
INSERT [dbo].[TblHistorialProductos] ([idHistorialProducto], [idProducto], [idEmpleado], [fechaCambio], [accion], [nombre], [precioUnidad], [unidadMedida], [stockUnidades]) VALUES (92, 41, 1, '2026-06-12T22:30:29.000', N'INSERT', N'Cerdo BBQ', 3300.00, N'Porción', 30)
INSERT [dbo].[TblHistorialProductos] ([idHistorialProducto], [idProducto], [idEmpleado], [fechaCambio], [accion], [nombre], [precioUnidad], [unidadMedida], [stockUnidades]) VALUES (93, 42, 1, '2026-06-12T22:30:29.000', N'INSERT', N'Arroz blanco', 1000.00, N'Porción', 30)
INSERT [dbo].[TblHistorialProductos] ([idHistorialProducto], [idProducto], [idEmpleado], [fechaCambio], [accion], [nombre], [precioUnidad], [unidadMedida], [stockUnidades]) VALUES (94, 43, 1, '2026-06-12T22:30:29.000', N'INSERT', N'Frijoles', 900.00, N'Porción', 30)
INSERT [dbo].[TblHistorialProductos] ([idHistorialProducto], [idProducto], [idEmpleado], [fechaCambio], [accion], [nombre], [precioUnidad], [unidadMedida], [stockUnidades]) VALUES (95, 44, 1, '2026-06-12T22:30:29.000', N'INSERT', N'Ensalada rusa', 1200.00, N'Porción', 30)
INSERT [dbo].[TblHistorialProductos] ([idHistorialProducto], [idProducto], [idEmpleado], [fechaCambio], [accion], [nombre], [precioUnidad], [unidadMedida], [stockUnidades]) VALUES (96, 45, 1, '2026-06-12T22:30:29.000', N'INSERT', N'Picadillo de papa', 1200.00, N'Porción', 30)
INSERT [dbo].[TblHistorialProductos] ([idHistorialProducto], [idProducto], [idEmpleado], [fechaCambio], [accion], [nombre], [precioUnidad], [unidadMedida], [stockUnidades]) VALUES (97, 46, 1, '2026-06-12T22:30:29.000', N'INSERT', N'Plátano maduro', 1000.00, N'Porción', 30)
INSERT [dbo].[TblHistorialProductos] ([idHistorialProducto], [idProducto], [idEmpleado], [fechaCambio], [accion], [nombre], [precioUnidad], [unidadMedida], [stockUnidades]) VALUES (98, 47, 1, '2026-06-12T22:30:29.000', N'INSERT', N'Pasta con salsa', 1300.00, N'Porción', 30)
INSERT [dbo].[TblHistorialProductos] ([idHistorialProducto], [idProducto], [idEmpleado], [fechaCambio], [accion], [nombre], [precioUnidad], [unidadMedida], [stockUnidades]) VALUES (99, 48, 1, '2026-06-12T22:30:29.000', N'INSERT', N'Fresco de cas', 0.00, N'Vaso', 30)
INSERT [dbo].[TblHistorialProductos] ([idHistorialProducto], [idProducto], [idEmpleado], [fechaCambio], [accion], [nombre], [precioUnidad], [unidadMedida], [stockUnidades]) VALUES (100, 49, 1, '2026-06-12T22:30:29.000', N'INSERT', N'Fresco de tamarindo', 0.00, N'Vaso', 30)
INSERT [dbo].[TblHistorialProductos] ([idHistorialProducto], [idProducto], [idEmpleado], [fechaCambio], [accion], [nombre], [precioUnidad], [unidadMedida], [stockUnidades]) VALUES (101, 50, 1, '2026-06-12T22:30:29.000', N'INSERT', N'Fresco de mora', 0.00, N'Vaso', 30)
INSERT [dbo].[TblHistorialProductos] ([idHistorialProducto], [idProducto], [idEmpleado], [fechaCambio], [accion], [nombre], [precioUnidad], [unidadMedida], [stockUnidades]) VALUES (102, 51, 1, '2026-06-12T22:30:29.000', N'INSERT', N'Fresco de maracuyá', 0.00, N'Vaso', 30)
INSERT [dbo].[TblHistorialProductos] ([idHistorialProducto], [idProducto], [idEmpleado], [fechaCambio], [accion], [nombre], [precioUnidad], [unidadMedida], [stockUnidades]) VALUES (103, 52, 1, '2026-06-12T22:30:29.000', N'INSERT', N'Fresco de frutas', 0.00, N'Vaso', 30)
INSERT [dbo].[TblHistorialProductos] ([idHistorialProducto], [idProducto], [idEmpleado], [fechaCambio], [accion], [nombre], [precioUnidad], [unidadMedida], [stockUnidades]) VALUES (104, 53, 1, '2026-06-12T22:30:29.000', N'INSERT', N'Coca-Cola 600 ml', 1500.00, N'Botella', 30)
INSERT [dbo].[TblHistorialProductos] ([idHistorialProducto], [idProducto], [idEmpleado], [fechaCambio], [accion], [nombre], [precioUnidad], [unidadMedida], [stockUnidades]) VALUES (105, 54, 1, '2026-06-12T22:30:29.000', N'INSERT', N'Coca-Cola Zero 600 ml', 1500.00, N'Botella', 30)
INSERT [dbo].[TblHistorialProductos] ([idHistorialProducto], [idProducto], [idEmpleado], [fechaCambio], [accion], [nombre], [precioUnidad], [unidadMedida], [stockUnidades]) VALUES (106, 55, 1, '2026-06-12T22:30:29.000', N'INSERT', N'Fanta naranja 600 ml', 1500.00, N'Botella', 30)
INSERT [dbo].[TblHistorialProductos] ([idHistorialProducto], [idProducto], [idEmpleado], [fechaCambio], [accion], [nombre], [precioUnidad], [unidadMedida], [stockUnidades]) VALUES (107, 56, 1, '2026-06-12T22:30:29.000', N'INSERT', N'Sprite 600 ml', 1500.00, N'Botella', 30)
INSERT [dbo].[TblHistorialProductos] ([idHistorialProducto], [idProducto], [idEmpleado], [fechaCambio], [accion], [nombre], [precioUnidad], [unidadMedida], [stockUnidades]) VALUES (108, 57, 1, '2026-06-12T22:30:29.000', N'INSERT', N'Té frío 500 ml', 1400.00, N'Botella', 30)
INSERT [dbo].[TblHistorialProductos] ([idHistorialProducto], [idProducto], [idEmpleado], [fechaCambio], [accion], [nombre], [precioUnidad], [unidadMedida], [stockUnidades]) VALUES (109, 42, 1, '2026-06-12T22:37:41.000', N'UPDATE', N'Arroz blanco', 1000.00, N'Porción', 29)
INSERT [dbo].[TblHistorialProductos] ([idHistorialProducto], [idProducto], [idEmpleado], [fechaCambio], [accion], [nombre], [precioUnidad], [unidadMedida], [stockUnidades]) VALUES (110, 48, 1, '2026-06-12T22:37:41.000', N'UPDATE', N'Fresco de cas', 0.00, N'Vaso', 29)
INSERT [dbo].[TblHistorialProductos] ([idHistorialProducto], [idProducto], [idEmpleado], [fechaCambio], [accion], [nombre], [precioUnidad], [unidadMedida], [stockUnidades]) VALUES (113, 38, 1, '2026-06-13T08:47:40.000', N'UPDATE', N'Filete de pescado', 3500.00, N'Porción', 29)
INSERT [dbo].[TblHistorialProductos] ([idHistorialProducto], [idProducto], [idEmpleado], [fechaCambio], [accion], [nombre], [precioUnidad], [unidadMedida], [stockUnidades]) VALUES (114, 42, 1, '2026-06-13T08:47:40.000', N'UPDATE', N'Arroz blanco', 1000.00, N'Porción', 28)
INSERT [dbo].[TblHistorialProductos] ([idHistorialProducto], [idProducto], [idEmpleado], [fechaCambio], [accion], [nombre], [precioUnidad], [unidadMedida], [stockUnidades]) VALUES (115, 45, 1, '2026-06-13T08:47:40.000', N'UPDATE', N'Picadillo de papa', 1200.00, N'Porción', 29)
INSERT [dbo].[TblHistorialProductos] ([idHistorialProducto], [idProducto], [idEmpleado], [fechaCambio], [accion], [nombre], [precioUnidad], [unidadMedida], [stockUnidades]) VALUES (116, 53, 1, '2026-06-13T08:47:40.000', N'UPDATE', N'Coca-Cola 600 ml', 1500.00, N'Botella', 29)
SET IDENTITY_INSERT [dbo].[TblHistorialProductos] OFF
GO

SET IDENTITY_INSERT [dbo].[TblHistorialReservaciones] ON
INSERT [dbo].[TblHistorialReservaciones] ([idHistorialReservacion], [idReservacion], [idEmpleado], [idCliente], [idMesa], [fecha], [fechaCambio], [horaReserva], [accion], [cantidadPersonas], [estado]) VALUES (1, 1, 1, 3, 1, '2026-06-12', '2026-06-11T20:50:28.000', '20:50:00', N'INSERT', 4, N'Confirmada')
INSERT [dbo].[TblHistorialReservaciones] ([idHistorialReservacion], [idReservacion], [idEmpleado], [idCliente], [idMesa], [fecha], [fechaCambio], [horaReserva], [accion], [cantidadPersonas], [estado]) VALUES (2, 1, 1, 3, 1, '2026-06-12', '2026-06-11T20:50:50.000', '20:50:00', N'UPDATE', 4, N'Cancelada')
INSERT [dbo].[TblHistorialReservaciones] ([idHistorialReservacion], [idReservacion], [idEmpleado], [idCliente], [idMesa], [fecha], [fechaCambio], [horaReserva], [accion], [cantidadPersonas], [estado]) VALUES (3, 1, 1, 3, 1, '2026-06-12', '2026-06-12T13:08:54.000', '20:50:00', N'DELETE', 4, N'Cancelada')
INSERT [dbo].[TblHistorialReservaciones] ([idHistorialReservacion], [idReservacion], [idEmpleado], [idCliente], [idMesa], [fecha], [fechaCambio], [horaReserva], [accion], [cantidadPersonas], [estado]) VALUES (4, 2, 9, 4, 3, '2026-06-12', '2026-06-12T21:43:56.000', '21:43:00', N'INSERT', 2, N'Confirmada')
INSERT [dbo].[TblHistorialReservaciones] ([idHistorialReservacion], [idReservacion], [idEmpleado], [idCliente], [idMesa], [fecha], [fechaCambio], [horaReserva], [accion], [cantidadPersonas], [estado]) VALUES (5, 2, 9, 4, 3, '2026-06-12', '2026-06-12T21:44:25.000', '21:43:00', N'UPDATE', 2, N'Cancelada')
INSERT [dbo].[TblHistorialReservaciones] ([idHistorialReservacion], [idReservacion], [idEmpleado], [idCliente], [idMesa], [fecha], [fechaCambio], [horaReserva], [accion], [cantidadPersonas], [estado]) VALUES (6, 2, 9, 4, 3, '2026-06-12', '2026-06-12T21:44:31.000', '21:43:00', N'DELETE', 2, N'Cancelada')
SET IDENTITY_INSERT [dbo].[TblHistorialReservaciones] OFF
GO

SET IDENTITY_INSERT [dbo].[TblHistorialDetalleTicket] ON
INSERT [dbo].[TblHistorialDetalleTicket] ([idHistorialDetalle], [idDetalle], [idTicket], [idProducto], [idEmpleado], [fechaCambio], [accion], [cantidadUnidades], [precioUnidad], [subtotal]) VALUES (74, 54, 15, 42, 1, '2026-06-12T22:37:41.000', N'INSERT', 1, 1000.00, 1000.00)
INSERT [dbo].[TblHistorialDetalleTicket] ([idHistorialDetalle], [idDetalle], [idTicket], [idProducto], [idEmpleado], [fechaCambio], [accion], [cantidadUnidades], [precioUnidad], [subtotal]) VALUES (75, 55, 15, 48, 1, '2026-06-12T22:37:41.000', N'INSERT', 1, 0.00, 0.00)
INSERT [dbo].[TblHistorialDetalleTicket] ([idHistorialDetalle], [idDetalle], [idTicket], [idProducto], [idEmpleado], [fechaCambio], [accion], [cantidadUnidades], [precioUnidad], [subtotal]) VALUES (76, 56, 16, 38, 1, '2026-06-13T08:47:40.000', N'INSERT', 1, 3500.00, 3500.00)
INSERT [dbo].[TblHistorialDetalleTicket] ([idHistorialDetalle], [idDetalle], [idTicket], [idProducto], [idEmpleado], [fechaCambio], [accion], [cantidadUnidades], [precioUnidad], [subtotal]) VALUES (77, 57, 16, 42, 1, '2026-06-13T08:47:40.000', N'INSERT', 1, 1000.00, 1000.00)
INSERT [dbo].[TblHistorialDetalleTicket] ([idHistorialDetalle], [idDetalle], [idTicket], [idProducto], [idEmpleado], [fechaCambio], [accion], [cantidadUnidades], [precioUnidad], [subtotal]) VALUES (78, 58, 16, 45, 1, '2026-06-13T08:47:40.000', N'INSERT', 1, 1200.00, 1200.00)
INSERT [dbo].[TblHistorialDetalleTicket] ([idHistorialDetalle], [idDetalle], [idTicket], [idProducto], [idEmpleado], [fechaCambio], [accion], [cantidadUnidades], [precioUnidad], [subtotal]) VALUES (79, 59, 16, 53, 1, '2026-06-13T08:47:40.000', N'INSERT', 1, 1500.00, 1500.00)
SET IDENTITY_INSERT [dbo].[TblHistorialDetalleTicket] OFF
GO

ENABLE TRIGGER ALL ON [dbo].[TblEmpleados];
ENABLE TRIGGER ALL ON [dbo].[TblUsuarios];
ENABLE TRIGGER ALL ON [dbo].[TblMesas];
ENABLE TRIGGER ALL ON [dbo].[TblProductos];
ENABLE TRIGGER ALL ON [dbo].[TblTickets];
ENABLE TRIGGER ALL ON [dbo].[TblDetalleTicket];
ENABLE TRIGGER ALL ON [dbo].[TblPagos];
ENABLE TRIGGER ALL ON [dbo].[TblHistorialProductos];
ENABLE TRIGGER ALL ON [dbo].[TblHistorialReservaciones];
ENABLE TRIGGER ALL ON [dbo].[TblHistorialDetalleTicket];
ENABLE TRIGGER ALL ON [dbo].[TblClientes];
ENABLE TRIGGER ALL ON [dbo].[TblReservaciones];
ENABLE TRIGGER ALL ON [dbo].[TblProduccion];
GO
