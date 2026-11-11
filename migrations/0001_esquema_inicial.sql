
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE FUNCTION [dbo].[fn_TotalTicket](@pIdTicket INT)
RETURNS DECIMAL(10,2)
AS
BEGIN
    DECLARE @vTotal DECIMAL(10,2);

    SELECT @vTotal = ROUND(ISNULL(SUM(subtotal), 0) * 1.13, 2)
    FROM TblDetalleTicket
    WHERE idTicket = @pIdTicket;

    RETURN @vTotal;
END
GO

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[TblMesas](
	[idMesa] [int] IDENTITY(1,1) NOT NULL,
	[numeroMesa] [int] NOT NULL,
	[capacidad] [int] NOT NULL,
	[activo] [bit] NOT NULL,
 CONSTRAINT [PK_TblMesas] PRIMARY KEY CLUSTERED
(
	[idMesa] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY],
 CONSTRAINT [UQ_TblMesas_numeroMesa] UNIQUE NONCLUSTERED
(
	[numeroMesa] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[TblTickets](
	[idTicket] [int] IDENTITY(1,1) NOT NULL,
	[idMesa] [int] NULL,
	[idUsuario] [int] NOT NULL,
	[fecha] [date] NOT NULL,
	[horaInicio] [time](7) NOT NULL,
	[fechaHoraFin] [datetime] NULL,
	[estado] [varchar](20) NOT NULL,
 CONSTRAINT [PK_TblTickets] PRIMARY KEY CLUSTERED
(
	[idTicket] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[TblDetalleTicket](
	[idDetalle] [int] IDENTITY(1,1) NOT NULL,
	[idTicket] [int] NOT NULL,
	[idProducto] [int] NOT NULL,
	[cantidadUnidades] [int] NOT NULL,
	[precioUnidad] [decimal](10, 2) NOT NULL,
	[subtotal] [decimal](10, 2) NOT NULL,
 CONSTRAINT [PK_TblDetalleTicket] PRIMARY KEY CLUSTERED
(
	[idDetalle] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE VIEW [dbo].[vCaja]
AS
SELECT
    t.idTicket,
    m.numeroMesa,
    t.estado,
    ROUND(ISNULL(SUM(dt.subtotal), 0), 2) AS subtotal,
    ROUND(ISNULL(SUM(dt.subtotal), 0) * 0.13, 2) AS impuesto,
    ROUND(ISNULL(SUM(dt.subtotal), 0) * 1.13, 2) AS total
FROM TblTickets t
LEFT JOIN TblMesas m ON t.idMesa = m.idMesa
LEFT JOIN TblDetalleTicket dt ON t.idTicket = dt.idTicket
GROUP BY t.idTicket, m.numeroMesa, t.estado;
GO

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[TblClientes](
	[idCliente] [int] IDENTITY(1,1) NOT NULL,
	[nombre] [varchar](100) NOT NULL,
	[telefono] [varchar](8) NULL,
	[email] [varchar](120) NULL,
	[direccion] [varchar](350) NULL,
	[fechaRegistro] [datetime] NOT NULL,
 CONSTRAINT [PK_TblClientes] PRIMARY KEY CLUSTERED
(
	[idCliente] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[TblReservaciones](
	[idReservacion] [int] IDENTITY(1,1) NOT NULL,
	[idCliente] [int] NOT NULL,
	[idMesa] [int] NOT NULL,
	[idEmpleado] [int] NOT NULL,
	[cantidadPersonas] [int] NOT NULL,
	[fecha] [date] NOT NULL,
	[horaReserva] [time](7) NOT NULL,
	[estado] [varchar](20) NOT NULL,
 CONSTRAINT [PK_TblReservaciones] PRIMARY KEY CLUSTERED
(
	[idReservacion] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[TblEmpleados](
	[idEmpleado] [int] IDENTITY(1,1) NOT NULL,
	[nombre] [varchar](100) NOT NULL,
	[puesto] [varchar](50) NOT NULL,
	[telefono] [varchar](8) NULL,
	[fechaContratacion] [date] NOT NULL,
	[activo] [bit] NOT NULL,
	[esSistema] [bit] NOT NULL,
 CONSTRAINT [PK_TblEmpleados] PRIMARY KEY CLUSTERED
(
	[idEmpleado] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE VIEW [dbo].[vReservacionesCompletas]
AS
SELECT
    r.idReservacion,
    c.nombre AS cliente,
    m.numeroMesa,
    e.nombre AS empleado,
    r.fecha,
    r.horaReserva,
    r.cantidadPersonas,
    r.estado
FROM TblReservaciones r
INNER JOIN TblClientes c ON r.idCliente = c.idCliente
INNER JOIN TblMesas m ON r.idMesa = m.idMesa
INNER JOIN TblEmpleados e ON r.idEmpleado = e.idEmpleado;
GO

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[TblProductos](
	[idProducto] [int] IDENTITY(1,1) NOT NULL,
	[nombre] [varchar](100) NOT NULL,
	[precioUnidad] [decimal](10, 2) NOT NULL,
	[unidadMedida] [varchar](20) NOT NULL,
	[stockUnidades] [int] NOT NULL,
	[activo] [bit] NOT NULL,
 CONSTRAINT [PK_TblProductos] PRIMARY KEY CLUSTERED
(
	[idProducto] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE VIEW [dbo].[vTicketsDetallados]
AS
SELECT
    t.idTicket,
    t.fecha,
    t.horaInicio,
    m.numeroMesa,
    CASE WHEN t.idMesa IS NULL THEN 'Para llevar' ELSE 'En el local' END AS modalidad,
    t.estado,
    p.nombre AS producto,
    dt.cantidadUnidades,
    dt.precioUnidad,
    dt.subtotal
FROM TblTickets t
LEFT JOIN TblMesas m ON t.idMesa = m.idMesa
INNER JOIN TblDetalleTicket dt ON t.idTicket = dt.idTicket
INNER JOIN TblProductos p ON dt.idProducto = p.idProducto;
GO

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[TblHistorialDetalleTicket](
	[idHistorialDetalle] [int] IDENTITY(1,1) NOT NULL,
	[idDetalle] [int] NULL,
	[idTicket] [int] NULL,
	[idProducto] [int] NULL,
	[idEmpleado] [int] NOT NULL,
	[fechaCambio] [datetime] NOT NULL,
	[accion] [varchar](10) NOT NULL,
	[cantidadUnidades] [int] NULL,
	[precioUnidad] [decimal](10, 2) NULL,
	[subtotal] [decimal](10, 2) NULL,
 CONSTRAINT [PK_TblHistorialDetalleTicket] PRIMARY KEY CLUSTERED
(
	[idHistorialDetalle] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[TblHistorialProductos](
	[idHistorialProducto] [int] IDENTITY(1,1) NOT NULL,
	[idProducto] [int] NULL,
	[idEmpleado] [int] NOT NULL,
	[fechaCambio] [datetime] NOT NULL,
	[accion] [varchar](10) NOT NULL,
	[nombre] [varchar](100) NULL,
	[precioUnidad] [decimal](10, 2) NULL,
	[unidadMedida] [varchar](20) NULL,
	[stockUnidades] [int] NULL,
 CONSTRAINT [PK_TblHistorialProductos] PRIMARY KEY CLUSTERED
(
	[idHistorialProducto] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[TblHistorialReservaciones](
	[idHistorialReservacion] [int] IDENTITY(1,1) NOT NULL,
	[idReservacion] [int] NULL,
	[idEmpleado] [int] NOT NULL,
	[idCliente] [int] NULL,
	[idMesa] [int] NULL,
	[fecha] [date] NULL,
	[fechaCambio] [datetime] NOT NULL,
	[horaReserva] [time](7) NULL,
	[accion] [varchar](10) NOT NULL,
	[cantidadPersonas] [int] NULL,
	[estado] [varchar](20) NULL,
 CONSTRAINT [PK_TblHistorialReservaciones] PRIMARY KEY CLUSTERED
(
	[idHistorialReservacion] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[TblPagos](
	[idPago] [int] IDENTITY(1,1) NOT NULL,
	[idTicket] [int] NOT NULL,
	[montoTotal] [decimal](10, 2) NOT NULL,
	[metodoPago] [varchar](20) NOT NULL,
	[fecha] [date] NOT NULL,
	[hora] [time](7) NOT NULL,
	[referencia] [varchar](60) NULL,
 CONSTRAINT [PK_TblPagos] PRIMARY KEY CLUSTERED
(
	[idPago] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY],
 CONSTRAINT [UQ_TblPagos_idTicket] UNIQUE NONCLUSTERED
(
	[idTicket] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[TblPermisos](
	[idPermiso] [int] IDENTITY(1,1) NOT NULL,
	[codigo] [varchar](60) NOT NULL,
	[nombre] [varchar](100) NOT NULL,
 CONSTRAINT [PK_TblPermisos] PRIMARY KEY CLUSTERED
(
	[idPermiso] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY],
 CONSTRAINT [UQ_TblPermisos_codigo] UNIQUE NONCLUSTERED
(
	[codigo] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[TblProduccion](
	[idTblProduccion] [int] IDENTITY(1,1) NOT NULL,
	[idProducto] [int] NOT NULL,
	[idEmpleado] [int] NOT NULL,
	[fecha] [date] NOT NULL,
	[hora] [time](7) NOT NULL,
	[cantidadProducidaUnidades] [int] NOT NULL,
 CONSTRAINT [PK_TblProduccion] PRIMARY KEY CLUSTERED
(
	[idTblProduccion] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[TblRoles](
	[idRol] [int] IDENTITY(1,1) NOT NULL,
	[nombre] [varchar](30) NOT NULL,
	[protegido] [bit] NOT NULL,
 CONSTRAINT [PK_TblRoles] PRIMARY KEY CLUSTERED
(
	[idRol] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY],
 CONSTRAINT [UQ_TblRoles_nombre] UNIQUE NONCLUSTERED
(
	[nombre] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[TblRolesPermisos](
	[idRol] [int] NOT NULL,
	[idPermiso] [int] NOT NULL,
 CONSTRAINT [PK_TblRolesPermisos] PRIMARY KEY CLUSTERED
(
	[idRol] ASC,
	[idPermiso] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[TblUsuarios](
	[idUsuario] [int] IDENTITY(1,1) NOT NULL,
	[correo] [varchar](120) NOT NULL,
	[passwordHash] [varchar](255) NOT NULL,
	[idRol] [int] NOT NULL,
	[idEmpleado] [int] NOT NULL,
	[activo] [bit] NOT NULL,
	[debeCambiarPassword] [bit] NOT NULL,
 CONSTRAINT [PK_TblUsuarios] PRIMARY KEY CLUSTERED
(
	[idUsuario] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY],
 CONSTRAINT [UQ_TblUsuarios_correo] UNIQUE NONCLUSTERED
(
	[correo] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY],
 CONSTRAINT [UQ_TblUsuarios_idEmpleado] UNIQUE NONCLUSTERED
(
	[idEmpleado] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

CREATE NONCLUSTERED INDEX [idx_TblHistorialProductos_fecha] ON [dbo].[TblHistorialProductos]
(
	[fechaCambio] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO

CREATE NONCLUSTERED INDEX [idx_TblPagos_fecha] ON [dbo].[TblPagos]
(
	[fecha] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO

CREATE NONCLUSTERED INDEX [idx_TblProductos_activo] ON [dbo].[TblProductos]
(
	[activo] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO

CREATE NONCLUSTERED INDEX [idx_TblProductos_nombre] ON [dbo].[TblProductos]
(
	[nombre] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO

CREATE UNIQUE NONCLUSTERED INDEX [uxTblProductosNombre] ON [dbo].[TblProductos]
(
	[nombre] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, IGNORE_DUP_KEY = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO

CREATE NONCLUSTERED INDEX [idx_TblReservaciones_estado] ON [dbo].[TblReservaciones]
(
	[estado] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO

CREATE NONCLUSTERED INDEX [idx_TblReservaciones_fecha] ON [dbo].[TblReservaciones]
(
	[fecha] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO

CREATE NONCLUSTERED INDEX [idx_TblReservaciones_fecha_estado] ON [dbo].[TblReservaciones]
(
	[fecha] ASC,
	[estado] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO

CREATE NONCLUSTERED INDEX [idx_TblTickets_estado] ON [dbo].[TblTickets]
(
	[estado] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO

CREATE NONCLUSTERED INDEX [idx_TblTickets_fecha] ON [dbo].[TblTickets]
(
	[fecha] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
ALTER TABLE [dbo].[TblClientes] ADD CONSTRAINT [DF_TblClientes_fechaRegistro] DEFAULT (getdate()) FOR [fechaRegistro]
GO
ALTER TABLE [dbo].[TblEmpleados] ADD CONSTRAINT [DF_TblEmpleados_activo] DEFAULT ((1)) FOR [activo]
GO
ALTER TABLE [dbo].[TblEmpleados] ADD CONSTRAINT [DF_TblEmpleados_esSistema] DEFAULT ((0)) FOR [esSistema]
GO
ALTER TABLE [dbo].[TblHistorialDetalleTicket] ADD CONSTRAINT [DF_TblHistorialDetalleTicket_fechaCambio] DEFAULT (getdate()) FOR [fechaCambio]
GO
ALTER TABLE [dbo].[TblHistorialProductos] ADD CONSTRAINT [DF_TblHistorialProductos_fechaCambio] DEFAULT (getdate()) FOR [fechaCambio]
GO
ALTER TABLE [dbo].[TblHistorialReservaciones] ADD CONSTRAINT [DF_TblHistorialReservaciones_fechaCambio] DEFAULT (getdate()) FOR [fechaCambio]
GO
ALTER TABLE [dbo].[TblMesas] ADD CONSTRAINT [DF_TblMesas_activo] DEFAULT ((1)) FOR [activo]
GO
ALTER TABLE [dbo].[TblProductos] ADD CONSTRAINT [DF_TblProductos_stockUnidades] DEFAULT ((0)) FOR [stockUnidades]
GO
ALTER TABLE [dbo].[TblProductos] ADD CONSTRAINT [DF_TblProductos_activo] DEFAULT ((1)) FOR [activo]
GO
ALTER TABLE [dbo].[TblReservaciones] ADD CONSTRAINT [DF_TblReservaciones_estado] DEFAULT ('Confirmada') FOR [estado]
GO
ALTER TABLE [dbo].[TblRoles] ADD CONSTRAINT [DF_TblRoles_protegido] DEFAULT ((0)) FOR [protegido]
GO
ALTER TABLE [dbo].[TblTickets] ADD CONSTRAINT [DF_TblTickets_estado] DEFAULT ('Pendiente') FOR [estado]
GO
ALTER TABLE [dbo].[TblUsuarios] ADD CONSTRAINT [DF_TblUsuarios_activo] DEFAULT ((1)) FOR [activo]
GO
ALTER TABLE [dbo].[TblUsuarios] ADD CONSTRAINT [DF_TblUsuarios_debeCambiarPassword] DEFAULT ((0)) FOR [debeCambiarPassword]
GO
ALTER TABLE [dbo].[TblDetalleTicket]  WITH CHECK ADD  CONSTRAINT [FK_TblDetalleTicket_producto] FOREIGN KEY([idProducto])
REFERENCES [dbo].[TblProductos] ([idProducto])
GO
ALTER TABLE [dbo].[TblDetalleTicket] CHECK CONSTRAINT [FK_TblDetalleTicket_producto]
GO
ALTER TABLE [dbo].[TblDetalleTicket]  WITH CHECK ADD  CONSTRAINT [FK_TblDetalleTicket_ticket] FOREIGN KEY([idTicket])
REFERENCES [dbo].[TblTickets] ([idTicket])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[TblDetalleTicket] CHECK CONSTRAINT [FK_TblDetalleTicket_ticket]
GO
ALTER TABLE [dbo].[TblPagos]  WITH CHECK ADD  CONSTRAINT [FK_TblPagos_ticket] FOREIGN KEY([idTicket])
REFERENCES [dbo].[TblTickets] ([idTicket])
GO
ALTER TABLE [dbo].[TblPagos] CHECK CONSTRAINT [FK_TblPagos_ticket]
GO
ALTER TABLE [dbo].[TblProduccion]  WITH CHECK ADD  CONSTRAINT [FK_TblProduccion_empleado] FOREIGN KEY([idEmpleado])
REFERENCES [dbo].[TblEmpleados] ([idEmpleado])
GO
ALTER TABLE [dbo].[TblProduccion] CHECK CONSTRAINT [FK_TblProduccion_empleado]
GO
ALTER TABLE [dbo].[TblProduccion]  WITH CHECK ADD  CONSTRAINT [FK_TblProduccion_producto] FOREIGN KEY([idProducto])
REFERENCES [dbo].[TblProductos] ([idProducto])
GO
ALTER TABLE [dbo].[TblProduccion] CHECK CONSTRAINT [FK_TblProduccion_producto]
GO
ALTER TABLE [dbo].[TblReservaciones]  WITH CHECK ADD  CONSTRAINT [FK_TblReservaciones_cliente] FOREIGN KEY([idCliente])
REFERENCES [dbo].[TblClientes] ([idCliente])
GO
ALTER TABLE [dbo].[TblReservaciones] CHECK CONSTRAINT [FK_TblReservaciones_cliente]
GO
ALTER TABLE [dbo].[TblReservaciones]  WITH CHECK ADD  CONSTRAINT [FK_TblReservaciones_empleado] FOREIGN KEY([idEmpleado])
REFERENCES [dbo].[TblEmpleados] ([idEmpleado])
GO
ALTER TABLE [dbo].[TblReservaciones] CHECK CONSTRAINT [FK_TblReservaciones_empleado]
GO
ALTER TABLE [dbo].[TblReservaciones]  WITH CHECK ADD  CONSTRAINT [FK_TblReservaciones_mesa] FOREIGN KEY([idMesa])
REFERENCES [dbo].[TblMesas] ([idMesa])
GO
ALTER TABLE [dbo].[TblReservaciones] CHECK CONSTRAINT [FK_TblReservaciones_mesa]
GO
ALTER TABLE [dbo].[TblRolesPermisos]  WITH CHECK ADD  CONSTRAINT [FK_TblRolesPermisos_permiso] FOREIGN KEY([idPermiso])
REFERENCES [dbo].[TblPermisos] ([idPermiso])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[TblRolesPermisos] CHECK CONSTRAINT [FK_TblRolesPermisos_permiso]
GO
ALTER TABLE [dbo].[TblRolesPermisos]  WITH CHECK ADD  CONSTRAINT [FK_TblRolesPermisos_rol] FOREIGN KEY([idRol])
REFERENCES [dbo].[TblRoles] ([idRol])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[TblRolesPermisos] CHECK CONSTRAINT [FK_TblRolesPermisos_rol]
GO
ALTER TABLE [dbo].[TblTickets]  WITH CHECK ADD  CONSTRAINT [FK_TblTickets_mesa] FOREIGN KEY([idMesa])
REFERENCES [dbo].[TblMesas] ([idMesa])
GO
ALTER TABLE [dbo].[TblTickets] CHECK CONSTRAINT [FK_TblTickets_mesa]
GO
ALTER TABLE [dbo].[TblTickets]  WITH CHECK ADD  CONSTRAINT [FK_TblTickets_usuario] FOREIGN KEY([idUsuario])
REFERENCES [dbo].[TblUsuarios] ([idUsuario])
GO
ALTER TABLE [dbo].[TblTickets] CHECK CONSTRAINT [FK_TblTickets_usuario]
GO
ALTER TABLE [dbo].[TblUsuarios]  WITH CHECK ADD  CONSTRAINT [FK_TblUsuarios_empleado] FOREIGN KEY([idEmpleado])
REFERENCES [dbo].[TblEmpleados] ([idEmpleado])
GO
ALTER TABLE [dbo].[TblUsuarios] CHECK CONSTRAINT [FK_TblUsuarios_empleado]
GO
ALTER TABLE [dbo].[TblUsuarios]  WITH CHECK ADD  CONSTRAINT [FK_TblUsuarios_rol] FOREIGN KEY([idRol])
REFERENCES [dbo].[TblRoles] ([idRol])
GO
ALTER TABLE [dbo].[TblUsuarios] CHECK CONSTRAINT [FK_TblUsuarios_rol]
GO
ALTER TABLE [dbo].[TblPagos]  WITH CHECK ADD  CONSTRAINT [CK_TblPagos_metodoPago] CHECK  (([metodoPago]='Tarjeta' OR [metodoPago]='SINPE' OR [metodoPago]='Efectivo'))
GO
ALTER TABLE [dbo].[TblPagos] CHECK CONSTRAINT [CK_TblPagos_metodoPago]
GO
ALTER TABLE [dbo].[TblProductos]  WITH CHECK ADD  CONSTRAINT [CK_TblProductos_unidadMedida] CHECK  (([unidadMedida]='Botella' OR [unidadMedida]='Vaso' OR [unidadMedida]='Porción'))
GO
ALTER TABLE [dbo].[TblProductos] CHECK CONSTRAINT [CK_TblProductos_unidadMedida]
GO
ALTER TABLE [dbo].[TblReservaciones]  WITH CHECK ADD  CONSTRAINT [CK_TblReservaciones_estado] CHECK  (([estado]='Cancelada' OR [estado]='Confirmada' OR [estado]='Pendiente'))
GO
ALTER TABLE [dbo].[TblReservaciones] CHECK CONSTRAINT [CK_TblReservaciones_estado]
GO
ALTER TABLE [dbo].[TblTickets]  WITH CHECK ADD  CONSTRAINT [CK_TblTickets_estado] CHECK  (([estado]='Anulado' OR [estado]='Pagado' OR [estado]='Pendiente'))
GO
ALTER TABLE [dbo].[TblTickets] CHECK CONSTRAINT [CK_TblTickets_estado]
GO

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE PROCEDURE [dbo].[pa_TotalTicket]
    @pIdTicket INT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT
        @pIdTicket AS idTicket,
        ROUND(ISNULL(SUM(subtotal), 0), 2) AS subtotal,
        ROUND(ISNULL(SUM(subtotal), 0) * 0.13, 2) AS impuesto,
        ROUND(ISNULL(SUM(subtotal), 0) * 1.13, 2) AS total
    FROM TblDetalleTicket
    WHERE idTicket = @pIdTicket;
END
GO

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

CREATE PROCEDURE [dbo].[pa_ProductoActualizar]
    @pIdProducto INT,
    @pNombre VARCHAR(100),
    @pPrecioUnidad DECIMAL(10,2),
    @pUnidadMedida VARCHAR(20),
    @pStockUnidades INT,
    @pActivo BIT
AS
BEGIN
    SET NOCOUNT ON;

        IF @pIdProducto IS NULL
            OR @pIdProducto <= 0
        BEGIN
            RAISERROR(
                'El ID del producto es obligatorio y debe ser mayor que cero.', 16, 1
            );
            RETURN;
        END;

        IF NOT EXISTS (
            SELECT 1
            FROM TblProductos
            WHERE idProducto = @pIdProducto
        )
        BEGIN
            RAISERROR(
                'El producto indicado no existe.', 16, 1
            );
            RETURN;
        END;

        IF @pNombre IS NULL
            OR LEN(LTRIM(RTRIM(@pNombre))) = 0
        BEGIN
            RAISERROR(
                'El nombre del producto es obligatorio.', 16, 1
            );
            RETURN;
        END;

        IF LEN(LTRIM(RTRIM(@pNombre))) > 100
        BEGIN
            RAISERROR(
                'El nombre del producto no puede superar los 100 caracteres.', 16, 1
            );
            RETURN;
        END;

        IF EXISTS (
            SELECT 1
            FROM TblProductos
            WHERE nombre = LTRIM(RTRIM(@pNombre))
              AND idProducto <> @pIdProducto
        )
        BEGIN
            RAISERROR(
                'Ya existe otro producto registrado con ese nombre.', 16, 1
            );
            RETURN;
        END;

        IF @pPrecioUnidad IS NULL
        BEGIN
            RAISERROR(
                'El precio del producto es obligatorio.', 16, 1
            );
            RETURN;
        END;

        IF @pPrecioUnidad < 0
        BEGIN
            RAISERROR(
                'El precio del producto no puede ser negativo.', 16, 1
            );
            RETURN;
        END;

        IF @pUnidadMedida IS NULL
            OR LEN(LTRIM(RTRIM(@pUnidadMedida))) = 0
        BEGIN
            RAISERROR(
                'La unidad de medida es obligatoria.', 16, 1
            );
            RETURN;
        END;

        IF LEN(LTRIM(RTRIM(@pUnidadMedida))) > 20
        BEGIN
            RAISERROR(
                'La unidad de medida no puede superar los 20 caracteres.', 16, 1
            );
            RETURN;
        END;

        IF @pStockUnidades IS NULL
        BEGIN
            RAISERROR(
                'El stock del producto es obligatorio.', 16, 1
            );
            RETURN;
        END;

        IF @pStockUnidades < 0
        BEGIN
            RAISERROR(
                'El stock del producto no puede ser negativo.', 16, 1
            );
            RETURN;
        END;

        IF @pActivo IS NULL
        BEGIN
            RAISERROR(
                'El estado activo del producto es obligatorio.', 16, 1
            );
            RETURN;
        END;

    UPDATE TblProductos
        SET
            nombre = LTRIM(RTRIM(@pNombre)),
            precioUnidad = @pPrecioUnidad,
            unidadMedida = LTRIM(RTRIM(@pUnidadMedida)),
            stockUnidades = @pStockUnidades,
            activo = @pActivo
        WHERE idProducto = @pIdProducto;

        SELECT
            idProducto,
            nombre,
            precioUnidad,
            unidadMedida,
            stockUnidades,
            activo
        FROM TblProductos
        WHERE idProducto = @pIdProducto;

END
GO

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

CREATE PROCEDURE [dbo].[pa_ProductoConsultar]
    @pIdProducto INT = NULL
AS
BEGIN
    SET NOCOUNT ON;

    IF @pIdProducto IS NOT NULL
       AND @pIdProducto <= 0
    BEGIN
        RAISERROR(
            'El ID del producto debe ser mayor que cero.', 16, 1
        );
        RETURN;
    END;

    IF @pIdProducto IS NULL
    BEGIN

        SELECT
            idProducto,
            nombre,
            precioUnidad,
            unidadMedida,
            stockUnidades,
            activo
        FROM TblProductos
        ORDER BY idProducto;

        RETURN;
    END;

SELECT
        idProducto,
        nombre,
        precioUnidad,
        unidadMedida,
        stockUnidades,
        activo
    FROM TblProductos
    WHERE idProducto = @pIdProducto;
END
GO

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

CREATE PROCEDURE [dbo].[pa_ProductoEliminar]
    @pIdProducto INT
AS
BEGIN
    SET NOCOUNT ON;

        IF @pIdProducto IS NULL
            OR @pIdProducto <= 0
        BEGIN
            RAISERROR(
                'El ID del producto es obligatorio y debe ser mayor que cero.', 16, 1
            );
            RETURN;
        END;

        IF NOT EXISTS (
            SELECT 1
            FROM TblProductos
            WHERE idProducto = @pIdProducto
        )
        BEGIN
            RAISERROR(
                'El producto indicado no existe.', 16, 1
            );
            RETURN;
        END;

        IF EXISTS (
            SELECT 1
            FROM TblProductos
            WHERE idProducto = @pIdProducto
              AND activo = 0
        )
        BEGIN
            RAISERROR(
                'El producto ya se encuentra inactivo.', 16, 1
            );
            RETURN;
        END;

    UPDATE TblProductos
        SET activo = 0
        WHERE idProducto = @pIdProducto;

        SELECT
            idProducto,
            nombre,
            precioUnidad,
            unidadMedida,
            stockUnidades,
            activo
        FROM TblProductos
        WHERE idProducto = @pIdProducto;

END
GO

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

CREATE PROCEDURE [dbo].[pa_ProductoInsertar]
    @pNombre VARCHAR(100),
    @pPrecioUnidad DECIMAL(10,2),
    @pUnidadMedida VARCHAR(20),
    @pStockUnidades INT,
    @pActivo BIT
AS
BEGIN
    SET NOCOUNT ON;

        IF @pNombre IS NULL
            OR LEN(LTRIM(RTRIM(@pNombre))) = 0
        BEGIN
            RAISERROR(
                'El nombre del producto es obligatorio.', 16, 1
            );
            RETURN;
        END;

        IF LEN(LTRIM(RTRIM(@pNombre))) > 100
        BEGIN
            RAISERROR(
                'El nombre del producto no puede superar los 100 caracteres.', 16, 1
            );
            RETURN;
        END;

        IF @pPrecioUnidad IS NULL
        BEGIN
            RAISERROR(
                'El precio del producto es obligatorio.', 16, 1
            );
            RETURN;
        END;

        IF @pPrecioUnidad <= 0
        BEGIN
            RAISERROR(
                'El precio del producto no puede ser menor a 0.', 16, 1
            );
            RETURN;
        END;

        IF @pUnidadMedida IS NULL
            OR LEN(LTRIM(RTRIM(@pUnidadMedida))) = 0
        BEGIN
            RAISERROR(
                'La unidad de medida es obligatoria.', 16, 1
            );
            RETURN;
        END;

        IF LEN(LTRIM(RTRIM(@pUnidadMedida))) > 20
        BEGIN
            RAISERROR(
                'La unidad de medida no puede superar los 20 caracteres.', 16, 1
            );
            RETURN;
        END;

        IF @pStockUnidades IS NULL
        BEGIN
            RAISERROR(
                'El stock del producto es obligatorio.', 16, 1
            );
            RETURN;
        END;

        IF @pStockUnidades < 0
        BEGIN
            RAISERROR(
                'El stock del producto no puede ser negativo.', 16, 1
            );
            RETURN;
        END;

        IF @pActivo IS NULL
        BEGIN
            RAISERROR(
                'El estado activo del producto es obligatorio.', 16, 1
            );
            RETURN;
        END;

        IF EXISTS (
            SELECT 1
            FROM TblProductos
            WHERE nombre = LTRIM(RTRIM(@pNombre))
        )
        BEGIN
            RAISERROR(
                'Ya existe un producto registrado con ese nombre.', 16, 1
            );
            RETURN;
        END;

    INSERT INTO TblProductos
        ( nombre, precioUnidad, unidadMedida, stockUnidades, activo )
        VALUES
        (
            LTRIM(RTRIM(@pNombre)),
            @pPrecioUnidad,
            LTRIM(RTRIM(@pUnidadMedida)),
            @pStockUnidades,
            @pActivo
        );

        SELECT
            idProducto,
            nombre,
            precioUnidad,
            unidadMedida,
            stockUnidades,
            activo
        FROM TblProductos
        WHERE idProducto = SCOPE_IDENTITY();

END
GO

SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

CREATE PROCEDURE [dbo].[pa_ProductosBajoStock]
    @pStockMinimo INT
AS
BEGIN
    SET NOCOUNT ON;

    IF @pStockMinimo IS NULL
    BEGIN
        RAISERROR(
            'Debe indicar el stock mínimo.', 16, 1
        );
        RETURN;
    END;

    IF @pStockMinimo < 0
    BEGIN
        RAISERROR(
            'El stock mínimo no puede ser negativo.', 16, 1
        );
        RETURN;
    END;

  SELECT
        idProducto,
        nombre,
        precioUnidad,
        unidadMedida,
        stockUnidades,
        activo
    FROM TblProductos
    WHERE activo = 1
      AND stockUnidades <= @pStockMinimo
    ORDER BY
        stockUnidades ASC,
        nombre ASC;
END
GO

SET IDENTITY_INSERT [dbo].[TblRoles] ON
INSERT [dbo].[TblRoles] ([idRol], [nombre], [protegido]) VALUES (1, N'Administrador', 1)
INSERT [dbo].[TblRoles] ([idRol], [nombre], [protegido]) VALUES (2, N'Mostrador', 0)
INSERT [dbo].[TblRoles] ([idRol], [nombre], [protegido]) VALUES (3, N'Cajero', 0)
INSERT [dbo].[TblRoles] ([idRol], [nombre], [protegido]) VALUES (4, N'Cocinero', 0)
SET IDENTITY_INSERT [dbo].[TblRoles] OFF
GO

SET IDENTITY_INSERT [dbo].[TblPermisos] ON
INSERT [dbo].[TblPermisos] ([idPermiso], [codigo], [nombre]) VALUES (1, N'mostrador.ver', N'Ver mostrador')
INSERT [dbo].[TblPermisos] ([idPermiso], [codigo], [nombre]) VALUES (2, N'mostrador.gestionar', N'Crear y anular tickets')
INSERT [dbo].[TblPermisos] ([idPermiso], [codigo], [nombre]) VALUES (3, N'caja.ver', N'Ver caja')
INSERT [dbo].[TblPermisos] ([idPermiso], [codigo], [nombre]) VALUES (4, N'caja.gestionar', N'Cobrar tickets y liberar mesas')
INSERT [dbo].[TblPermisos] ([idPermiso], [codigo], [nombre]) VALUES (5, N'cocina.ver', N'Ver cocina e inventario')
INSERT [dbo].[TblPermisos] ([idPermiso], [codigo], [nombre]) VALUES (6, N'cocina.gestionar', N'Registrar producción y reposición')
INSERT [dbo].[TblPermisos] ([idPermiso], [codigo], [nombre]) VALUES (7, N'productos.ver', N'Ver productos')
INSERT [dbo].[TblPermisos] ([idPermiso], [codigo], [nombre]) VALUES (8, N'productos.gestionar', N'Administrar productos')
INSERT [dbo].[TblPermisos] ([idPermiso], [codigo], [nombre]) VALUES (9, N'mesas.ver', N'Ver mesas')
INSERT [dbo].[TblPermisos] ([idPermiso], [codigo], [nombre]) VALUES (10, N'mesas.gestionar', N'Administrar mesas')
INSERT [dbo].[TblPermisos] ([idPermiso], [codigo], [nombre]) VALUES (11, N'clientes.ver', N'Ver clientes')
INSERT [dbo].[TblPermisos] ([idPermiso], [codigo], [nombre]) VALUES (12, N'clientes.gestionar', N'Administrar clientes')
INSERT [dbo].[TblPermisos] ([idPermiso], [codigo], [nombre]) VALUES (13, N'reservaciones.ver', N'Ver reservaciones')
INSERT [dbo].[TblPermisos] ([idPermiso], [codigo], [nombre]) VALUES (14, N'reservaciones.gestionar', N'Administrar reservaciones')
INSERT [dbo].[TblPermisos] ([idPermiso], [codigo], [nombre]) VALUES (15, N'empleados.ver', N'Ver empleados')
INSERT [dbo].[TblPermisos] ([idPermiso], [codigo], [nombre]) VALUES (16, N'empleados.gestionar', N'Administrar empleados')
INSERT [dbo].[TblPermisos] ([idPermiso], [codigo], [nombre]) VALUES (17, N'usuarios.gestionar', N'Administrar usuarios')
INSERT [dbo].[TblPermisos] ([idPermiso], [codigo], [nombre]) VALUES (18, N'roles.gestionar', N'Administrar roles y permisos')
INSERT [dbo].[TblPermisos] ([idPermiso], [codigo], [nombre]) VALUES (19, N'bitacoras.ver', N'Ver bitácoras')
INSERT [dbo].[TblPermisos] ([idPermiso], [codigo], [nombre]) VALUES (20, N'reportes.ver', N'Ver reportes')
INSERT [dbo].[TblPermisos] ([idPermiso], [codigo], [nombre]) VALUES (21, N'respaldos.ver', N'Ver historial de respaldos')
INSERT [dbo].[TblPermisos] ([idPermiso], [codigo], [nombre]) VALUES (22, N'respaldos.gestionar', N'Generar respaldos de la base')
SET IDENTITY_INSERT [dbo].[TblPermisos] OFF
GO

INSERT [dbo].[TblRolesPermisos] ([idRol], [idPermiso]) VALUES (1, 1)
INSERT [dbo].[TblRolesPermisos] ([idRol], [idPermiso]) VALUES (1, 2)
INSERT [dbo].[TblRolesPermisos] ([idRol], [idPermiso]) VALUES (1, 3)
INSERT [dbo].[TblRolesPermisos] ([idRol], [idPermiso]) VALUES (1, 4)
INSERT [dbo].[TblRolesPermisos] ([idRol], [idPermiso]) VALUES (1, 5)
INSERT [dbo].[TblRolesPermisos] ([idRol], [idPermiso]) VALUES (1, 6)
INSERT [dbo].[TblRolesPermisos] ([idRol], [idPermiso]) VALUES (1, 7)
INSERT [dbo].[TblRolesPermisos] ([idRol], [idPermiso]) VALUES (1, 8)
INSERT [dbo].[TblRolesPermisos] ([idRol], [idPermiso]) VALUES (1, 9)
INSERT [dbo].[TblRolesPermisos] ([idRol], [idPermiso]) VALUES (1, 10)
INSERT [dbo].[TblRolesPermisos] ([idRol], [idPermiso]) VALUES (1, 11)
INSERT [dbo].[TblRolesPermisos] ([idRol], [idPermiso]) VALUES (1, 12)
INSERT [dbo].[TblRolesPermisos] ([idRol], [idPermiso]) VALUES (1, 13)
INSERT [dbo].[TblRolesPermisos] ([idRol], [idPermiso]) VALUES (1, 14)
INSERT [dbo].[TblRolesPermisos] ([idRol], [idPermiso]) VALUES (1, 15)
INSERT [dbo].[TblRolesPermisos] ([idRol], [idPermiso]) VALUES (1, 16)
INSERT [dbo].[TblRolesPermisos] ([idRol], [idPermiso]) VALUES (1, 17)
INSERT [dbo].[TblRolesPermisos] ([idRol], [idPermiso]) VALUES (1, 18)
INSERT [dbo].[TblRolesPermisos] ([idRol], [idPermiso]) VALUES (1, 19)
INSERT [dbo].[TblRolesPermisos] ([idRol], [idPermiso]) VALUES (1, 20)
INSERT [dbo].[TblRolesPermisos] ([idRol], [idPermiso]) VALUES (1, 21)
INSERT [dbo].[TblRolesPermisos] ([idRol], [idPermiso]) VALUES (1, 22)
INSERT [dbo].[TblRolesPermisos] ([idRol], [idPermiso]) VALUES (2, 1)
INSERT [dbo].[TblRolesPermisos] ([idRol], [idPermiso]) VALUES (2, 2)
INSERT [dbo].[TblRolesPermisos] ([idRol], [idPermiso]) VALUES (2, 7)
INSERT [dbo].[TblRolesPermisos] ([idRol], [idPermiso]) VALUES (2, 9)
INSERT [dbo].[TblRolesPermisos] ([idRol], [idPermiso]) VALUES (2, 10)
INSERT [dbo].[TblRolesPermisos] ([idRol], [idPermiso]) VALUES (2, 11)
INSERT [dbo].[TblRolesPermisos] ([idRol], [idPermiso]) VALUES (2, 12)
INSERT [dbo].[TblRolesPermisos] ([idRol], [idPermiso]) VALUES (2, 13)
INSERT [dbo].[TblRolesPermisos] ([idRol], [idPermiso]) VALUES (2, 14)
INSERT [dbo].[TblRolesPermisos] ([idRol], [idPermiso]) VALUES (3, 1)
INSERT [dbo].[TblRolesPermisos] ([idRol], [idPermiso]) VALUES (3, 2)
INSERT [dbo].[TblRolesPermisos] ([idRol], [idPermiso]) VALUES (3, 3)
INSERT [dbo].[TblRolesPermisos] ([idRol], [idPermiso]) VALUES (3, 4)
INSERT [dbo].[TblRolesPermisos] ([idRol], [idPermiso]) VALUES (3, 9)
INSERT [dbo].[TblRolesPermisos] ([idRol], [idPermiso]) VALUES (3, 10)
INSERT [dbo].[TblRolesPermisos] ([idRol], [idPermiso]) VALUES (3, 11)
INSERT [dbo].[TblRolesPermisos] ([idRol], [idPermiso]) VALUES (3, 12)
INSERT [dbo].[TblRolesPermisos] ([idRol], [idPermiso]) VALUES (3, 13)
INSERT [dbo].[TblRolesPermisos] ([idRol], [idPermiso]) VALUES (3, 14)
INSERT [dbo].[TblRolesPermisos] ([idRol], [idPermiso]) VALUES (3, 20)
INSERT [dbo].[TblRolesPermisos] ([idRol], [idPermiso]) VALUES (4, 5)
INSERT [dbo].[TblRolesPermisos] ([idRol], [idPermiso]) VALUES (4, 6)
INSERT [dbo].[TblRolesPermisos] ([idRol], [idPermiso]) VALUES (4, 7)
INSERT [dbo].[TblRolesPermisos] ([idRol], [idPermiso]) VALUES (4, 8)
GO

SET ANSI_NULLS ON;
GO
SET QUOTED_IDENTIFIER ON;
GO
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
IF OBJECT_ID(N'dbo.TblHistorialProductos', N'U') IS NULL
CREATE TABLE [dbo].[TblHistorialProductos](
	[idHistorialProducto] [int] IDENTITY(1,1) NOT NULL,
	[idProducto] [int] NULL,
	[idEmpleado] [int] NOT NULL,
	[fechaCambio] [datetime] NOT NULL,
	[accion] [varchar](10) NOT NULL,
	[nombre] [varchar](100) NULL,
	[precioUnidad] [decimal](10, 2) NULL,
	[unidadMedida] [varchar](20) NULL,
	[stockUnidades] [int] NULL,
 CONSTRAINT [PK_TblHistorialProductos] PRIMARY KEY CLUSTERED
(
	[idHistorialProducto] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
IF NOT EXISTS (SELECT 1 FROM sys.default_constraints WHERE parent_object_id=OBJECT_ID(N'dbo.TblHistorialProductos') AND parent_column_id=COLUMNPROPERTY(OBJECT_ID(N'dbo.TblHistorialProductos'),N'fechaCambio','ColumnId'))
ALTER TABLE dbo.TblHistorialProductos ADD CONSTRAINT DF_TblHistorialProductos_fechaCambio DEFAULT(GETDATE()) FOR fechaCambio;
GO
IF OBJECT_ID(N'dbo.TblHistorialReservaciones', N'U') IS NULL
CREATE TABLE [dbo].[TblHistorialReservaciones](
	[idHistorialReservacion] [int] IDENTITY(1,1) NOT NULL,
	[idReservacion] [int] NULL,
	[idEmpleado] [int] NOT NULL,
	[idCliente] [int] NULL,
	[idMesa] [int] NULL,
	[fecha] [date] NULL,
	[fechaCambio] [datetime] NOT NULL,
	[horaReserva] [time](7) NULL,
	[accion] [varchar](10) NOT NULL,
	[cantidadPersonas] [int] NULL,
	[estado] [varchar](20) NULL,
 CONSTRAINT [PK_TblHistorialReservaciones] PRIMARY KEY CLUSTERED
(
	[idHistorialReservacion] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
IF NOT EXISTS (SELECT 1 FROM sys.default_constraints WHERE parent_object_id=OBJECT_ID(N'dbo.TblHistorialReservaciones') AND parent_column_id=COLUMNPROPERTY(OBJECT_ID(N'dbo.TblHistorialReservaciones'),N'fechaCambio','ColumnId'))
ALTER TABLE dbo.TblHistorialReservaciones ADD CONSTRAINT DF_TblHistorialReservaciones_fechaCambio DEFAULT(GETDATE()) FOR fechaCambio;
GO
IF OBJECT_ID(N'dbo.TblHistorialDetalleTicket', N'U') IS NULL
CREATE TABLE [dbo].[TblHistorialDetalleTicket](
	[idHistorialDetalle] [int] IDENTITY(1,1) NOT NULL,
	[idDetalle] [int] NULL,
	[idTicket] [int] NULL,
	[idProducto] [int] NULL,
	[idEmpleado] [int] NOT NULL,
	[fechaCambio] [datetime] NOT NULL,
	[accion] [varchar](10) NOT NULL,
	[cantidadUnidades] [int] NULL,
	[precioUnidad] [decimal](10, 2) NULL,
	[subtotal] [decimal](10, 2) NULL,
 CONSTRAINT [PK_TblHistorialDetalleTicket] PRIMARY KEY CLUSTERED
(
	[idHistorialDetalle] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
IF NOT EXISTS (SELECT 1 FROM sys.default_constraints WHERE parent_object_id=OBJECT_ID(N'dbo.TblHistorialDetalleTicket') AND parent_column_id=COLUMNPROPERTY(OBJECT_ID(N'dbo.TblHistorialDetalleTicket'),N'fechaCambio','ColumnId'))
ALTER TABLE dbo.TblHistorialDetalleTicket ADD CONSTRAINT DF_TblHistorialDetalleTicket_fechaCambio DEFAULT(GETDATE()) FOR fechaCambio;
GO

IF NOT EXISTS (SELECT 1 FROM dbo.TblEmpleados WHERE esSistema=1)
 INSERT dbo.TblEmpleados(nombre,puesto,telefono,fechaContratacion,activo,esSistema)
 VALUES ('Sistema auditoria','Sistema',NULL,CONVERT(date,GETDATE()),1,1);
GO

CREATE OR ALTER FUNCTION dbo.fn_EmpleadoBitacora(@pIdEmpleadoAlternativo INT)
RETURNS INT
AS
BEGIN
 DECLARE @actor INT=TRY_CAST(SESSION_CONTEXT(N'idEmpleado') AS INT);
 IF EXISTS(SELECT 1 FROM dbo.TblEmpleados WHERE idEmpleado=@actor) RETURN @actor;
 RETURN (SELECT TOP (1) idEmpleado FROM dbo.TblEmpleados WHERE esSistema=1 ORDER BY idEmpleado);
END;
GO

IF COL_LENGTH(N'dbo.TblHistorialProductos',N'activo') IS NULL
 ALTER TABLE dbo.TblHistorialProductos ADD [activo]                 BIT            NULL;
GO
IF COL_LENGTH(N'dbo.TblHistorialProductos',N'nombreAnterior') IS NULL
 ALTER TABLE dbo.TblHistorialProductos ADD [nombreAnterior]         VARCHAR(100)   NULL;
GO
IF COL_LENGTH(N'dbo.TblHistorialProductos',N'precioUnidadAnterior') IS NULL
 ALTER TABLE dbo.TblHistorialProductos ADD [precioUnidadAnterior]   DECIMAL(10, 2) NULL;
GO
IF COL_LENGTH(N'dbo.TblHistorialProductos',N'unidadMedidaAnterior') IS NULL
 ALTER TABLE dbo.TblHistorialProductos ADD [unidadMedidaAnterior]   VARCHAR(20)    NULL;
GO
IF COL_LENGTH(N'dbo.TblHistorialProductos',N'stockUnidadesAnterior') IS NULL
 ALTER TABLE dbo.TblHistorialProductos ADD [stockUnidadesAnterior]  INT            NULL;
GO
IF COL_LENGTH(N'dbo.TblHistorialProductos',N'activoAnterior') IS NULL
 ALTER TABLE dbo.TblHistorialProductos ADD [activoAnterior]         BIT            NULL;
GO
IF COL_LENGTH(N'dbo.TblHistorialProductos',N'usuarioBD') IS NULL
 ALTER TABLE dbo.TblHistorialProductos ADD [usuarioBD]  NVARCHAR(128) NULL CONSTRAINT [DF_TblHistorialProductos_usuarioBD]  DEFAULT (SUSER_SNAME());
GO
IF COL_LENGTH(N'dbo.TblHistorialProductos',N'equipo') IS NULL
 ALTER TABLE dbo.TblHistorialProductos ADD [equipo]     NVARCHAR(128) NULL CONSTRAINT [DF_TblHistorialProductos_equipo]     DEFAULT (HOST_NAME());
GO
IF COL_LENGTH(N'dbo.TblHistorialProductos',N'aplicacion') IS NULL
 ALTER TABLE dbo.TblHistorialProductos ADD [aplicacion] NVARCHAR(128) NULL CONSTRAINT [DF_TblHistorialProductos_aplicacion] DEFAULT (APP_NAME());
GO

IF COL_LENGTH(N'dbo.TblHistorialReservaciones',N'idClienteAnterior') IS NULL
 ALTER TABLE dbo.TblHistorialReservaciones ADD [idClienteAnterior]         INT         NULL;
GO
IF COL_LENGTH(N'dbo.TblHistorialReservaciones',N'idMesaAnterior') IS NULL
 ALTER TABLE dbo.TblHistorialReservaciones ADD [idMesaAnterior]            INT         NULL;
GO
IF COL_LENGTH(N'dbo.TblHistorialReservaciones',N'fechaAnterior') IS NULL
 ALTER TABLE dbo.TblHistorialReservaciones ADD [fechaAnterior]             DATE        NULL;
GO
IF COL_LENGTH(N'dbo.TblHistorialReservaciones',N'horaReservaAnterior') IS NULL
 ALTER TABLE dbo.TblHistorialReservaciones ADD [horaReservaAnterior]       TIME(7)     NULL;
GO
IF COL_LENGTH(N'dbo.TblHistorialReservaciones',N'cantidadPersonasAnterior') IS NULL
 ALTER TABLE dbo.TblHistorialReservaciones ADD [cantidadPersonasAnterior]  INT         NULL;
GO
IF COL_LENGTH(N'dbo.TblHistorialReservaciones',N'estadoAnterior') IS NULL
 ALTER TABLE dbo.TblHistorialReservaciones ADD [estadoAnterior]            VARCHAR(20) NULL;
GO
IF COL_LENGTH(N'dbo.TblHistorialReservaciones',N'usuarioBD') IS NULL
 ALTER TABLE dbo.TblHistorialReservaciones ADD [usuarioBD]  NVARCHAR(128) NULL CONSTRAINT [DF_TblHistorialReservaciones_usuarioBD]  DEFAULT (SUSER_SNAME());
GO
IF COL_LENGTH(N'dbo.TblHistorialReservaciones',N'equipo') IS NULL
 ALTER TABLE dbo.TblHistorialReservaciones ADD [equipo]     NVARCHAR(128) NULL CONSTRAINT [DF_TblHistorialReservaciones_equipo]     DEFAULT (HOST_NAME());
GO
IF COL_LENGTH(N'dbo.TblHistorialReservaciones',N'aplicacion') IS NULL
 ALTER TABLE dbo.TblHistorialReservaciones ADD [aplicacion] NVARCHAR(128) NULL CONSTRAINT [DF_TblHistorialReservaciones_aplicacion] DEFAULT (APP_NAME());
GO

IF COL_LENGTH(N'dbo.TblHistorialDetalleTicket',N'cantidadUnidadesAnterior') IS NULL
 ALTER TABLE dbo.TblHistorialDetalleTicket ADD [cantidadUnidadesAnterior]  INT            NULL;
GO
IF COL_LENGTH(N'dbo.TblHistorialDetalleTicket',N'precioUnidadAnterior') IS NULL
 ALTER TABLE dbo.TblHistorialDetalleTicket ADD [precioUnidadAnterior]      DECIMAL(10, 2) NULL;
GO
IF COL_LENGTH(N'dbo.TblHistorialDetalleTicket',N'subtotalAnterior') IS NULL
 ALTER TABLE dbo.TblHistorialDetalleTicket ADD [subtotalAnterior]          DECIMAL(10, 2) NULL;
GO
IF COL_LENGTH(N'dbo.TblHistorialDetalleTicket',N'usuarioBD') IS NULL
 ALTER TABLE dbo.TblHistorialDetalleTicket ADD [usuarioBD]  NVARCHAR(128) NULL CONSTRAINT [DF_TblHistorialDetalleTicket_usuarioBD]  DEFAULT (SUSER_SNAME());
GO
IF COL_LENGTH(N'dbo.TblHistorialDetalleTicket',N'equipo') IS NULL
 ALTER TABLE dbo.TblHistorialDetalleTicket ADD [equipo]     NVARCHAR(128) NULL CONSTRAINT [DF_TblHistorialDetalleTicket_equipo]     DEFAULT (HOST_NAME());
GO
IF COL_LENGTH(N'dbo.TblHistorialDetalleTicket',N'aplicacion') IS NULL
 ALTER TABLE dbo.TblHistorialDetalleTicket ADD [aplicacion] NVARCHAR(128) NULL CONSTRAINT [DF_TblHistorialDetalleTicket_aplicacion] DEFAULT (APP_NAME());
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'idx_TblHistorialReservaciones_fecha')
    CREATE NONCLUSTERED INDEX [idx_TblHistorialReservaciones_fecha]
        ON [dbo].[TblHistorialReservaciones] ([fechaCambio]);
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'idx_TblHistorialDetalleTicket_fecha')
    CREATE NONCLUSTERED INDEX [idx_TblHistorialDetalleTicket_fecha]
        ON [dbo].[TblHistorialDetalleTicket] ([fechaCambio]);
GO

IF OBJECT_ID(N'dbo.TblAuditoriaCaja', N'U') IS NULL
    CREATE TABLE [dbo].[TblAuditoriaCaja] (
        [idAuditoriaCaja]     INT IDENTITY(1, 1) NOT NULL,
        [fechaHora]           DATETIME2(3)   NOT NULL CONSTRAINT [DF_TblAuditoriaCaja_fechaHora] DEFAULT (SYSDATETIME()),
        [idEmpleado]          INT            NOT NULL,
        [tablaAfectada]       VARCHAR(30)    NOT NULL,
        [accion]              VARCHAR(10)    NOT NULL,
        [idRegistro]          INT            NOT NULL,
        [idTicket]            INT            NULL,
        [montoTicket]         DECIMAL(10, 2) NULL,
        [estadoAnterior]      VARCHAR(20)    NULL,
        [estadoNuevo]         VARCHAR(20)    NULL,
        [montoAnterior]       DECIMAL(10, 2) NULL,
        [montoNuevo]          DECIMAL(10, 2) NULL,
        [metodoPagoAnterior]  VARCHAR(20)    NULL,
        [metodoPagoNuevo]     VARCHAR(20)    NULL,
        [referenciaAnterior]  VARCHAR(60)    NULL,
        [referenciaNueva]     VARCHAR(60)    NULL,
        [usuarioBD]   NVARCHAR(128) NULL CONSTRAINT [DF_TblAuditoriaCaja_usuarioBD]  DEFAULT (SUSER_SNAME()),
        [equipo]      NVARCHAR(128) NULL CONSTRAINT [DF_TblAuditoriaCaja_equipo]     DEFAULT (HOST_NAME()),
        [aplicacion]  NVARCHAR(128) NULL CONSTRAINT [DF_TblAuditoriaCaja_aplicacion] DEFAULT (APP_NAME()),
        CONSTRAINT [PK_TblAuditoriaCaja] PRIMARY KEY CLUSTERED ([idAuditoriaCaja]),
        CONSTRAINT [CK_TblAuditoriaCaja_accion] CHECK ([accion] IN ('INSERT', 'UPDATE', 'DELETE'))
    );
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'idx_TblAuditoriaCaja_fecha')
    CREATE NONCLUSTERED INDEX [idx_TblAuditoriaCaja_fecha] ON [dbo].[TblAuditoriaCaja] ([fechaHora]);
GO

IF OBJECT_ID(N'dbo.TblAuditoriaSeguridad', N'U') IS NULL
    CREATE TABLE [dbo].[TblAuditoriaSeguridad] (
        [idAuditoriaSeguridad]  INT IDENTITY(1, 1) NOT NULL,
        [fechaHora]             DATETIME2(3)  NOT NULL CONSTRAINT [DF_TblAuditoriaSeguridad_fechaHora] DEFAULT (SYSDATETIME()),
        [idEmpleado]            INT           NOT NULL,
        [tablaAfectada]         NVARCHAR(128) NOT NULL,
        [accion]                VARCHAR(40)   NOT NULL,
        [idRegistro]            INT           NULL,
        [correoAnterior]        VARCHAR(120)  NULL,
        [correoNuevo]           VARCHAR(120)  NULL,
        [idRolAnterior]         INT           NULL,
        [idRolNuevo]            INT           NULL,
        [activoAnterior]        BIT           NULL,
        [activoNuevo]           BIT           NULL,
        [cambioPassword]        BIT           NULL,
        [idPermiso]             INT           NULL,
        [detalle]               NVARCHAR(MAX) NULL,
        [usuarioBD]   NVARCHAR(128) NULL CONSTRAINT [DF_TblAuditoriaSeguridad_usuarioBD]  DEFAULT (SUSER_SNAME()),
        [equipo]      NVARCHAR(128) NULL CONSTRAINT [DF_TblAuditoriaSeguridad_equipo]     DEFAULT (HOST_NAME()),
        [aplicacion]  NVARCHAR(128) NULL CONSTRAINT [DF_TblAuditoriaSeguridad_aplicacion] DEFAULT (APP_NAME()),
        CONSTRAINT [PK_TblAuditoriaSeguridad] PRIMARY KEY CLUSTERED ([idAuditoriaSeguridad])
    );
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'idx_TblAuditoriaSeguridad_fecha')
    CREATE NONCLUSTERED INDEX [idx_TblAuditoriaSeguridad_fecha] ON [dbo].[TblAuditoriaSeguridad] ([fechaHora]);
GO

IF OBJECT_ID(N'dbo.TblAuditoriaSesiones', N'U') IS NULL
    CREATE TABLE [dbo].[TblAuditoriaSesiones] (
        [idAuditoriaSesion]  INT IDENTITY(1, 1) NOT NULL,
        [fechaHora]          DATETIME2(3)  NOT NULL CONSTRAINT [DF_TblAuditoriaSesiones_fechaHora] DEFAULT (SYSDATETIME()),
        [evento]             VARCHAR(20)   NOT NULL,
        [correo]             VARCHAR(120)  NOT NULL,
        [idUsuario]          INT           NULL,
        [idEmpleado]         INT           NULL,
        [direccionIp]        VARCHAR(45)   NULL,
        [navegador]          VARCHAR(200)  NULL,
        [usuarioBD]   NVARCHAR(128) NULL CONSTRAINT [DF_TblAuditoriaSesiones_usuarioBD] DEFAULT (SUSER_SNAME()),
        [equipo]      NVARCHAR(128) NULL CONSTRAINT [DF_TblAuditoriaSesiones_equipo]    DEFAULT (HOST_NAME()),
        CONSTRAINT [PK_TblAuditoriaSesiones] PRIMARY KEY CLUSTERED ([idAuditoriaSesion]),
        CONSTRAINT [CK_TblAuditoriaSesiones_evento] CHECK ([evento] IN ('LOGIN_OK', 'LOGIN_FALLIDO', 'LOGOUT'))
    );
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'idx_TblAuditoriaSesiones_fecha')
    CREATE NONCLUSTERED INDEX [idx_TblAuditoriaSesiones_fecha] ON [dbo].[TblAuditoriaSesiones] ([fechaHora]);
GO

IF OBJECT_ID(N'dbo.CK_TblAuditoriaCaja_accion',N'C') IS NOT NULL
 ALTER TABLE dbo.TblAuditoriaCaja DROP CONSTRAINT CK_TblAuditoriaCaja_accion;
GO
ALTER TABLE dbo.TblAuditoriaCaja WITH CHECK ADD CONSTRAINT CK_TblAuditoriaCaja_accion
 CHECK(accion IN ('INSERT','UPDATE','DELETE'));
GO
IF COL_LENGTH(N'dbo.TblHistorialDetalleTicket',N'idTicketAnterior') IS NULL ALTER TABLE dbo.TblHistorialDetalleTicket ADD idTicketAnterior INT NULL;
GO
IF COL_LENGTH(N'dbo.TblHistorialDetalleTicket',N'idProductoAnterior') IS NULL ALTER TABLE dbo.TblHistorialDetalleTicket ADD idProductoAnterior INT NULL;
GO
IF COL_LENGTH(N'dbo.TblAuditoriaCaja',N'idTicketAnterior') IS NULL ALTER TABLE dbo.TblAuditoriaCaja ADD idTicketAnterior INT NULL;
GO
IF COL_LENGTH(N'dbo.TblAuditoriaSeguridad',N'idEmpleadoAsociadoAnterior') IS NULL ALTER TABLE dbo.TblAuditoriaSeguridad ADD idEmpleadoAsociadoAnterior INT NULL;
GO
IF COL_LENGTH(N'dbo.TblAuditoriaSeguridad',N'idEmpleadoAsociadoNuevo') IS NULL ALTER TABLE dbo.TblAuditoriaSeguridad ADD idEmpleadoAsociadoNuevo INT NULL;
GO
IF COL_LENGTH(N'dbo.TblAuditoriaSeguridad',N'debeCambiarPasswordAnterior') IS NULL ALTER TABLE dbo.TblAuditoriaSeguridad ADD debeCambiarPasswordAnterior BIT NULL;
GO
IF COL_LENGTH(N'dbo.TblAuditoriaSeguridad',N'debeCambiarPasswordNuevo') IS NULL ALTER TABLE dbo.TblAuditoriaSeguridad ADD debeCambiarPasswordNuevo BIT NULL;
GO

CREATE OR ALTER TRIGGER [dbo].[trg_BitacoraProductosInsert]
ON [dbo].[TblProductos]
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO [dbo].[TblHistorialProductos]
        (idProducto, idEmpleado, accion, nombre, precioUnidad, unidadMedida, stockUnidades, activo)
    SELECT i.idProducto, dbo.fn_EmpleadoBitacora(NULL), 'INSERT',
           i.nombre, i.precioUnidad, i.unidadMedida, i.stockUnidades, i.activo
    FROM inserted AS i;
END
GO

CREATE OR ALTER TRIGGER [dbo].[trg_BitacoraProductosUpdate]
ON [dbo].[TblProductos]
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO [dbo].[TblHistorialProductos]
        (idProducto, idEmpleado, accion,
         nombre, precioUnidad, unidadMedida, stockUnidades, activo,
         nombreAnterior, precioUnidadAnterior, unidadMedidaAnterior, stockUnidadesAnterior, activoAnterior)
    SELECT i.idProducto, dbo.fn_EmpleadoBitacora(NULL), 'UPDATE',
           i.nombre, i.precioUnidad, i.unidadMedida, i.stockUnidades, i.activo,
           d.nombre, d.precioUnidad, d.unidadMedida, d.stockUnidades, d.activo
    FROM inserted AS i
    INNER JOIN deleted AS d ON d.idProducto = i.idProducto;
END
GO

CREATE OR ALTER TRIGGER [dbo].[trg_BitacoraProductosDelete]
ON [dbo].[TblProductos]
AFTER DELETE
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO [dbo].[TblHistorialProductos]
        (idProducto, idEmpleado, accion, nombre, precioUnidad, unidadMedida, stockUnidades, activo)
    SELECT d.idProducto, dbo.fn_EmpleadoBitacora(NULL), 'DELETE',
           d.nombre, d.precioUnidad, d.unidadMedida, d.stockUnidades, d.activo
    FROM deleted AS d;
END
GO

CREATE OR ALTER TRIGGER [dbo].[trg_BitacoraReservacionesInsert]
ON [dbo].[TblReservaciones]
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO [dbo].[TblHistorialReservaciones]
        (idReservacion, idEmpleado, accion, idCliente, idMesa, fecha, horaReserva, cantidadPersonas, estado)
    SELECT i.idReservacion, dbo.fn_EmpleadoBitacora(i.idEmpleado), 'INSERT',
           i.idCliente, i.idMesa, i.fecha, i.horaReserva, i.cantidadPersonas, i.estado
    FROM inserted AS i;
END
GO

CREATE OR ALTER TRIGGER [dbo].[trg_BitacoraReservacionesUpdate]
ON [dbo].[TblReservaciones]
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO [dbo].[TblHistorialReservaciones]
        (idReservacion, idEmpleado, accion,
         idCliente, idMesa, fecha, horaReserva, cantidadPersonas, estado,
         idClienteAnterior, idMesaAnterior, fechaAnterior, horaReservaAnterior,
         cantidadPersonasAnterior, estadoAnterior)
    SELECT i.idReservacion, dbo.fn_EmpleadoBitacora(i.idEmpleado), 'UPDATE',
           i.idCliente, i.idMesa, i.fecha, i.horaReserva, i.cantidadPersonas, i.estado,
           d.idCliente, d.idMesa, d.fecha, d.horaReserva, d.cantidadPersonas, d.estado
    FROM inserted AS i
    INNER JOIN deleted AS d ON d.idReservacion = i.idReservacion;
END
GO

CREATE OR ALTER TRIGGER [dbo].[trg_BitacoraReservacionesDelete]
ON [dbo].[TblReservaciones]
AFTER DELETE
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO [dbo].[TblHistorialReservaciones]
        (idReservacion, idEmpleado, accion, idCliente, idMesa, fecha, horaReserva, cantidadPersonas, estado)
    SELECT d.idReservacion, dbo.fn_EmpleadoBitacora(d.idEmpleado), 'DELETE',
           d.idCliente, d.idMesa, d.fecha, d.horaReserva, d.cantidadPersonas, d.estado
    FROM deleted AS d;
END
GO

CREATE OR ALTER TRIGGER [dbo].[trg_BitacoraDetalleTicketInsert]
ON [dbo].[TblDetalleTicket]
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO [dbo].[TblHistorialDetalleTicket]
        (idDetalle, idTicket, idProducto, idEmpleado, accion, cantidadUnidades, precioUnidad, subtotal)
    SELECT i.idDetalle, i.idTicket, i.idProducto, dbo.fn_EmpleadoBitacora(NULL), 'INSERT',
           i.cantidadUnidades, i.precioUnidad, i.subtotal
    FROM inserted AS i;
END
GO

CREATE OR ALTER TRIGGER [dbo].[trg_BitacoraDetalleTicketUpdate]
ON [dbo].[TblDetalleTicket]
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO [dbo].[TblHistorialDetalleTicket]
        (idDetalle, idTicket, idProducto, idEmpleado, accion,
         cantidadUnidades, precioUnidad, subtotal,
         cantidadUnidadesAnterior, precioUnidadAnterior, subtotalAnterior, idTicketAnterior, idProductoAnterior)
    SELECT i.idDetalle, i.idTicket, i.idProducto, dbo.fn_EmpleadoBitacora(NULL), 'UPDATE',
           i.cantidadUnidades, i.precioUnidad, i.subtotal,
           d.cantidadUnidades, d.precioUnidad, d.subtotal, d.idTicket, d.idProducto
    FROM inserted AS i
    INNER JOIN deleted AS d ON d.idDetalle = i.idDetalle;
END
GO

CREATE OR ALTER TRIGGER [dbo].[trg_BitacoraDetalleTicketDelete]
ON [dbo].[TblDetalleTicket]
AFTER DELETE
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO [dbo].[TblHistorialDetalleTicket]
        (idDetalle, idTicket, idProducto, idEmpleado, accion, cantidadUnidades, precioUnidad, subtotal)
    SELECT d.idDetalle, d.idTicket, d.idProducto, dbo.fn_EmpleadoBitacora(NULL), 'DELETE',
           d.cantidadUnidades, d.precioUnidad, d.subtotal
    FROM deleted AS d;
END
GO

CREATE OR ALTER TRIGGER [dbo].[trg_AuditoriaCajaTicketsUpdate]
ON [dbo].[TblTickets]
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO [dbo].[TblAuditoriaCaja]
        (idEmpleado, tablaAfectada, accion, idRegistro, idTicket, montoTicket, estadoAnterior, estadoNuevo)
    SELECT dbo.fn_EmpleadoBitacora(u.idEmpleado), 'TblTickets', 'UPDATE', i.idTicket, i.idTicket,
           dbo.fn_TotalTicket(i.idTicket), d.estado, i.estado
    FROM inserted AS i
    INNER JOIN deleted AS d ON d.idTicket = i.idTicket
    LEFT JOIN dbo.TblUsuarios AS u ON u.idUsuario = i.idUsuario
    WHERE i.estado <> d.estado;
END
GO

CREATE OR ALTER TRIGGER [dbo].[trg_AuditoriaCajaTicketsDelete]
ON [dbo].[TblTickets]
AFTER DELETE
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO [dbo].[TblAuditoriaCaja]
        (idEmpleado, tablaAfectada, accion, idRegistro, idTicket, estadoAnterior)
    SELECT dbo.fn_EmpleadoBitacora(NULL), 'TblTickets', 'DELETE', d.idTicket, d.idTicket, d.estado
    FROM deleted AS d;
END
GO

CREATE OR ALTER TRIGGER [dbo].[trg_AuditoriaCajaPagosUpdate]
ON [dbo].[TblPagos]
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO [dbo].[TblAuditoriaCaja]
        (idEmpleado, tablaAfectada, accion, idRegistro, idTicket,
         idTicketAnterior, montoAnterior, montoNuevo, metodoPagoAnterior, metodoPagoNuevo,
         referenciaAnterior, referenciaNueva)
    SELECT dbo.fn_EmpleadoBitacora(NULL), 'TblPagos', 'UPDATE', i.idPago, i.idTicket,
           d.idTicket, d.montoTotal, i.montoTotal, d.metodoPago, i.metodoPago,
           d.referencia, i.referencia
    FROM inserted AS i
    INNER JOIN deleted AS d ON d.idPago = i.idPago;
END
GO

CREATE OR ALTER TRIGGER [dbo].[trg_AuditoriaCajaPagosDelete]
ON [dbo].[TblPagos]
AFTER DELETE
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO [dbo].[TblAuditoriaCaja]
        (idEmpleado, tablaAfectada, accion, idRegistro, idTicket,
         montoAnterior, metodoPagoAnterior, referenciaAnterior)
    SELECT dbo.fn_EmpleadoBitacora(NULL), 'TblPagos', 'DELETE', d.idPago, d.idTicket,
           d.montoTotal, d.metodoPago, d.referencia
    FROM deleted AS d;
END
GO

CREATE OR ALTER TRIGGER [dbo].[trg_AuditoriaSeguridadUsuariosInsert]
ON [dbo].[TblUsuarios]
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO [dbo].[TblAuditoriaSeguridad]
        (idEmpleado, tablaAfectada, accion, idRegistro, correoNuevo, idRolNuevo, activoNuevo, cambioPassword, idEmpleadoAsociadoNuevo, debeCambiarPasswordNuevo)
    SELECT dbo.fn_EmpleadoBitacora(NULL), N'TblUsuarios', 'INSERT', i.idUsuario,
           i.correo, i.idRol, i.activo, 1, i.idEmpleado, i.debeCambiarPassword
    FROM inserted AS i;
END
GO

CREATE OR ALTER TRIGGER [dbo].[trg_AuditoriaSeguridadUsuariosUpdate]
ON [dbo].[TblUsuarios]
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO [dbo].[TblAuditoriaSeguridad]
        (idEmpleado, tablaAfectada, accion, idRegistro,
         correoAnterior, correoNuevo, idRolAnterior, idRolNuevo,
         activoAnterior, activoNuevo, cambioPassword, idEmpleadoAsociadoAnterior, idEmpleadoAsociadoNuevo, debeCambiarPasswordAnterior, debeCambiarPasswordNuevo)
    SELECT dbo.fn_EmpleadoBitacora(NULL), N'TblUsuarios', 'UPDATE', i.idUsuario,
           d.correo, i.correo, d.idRol, i.idRol,
           d.activo, i.activo,
           CASE WHEN i.passwordHash <> d.passwordHash THEN 1 ELSE 0 END,
           d.idEmpleado, i.idEmpleado, d.debeCambiarPassword, i.debeCambiarPassword
    FROM inserted AS i
    INNER JOIN deleted AS d ON d.idUsuario = i.idUsuario
    WHERE EXISTS (
        SELECT i.correo, i.idRol, i.idEmpleado, i.activo, i.passwordHash, i.debeCambiarPassword
        EXCEPT
        SELECT d.correo, d.idRol, d.idEmpleado, d.activo, d.passwordHash, d.debeCambiarPassword
    );
END
GO

CREATE OR ALTER TRIGGER [dbo].[trg_AuditoriaSeguridadUsuariosDelete]
ON [dbo].[TblUsuarios]
AFTER DELETE
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO [dbo].[TblAuditoriaSeguridad]
        (idEmpleado, tablaAfectada, accion, idRegistro, correoAnterior, idRolAnterior, activoAnterior, idEmpleadoAsociadoAnterior, debeCambiarPasswordAnterior)
    SELECT dbo.fn_EmpleadoBitacora(NULL), N'TblUsuarios', 'DELETE', d.idUsuario,
           d.correo, d.idRol, d.activo, d.idEmpleado, d.debeCambiarPassword
    FROM deleted AS d;
END
GO

CREATE OR ALTER TRIGGER [dbo].[trg_AuditoriaSeguridadRolesPermisosInsert]
ON [dbo].[TblRolesPermisos]
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO [dbo].[TblAuditoriaSeguridad]
        (idEmpleado, tablaAfectada, accion, idRegistro, idRolNuevo, idPermiso)
    SELECT dbo.fn_EmpleadoBitacora(NULL), N'TblRolesPermisos', 'INSERT', i.idRol, i.idRol, i.idPermiso
    FROM inserted AS i;
END
GO

CREATE OR ALTER TRIGGER [dbo].[trg_AuditoriaSeguridadRolesPermisosDelete]
ON [dbo].[TblRolesPermisos]
AFTER DELETE
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO [dbo].[TblAuditoriaSeguridad]
        (idEmpleado, tablaAfectada, accion, idRegistro, idRolAnterior, idPermiso)
    SELECT dbo.fn_EmpleadoBitacora(NULL), N'TblRolesPermisos', 'DELETE', d.idRol, d.idRol, d.idPermiso
    FROM deleted AS d;
END
GO

CREATE OR ALTER TRIGGER dbo.trg_AuditoriaCajaPagosInsert ON dbo.TblPagos AFTER INSERT AS
BEGIN
 SET NOCOUNT ON;
 INSERT dbo.TblAuditoriaCaja(idEmpleado,tablaAfectada,accion,idRegistro,idTicket,montoNuevo,metodoPagoNuevo,referenciaNueva)
 SELECT dbo.fn_EmpleadoBitacora(NULL),'TblPagos','INSERT',idPago,idTicket,montoTotal,metodoPago,referencia FROM inserted;
END;
GO

CREATE OR ALTER TRIGGER dbo.trg_AuditoriaSeguridadRolesPermisosUpdate
ON dbo.TblRolesPermisos AFTER UPDATE AS
BEGIN
 SET NOCOUNT ON;
 INSERT dbo.TblAuditoriaSeguridad(idEmpleado,tablaAfectada,accion,idRegistro,idRolAnterior,idPermiso,detalle)
 SELECT dbo.fn_EmpleadoBitacora(NULL),N'TblRolesPermisos','DELETE',idRol,idRol,idPermiso,N'Retiro por UPDATE'
 FROM (SELECT idRol,idPermiso FROM deleted EXCEPT SELECT idRol,idPermiso FROM inserted) d;
 INSERT dbo.TblAuditoriaSeguridad(idEmpleado,tablaAfectada,accion,idRegistro,idRolNuevo,idPermiso,detalle)
 SELECT dbo.fn_EmpleadoBitacora(NULL),N'TblRolesPermisos','INSERT',idRol,idRol,idPermiso,N'Asignación por UPDATE'
 FROM (SELECT idRol,idPermiso FROM inserted EXCEPT SELECT idRol,idPermiso FROM deleted) i;
END;
GO

CREATE OR ALTER PROCEDURE [dbo].[pa_RegistrarEventoSesion]
    @pEvento      VARCHAR(20),
    @pCorreo      VARCHAR(120),
    @pIdUsuario   INT          = NULL,
    @pDireccionIp VARCHAR(45)  = NULL,
    @pNavegador   VARCHAR(200) = NULL
AS
BEGIN
    SET NOCOUNT ON;

    IF @pEvento IS NULL OR @pEvento NOT IN ('LOGIN_OK', 'LOGIN_FALLIDO', 'LOGOUT')
    BEGIN
        RAISERROR('El evento de sesión no es válido.', 16, 1);
        RETURN;
    END;

    INSERT INTO [dbo].[TblAuditoriaSesiones]
        (evento, correo, idUsuario, idEmpleado, direccionIp, navegador)
    SELECT @pEvento,
           LEFT(ISNULL(@pCorreo, ''), 120),
           @pIdUsuario,
           (SELECT u.idEmpleado FROM dbo.TblUsuarios AS u WHERE u.idUsuario = @pIdUsuario),
           LEFT(@pDireccionIp, 45),
           LEFT(@pNavegador, 200);
END
GO

CREATE OR ALTER TRIGGER [dbo].[trg_ProtegerHistorialProductos]
ON [dbo].[TblHistorialProductos]
INSTEAD OF UPDATE, DELETE
AS
BEGIN
    THROW 51000, N'Los registros de auditoría no se pueden modificar ni eliminar.', 1;
END
GO

CREATE OR ALTER TRIGGER [dbo].[trg_ProtegerHistorialReservaciones]
ON [dbo].[TblHistorialReservaciones]
INSTEAD OF UPDATE, DELETE
AS
BEGIN
    THROW 51000, N'Los registros de auditoría no se pueden modificar ni eliminar.', 1;
END
GO

CREATE OR ALTER TRIGGER [dbo].[trg_ProtegerHistorialDetalleTicket]
ON [dbo].[TblHistorialDetalleTicket]
INSTEAD OF UPDATE, DELETE
AS
BEGIN
    THROW 51000, N'Los registros de auditoría no se pueden modificar ni eliminar.', 1;
END
GO

CREATE OR ALTER TRIGGER [dbo].[trg_ProtegerAuditoriaCaja]
ON [dbo].[TblAuditoriaCaja]
INSTEAD OF UPDATE, DELETE
AS
BEGIN
    THROW 51000, N'Los registros de auditoría no se pueden modificar ni eliminar.', 1;
END
GO

CREATE OR ALTER TRIGGER [dbo].[trg_ProtegerAuditoriaSeguridad]
ON [dbo].[TblAuditoriaSeguridad]
INSTEAD OF UPDATE, DELETE
AS
BEGIN
    THROW 51000, N'Los registros de auditoría no se pueden modificar ni eliminar.', 1;
END
GO

CREATE OR ALTER TRIGGER [dbo].[trg_ProtegerAuditoriaSesiones]
ON [dbo].[TblAuditoriaSesiones]
INSTEAD OF UPDATE, DELETE
AS
BEGIN
    THROW 51000, N'Los registros de auditoría no se pueden modificar ni eliminar.', 1;
END
GO

CREATE OR ALTER VIEW [dbo].[vIntentosFallidosRecientes]
AS
SELECT correo,
       COUNT(*)       AS intentosFallidos,
       MIN(fechaHora) AS primerIntento,
       MAX(fechaHora) AS ultimoIntento
FROM dbo.TblAuditoriaSesiones
WHERE evento = 'LOGIN_FALLIDO'
  AND fechaHora >= DATEADD(HOUR, -24, SYSDATETIME())
GROUP BY correo;
GO

CREATE OR ALTER VIEW dbo.vAuditoriaGeneral AS
SELECT N'TblHistorialProductos' AS origen, idHistorialProducto AS idAuditoria, CAST(fechaCambio AS datetime2(3)) AS fechaHora, idEmpleado, CAST(accion AS varchar(40)) AS operacion, CAST(N'TblProductos' AS nvarchar(128)) AS tablaAfectada, idProducto AS idRegistro, usuarioBD FROM dbo.TblHistorialProductos
UNION ALL
SELECT N'TblHistorialReservaciones' AS origen, idHistorialReservacion AS idAuditoria, CAST(fechaCambio AS datetime2(3)) AS fechaHora, idEmpleado, CAST(accion AS varchar(40)) AS operacion, CAST(N'TblReservaciones' AS nvarchar(128)) AS tablaAfectada, idReservacion AS idRegistro, usuarioBD FROM dbo.TblHistorialReservaciones
UNION ALL
SELECT N'TblHistorialDetalleTicket' AS origen, idHistorialDetalle AS idAuditoria, CAST(fechaCambio AS datetime2(3)) AS fechaHora, idEmpleado, CAST(accion AS varchar(40)) AS operacion, CAST(N'TblDetalleTicket' AS nvarchar(128)) AS tablaAfectada, idDetalle AS idRegistro, usuarioBD FROM dbo.TblHistorialDetalleTicket
UNION ALL
SELECT N'TblAuditoriaCaja' AS origen, idAuditoriaCaja AS idAuditoria, CAST(fechaHora AS datetime2(3)) AS fechaHora, idEmpleado, CAST(accion AS varchar(40)) AS operacion, CAST(tablaAfectada AS nvarchar(128)) AS tablaAfectada, idRegistro AS idRegistro, usuarioBD FROM dbo.TblAuditoriaCaja
UNION ALL
SELECT N'TblAuditoriaSeguridad' AS origen, idAuditoriaSeguridad AS idAuditoria, CAST(fechaHora AS datetime2(3)) AS fechaHora, idEmpleado, CAST(accion AS varchar(40)) AS operacion, CAST(tablaAfectada AS nvarchar(128)) AS tablaAfectada, idRegistro AS idRegistro, usuarioBD FROM dbo.TblAuditoriaSeguridad
UNION ALL
SELECT N'TblAuditoriaSesiones' AS origen, idAuditoriaSesion AS idAuditoria, CAST(fechaHora AS datetime2(3)) AS fechaHora, idEmpleado, CAST(evento AS varchar(40)) AS operacion, CAST(N'SesionesAplicacion' AS nvarchar(128)) AS tablaAfectada, idUsuario AS idRegistro, usuarioBD FROM dbo.TblAuditoriaSesiones;
GO

IF OBJECT_ID(N'dbo.TblHistorialRespaldos', N'U') IS NULL
    CREATE TABLE [dbo].[TblHistorialRespaldos] (
        [idRespaldo]   INT IDENTITY(1, 1) NOT NULL,
        [fechaInicio]  DATETIME2(3)   NOT NULL,
        [fechaFin]     DATETIME2(3)   NOT NULL CONSTRAINT [DF_TblHistorialRespaldos_fechaFin] DEFAULT (SYSDATETIME()),
        [tipo]         VARCHAR(12)    NOT NULL,
        [estado]       VARCHAR(10)    NOT NULL,
        [archivo]      NVARCHAR(400)  NOT NULL,
        [tamanoBytes]  BIGINT         NULL,
        [verificado]   BIT            NOT NULL CONSTRAINT [DF_TblHistorialRespaldos_verificado] DEFAULT (0),
        [descripcion]  NVARCHAR(200)  NULL,
        [mensaje]      NVARCHAR(2048) NULL,
        [idEmpleado]   INT            NOT NULL,
        [usuarioBD]   NVARCHAR(128) NULL CONSTRAINT [DF_TblHistorialRespaldos_usuarioBD]  DEFAULT (SUSER_SNAME()),
        [equipo]      NVARCHAR(128) NULL CONSTRAINT [DF_TblHistorialRespaldos_equipo]     DEFAULT (HOST_NAME()),
        [aplicacion]  NVARCHAR(128) NULL CONSTRAINT [DF_TblHistorialRespaldos_aplicacion] DEFAULT (APP_NAME()),
        CONSTRAINT [PK_TblHistorialRespaldos] PRIMARY KEY CLUSTERED ([idRespaldo]),
        CONSTRAINT [CK_TblHistorialRespaldos_tipo]   CHECK ([tipo] IN ('COMPLETO', 'DIFERENCIAL', 'LOG')),
        CONSTRAINT [CK_TblHistorialRespaldos_estado] CHECK ([estado] IN ('EXITOSO', 'FALLIDO'))
    );

GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'idx_TblHistorialRespaldos_fecha')
    CREATE NONCLUSTERED INDEX [idx_TblHistorialRespaldos_fecha] ON [dbo].[TblHistorialRespaldos] ([fechaInicio]);

GO

CREATE OR ALTER VIEW [dbo].[vHistorialRespaldos]
AS
SELECT r.idRespaldo,
       r.fechaInicio,
       r.fechaFin,
       DATEDIFF(MILLISECOND, r.fechaInicio, r.fechaFin) / 1000.0 AS duracionSegundos,
       r.tipo,
       r.estado,
       r.archivo,
       r.tamanoBytes,
       CAST(r.tamanoBytes / 1048576.0 AS DECIMAL(12, 2)) AS tamanoMB,
       r.verificado,
       r.descripcion,
       r.mensaje,
       r.idEmpleado,
       e.nombre AS empleado,
       r.usuarioBD,
       r.equipo
FROM dbo.TblHistorialRespaldos AS r
LEFT JOIN dbo.TblEmpleados AS e ON e.idEmpleado = r.idEmpleado;

GO

CREATE OR ALTER TRIGGER [dbo].[trg_ProtegerHistorialRespaldos]
ON [dbo].[TblHistorialRespaldos]
INSTEAD OF UPDATE, DELETE
AS
BEGIN
    THROW 51000, N'Los registros de auditoría no se pueden modificar ni eliminar.', 1;
END

GO
CREATE OR ALTER TRIGGER [trg_AuditoriaDDL]
ON DATABASE
FOR DDL_TABLE_EVENTS, DDL_TRIGGER_EVENTS, DDL_PROCEDURE_EVENTS,
    DDL_FUNCTION_EVENTS, DDL_VIEW_EVENTS
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @evento XML = EVENTDATA();
    INSERT INTO [dbo].[TblAuditoriaSeguridad] (idEmpleado, tablaAfectada, accion, detalle)
    VALUES (
        dbo.fn_EmpleadoBitacora(NULL),
        ISNULL(@evento.value('(/EVENT_INSTANCE/ObjectName)[1]', 'NVARCHAR(128)'), N'(base de datos)'),
        @evento.value('(/EVENT_INSTANCE/EventType)[1]', 'VARCHAR(40)'),
        @evento.value('(/EVENT_INSTANCE/TSQLCommand/CommandText)[1]', 'NVARCHAR(MAX)')
    );
END
GO
