-- =============================================================================
-- MySQL DDL: users, roles, scope, user_role, role_scope
-- =============================================================================
-- Recomendado ejecutar con un usuario con permisos de DDL
-- Ajusta el nombre del schema si lo necesitas (USE my_database;)
-- =============================================================================

-- Opcional: asegurar el modo seguro de FK durante la creación
SET FOREIGN_KEY_CHECKS = 0;

-- -----------------------------------------------------------------------------
-- Limpieza previa (DROP IF EXISTS)
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS `role_scope`;
DROP TABLE IF EXISTS `user_role`;
DROP TABLE IF EXISTS `scope`;
DROP TABLE IF EXISTS `role`;
DROP TABLE IF EXISTS `users`;

-- -----------------------------------------------------------------------------
-- Tabla: user
-- -----------------------------------------------------------------------------
CREATE TABLE `user` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(100) NOT NULL,
  `email` VARCHAR(320) NOT NULL,
  `password_hash` VARCHAR(255) NOT NULL,
  `isActive` TINYINT(1) NOT NULL DEFAULT 1,
  `retryCount` INT NOT NULL DEFAULT 0,
  `fullName` VARCHAR(200) NULL,
  `phone` VARCHAR(50) NULL,
  `lastLogin_at` TIMESTAMP NULL DEFAULT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_user_username` (`username`),
  UNIQUE KEY `uq_user_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- Tabla: role
-- -----------------------------------------------------------------------------
CREATE TABLE `role` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(100) NOT NULL,
  `description` VARCHAR(500) NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_role_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- Tabla: scope
-- -----------------------------------------------------------------------------
CREATE TABLE `scope` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(150) NOT NULL,
  `description` VARCHAR(500) NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_scope_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- Tabla: user_role (tabla de unión N:M entre users y role)
-- Clave primaria compuesta (user_id, role_id) como has indicado
-- -----------------------------------------------------------------------------
CREATE TABLE `user_role` (
  `user_id` INT UNSIGNED NOT NULL,
  `role_id` INT UNSIGNED NOT NULL,
  `assigned_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `assigned_by` VARCHAR(100) NULL,
  PRIMARY KEY (`user_id`, `role_id`),
  KEY `ix_user_role_role_id` (`role_id`),
  CONSTRAINT `fk_user_role_user` FOREIGN KEY (`user_id`)
    REFERENCES `user` (`id`)
    ON UPDATE CASCADE
    ON DELETE CASCADE,
  CONSTRAINT `fk_user_role_role` FOREIGN KEY (`role_id`)
    REFERENCES `role` (`id`)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- Tabla: role_scope (tabla de unión N:M entre roles y scope)
-- Clave primaria compuesta (role_id, scope_id) como has indicado
-- -----------------------------------------------------------------------------
CREATE TABLE `role_scope` (
  `role_id` INT UNSIGNED NOT NULL,
  `scope_id` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`role_id`, `scope_id`),
  KEY `ix_role_scope_scope_id` (`scope_id`),
  CONSTRAINT `fk_role_scope_role` FOREIGN KEY (`role_id`)
    REFERENCES `role` (`id`)
    ON UPDATE CASCADE
    ON DELETE CASCADE,
  CONSTRAINT `fk_role_scope_scope` FOREIGN KEY (`scope_id`)
    REFERENCES `scope` (`id`)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Restaurar comprobaciones de FK
SET FOREIGN_KEY_CHECKS = 1;