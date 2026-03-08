INSERT INTO role (id, name) VALUES
(1, 'admin'),
(2, 'user'),
(3, 'supervisor');

INSERT INTO scope (id, name) VALUES
(1, 'user.read'),
(2, 'user.write'),
(3, 'role.read'),
(4, 'role.write'),
(5, 'product.read'),
(6, 'product.write');

-- Rol admin ⇒ tiene todos los permisos
INSERT INTO role_scope (role_id, scope_id)
SELECT 1, id FROM scope;

-- Rol user ⇒ permisos típicos:

INSERT INTO role_scope (role_id, scope_id) VALUES
(2, 1),   -- user.read
(2, 5);   -- product.read

-- Rol supervisor ⇒ permisos intermedios:
INSERT INTO role_scope (role_id, scope_id) VALUES
(3, 1),  -- user.read
(3, 5),  -- product.read
(3, 6);  -- product.write

commit;

