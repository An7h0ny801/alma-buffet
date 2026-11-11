SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

CREATE OR ALTER PROCEDURE [dbo].[pa_RespaldarBase]
    @pTipo        VARCHAR(12)   = 'COMPLETO',
    @pDescripcion NVARCHAR(200) = NULL,
    @pVerificar   BIT           = 1
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @vBase        SYSNAME       = DB_NAME();
    DECLARE @vInicio      DATETIME2(3)  = SYSDATETIME();
    DECLARE @vEstado      VARCHAR(10)   = 'EXITOSO';
    DECLARE @vVerificado  BIT           = 0;
    DECLARE @vPaso        NVARCHAR(40)  = N'generar el respaldo';
    DECLARE @vCarpeta     NVARCHAR(260) = CAST(SERVERPROPERTY('InstanceDefaultBackupPath') AS NVARCHAR(260));
    DECLARE @vHayCompleto BIT           = 0;
    DECLARE @vArchivo     NVARCHAR(400);
    DECLARE @vNombreSet   NVARCHAR(128);
    DECLARE @vTamano      BIGINT;
    DECLARE @vMensaje     NVARCHAR(2048);
    DECLARE @vSql         NVARCHAR(MAX);
    DECLARE @vSeparador   NCHAR(1);

    SET @pTipo = UPPER(LTRIM(RTRIM(ISNULL(@pTipo, ''))));
    SET @pDescripcion = NULLIF(LTRIM(RTRIM(@pDescripcion)), N'');

    IF CAST(SERVERPROPERTY('EngineEdition') AS INT) = 5
        THROW 51014, N'En Azure SQL Database los respaldos son automáticos y se administran desde el portal de Azure.', 1;

    IF @pTipo NOT IN ('COMPLETO', 'DIFERENCIAL', 'LOG')
        THROW 51010, N'El tipo de respaldo no es válido: use COMPLETO, DIFERENCIAL o LOG.', 1;

    IF @@TRANCOUNT > 0
        THROW 51011, N'El respaldo no se puede ejecutar dentro de una transacción.', 1;

    IF @pTipo = 'LOG'
       AND (SELECT recovery_model_desc FROM sys.databases WHERE name = @vBase) = N'SIMPLE'
        THROW 51012, N'La base usa el modelo de recuperación SIMPLE, que no admite respaldos del log.', 1;

    IF @pTipo IN ('DIFERENCIAL', 'LOG')
    BEGIN
        EXEC sys.sp_executesql
             N'SELECT @pHay = CASE WHEN EXISTS (SELECT 1 FROM msdb.dbo.backupset WHERE database_name = @pBase AND type = ''D'') THEN 1 ELSE 0 END;',
             N'@pBase SYSNAME, @pHay BIT OUTPUT',
             @pBase = @vBase, @pHay = @vHayCompleto OUTPUT;
        IF @vHayCompleto = 0
            THROW 51013, N'Primero debe generar un respaldo COMPLETO de la base.', 1;
    END;

    IF @vCarpeta IS NULL
        THROW 51015, N'SQL Server no tiene configurada una carpeta predeterminada de respaldos.', 1;

    SET @vSeparador = CASE WHEN CHARINDEX(N'/', @vCarpeta) > 0 THEN N'/' ELSE N'\' END;
    IF RIGHT(@vCarpeta, 1) NOT IN (N'\', N'/')
        SET @vCarpeta += @vSeparador;

    SET @vArchivo = @vCarpeta + @vBase + N'_' + @pTipo + N'_'
                  + FORMAT(@vInicio, N'yyyyMMdd_HHmmssfff')
                  + CASE WHEN @pTipo = 'LOG' THEN N'.trn' ELSE N'.bak' END;
    SET @vNombreSet = LEFT(N'Alma Buffet - respaldo ' + LOWER(@pTipo) + N' ' + FORMAT(@vInicio, N'yyyy-MM-dd HH:mm'), 128);

    SET @vSql = CASE WHEN @pTipo = 'LOG' THEN N'BACKUP LOG ' ELSE N'BACKUP DATABASE ' END
              + QUOTENAME(@vBase) + N' TO DISK = @pArchivo WITH CHECKSUM, INIT, NAME = @pNombre, DESCRIPTION = @pDescripcion'
              + CASE WHEN @pTipo = 'DIFERENCIAL' THEN N', DIFFERENTIAL' ELSE N'' END
              + CASE WHEN CAST(SERVERPROPERTY('EngineEdition') AS INT) = 4 THEN N'' ELSE N', COMPRESSION' END
              + N';';

    BEGIN TRY
        EXEC sys.sp_executesql @vSql,
             N'@pArchivo NVARCHAR(400), @pNombre NVARCHAR(128), @pDescripcion NVARCHAR(255)',
             @pArchivo = @vArchivo, @pNombre = @vNombreSet, @pDescripcion = @pDescripcion;

        EXEC sys.sp_executesql
             N'SELECT TOP (1) @pTamano = bs.compressed_backup_size
               FROM msdb.dbo.backupset AS bs
               JOIN msdb.dbo.backupmediafamily AS mf ON mf.media_set_id = bs.media_set_id
               WHERE mf.physical_device_name = @pArchivo
               ORDER BY bs.backup_set_id DESC;',
             N'@pArchivo NVARCHAR(400), @pTamano BIGINT OUTPUT',
             @pArchivo = @vArchivo, @pTamano = @vTamano OUTPUT;

        IF @pVerificar = 1
        BEGIN
            SET @vPaso = N'verificar el respaldo';
            EXEC sys.sp_executesql N'RESTORE VERIFYONLY FROM DISK = @pArchivo WITH CHECKSUM;',
                 N'@pArchivo NVARCHAR(400)', @pArchivo = @vArchivo;
            SET @vVerificado = 1;
        END;

        SET @vMensaje = CASE WHEN @vVerificado = 1
                             THEN N'Respaldo generado y verificado correctamente.'
                             ELSE N'Respaldo generado (sin verificar).' END;
    END TRY
    BEGIN CATCH
        IF @vPaso = N'verificar el respaldo'
            SET @vMensaje = N'Respaldo generado, pero no se pudo verificar: ' + ERROR_MESSAGE();
        ELSE
        BEGIN
            SET @vEstado = 'FALLIDO';
            SET @vMensaje = N'No se pudo generar el respaldo: ' + ERROR_MESSAGE();
        END;
    END CATCH;

    INSERT INTO [dbo].[TblHistorialRespaldos]
        (fechaInicio, tipo, estado, archivo, tamanoBytes, verificado, descripcion, mensaje, idEmpleado)
    VALUES
        (@vInicio, @pTipo, @vEstado, @vArchivo, @vTamano, @vVerificado, @pDescripcion,
         LEFT(@vMensaje, 2048), dbo.fn_EmpleadoBitacora(NULL));

    SELECT idRespaldo, estado, archivo, tamanoBytes, verificado, mensaje
    FROM [dbo].[TblHistorialRespaldos]
    WHERE idRespaldo = SCOPE_IDENTITY();
END
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'idx_TblAuditoriaSesiones_correo' AND object_id = OBJECT_ID(N'dbo.TblAuditoriaSesiones'))
    CREATE NONCLUSTERED INDEX [idx_TblAuditoriaSesiones_correo]
        ON [dbo].[TblAuditoriaSesiones] ([correo], [evento], [fechaHora]);
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'idx_TblAuditoriaSesiones_direccionIp' AND object_id = OBJECT_ID(N'dbo.TblAuditoriaSesiones'))
    CREATE NONCLUSTERED INDEX [idx_TblAuditoriaSesiones_direccionIp]
        ON [dbo].[TblAuditoriaSesiones] ([direccionIp], [evento], [fechaHora]);
GO
