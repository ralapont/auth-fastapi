-- Crear base de datos si no existe
CREATE DATABASE IF NOT EXISTS auth_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- Crear usuario (si ya existe, puedes usar DROP USER primero)
CREATE USER IF NOT EXISTS 'auth_user'@'%' IDENTIFIED BY 'auth_pass';

-- Otorgar permisos para operar con tablas
GRANT ALL PRIVILEGES ON auth_db.* TO 'auth_user'@'%';
FLUSH PRIVILEGES;

-- Otorgar permisos necesarios sobre la base de datos
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, INDEX, REFERENCES
ON auth_db.*
TO 'auth_user'@'%';


-- Permiso para conectarse al servidor (incluido automáticamente con CREATE USER)
-- Pero si quieres ser explícito:
GRANT USAGE ON *.* TO 'auth_user'@'%';

-- Aplicar cambios
FLUSH PRIVILEGES;