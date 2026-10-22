-- Aplique UMA vez no banco existente (Supabase > SQL Editor).
-- O create_all do SQLAlchemy não altera tabelas que já existem.

ALTER TABLE pescador ADD COLUMN IF NOT EXISTS senha_hash VARCHAR(255);

-- Se esta linha falhar, há e-mails duplicados: corrija-os antes.
-- Consulta para achar: SELECT email, count(*) FROM pescador GROUP BY email HAVING count(*) > 1;
CREATE UNIQUE INDEX IF NOT EXISTS ix_pescador_email ON pescador (email);
