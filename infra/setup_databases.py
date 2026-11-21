"""Cria, no PostgreSQL da Azure, um banco e um usuário para cada ambiente (dev e prod).

Cada ambiente usa o próprio usuário, dono só do próprio banco: a API de dev não consegue ler os dados de prod.
O administrador do servidor serve só para este script. Rodar de novo não apaga nada; só atualiza as senhas.

Uso (precisa de uma regra de firewall liberando o seu IP enquanto roda):
  python infra/setup_databases.py <host> <senha-admin> <senha-dev> <senha-prod>
As senhas vêm de argumentos para não ficarem gravadas em arquivo do repositório.
"""
import sys

import psycopg2
from psycopg2 import sql

ADMIN_USER = "talentixadmin"
ENVIRONMENTS = ("dev", "prod")


def connect(host: str, password: str, database: str = "postgres"):
  return psycopg2.connect(host=host, user=ADMIN_USER, password=password, dbname=database, sslmode="require")


def main(host: str, admin_password: str, passwords: dict[str, str]) -> None:
  admin = connect(host, admin_password)
  # CREATE DATABASE não roda dentro de transação.
  admin.autocommit = True
  with admin.cursor() as cursor:
    for env in ENVIRONMENTS:
      role, database = f"talentix_{env}", f"talentix_{env}"
      cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (role,))
      action = "ALTER" if cursor.fetchone() else "CREATE"
      cursor.execute(sql.SQL(action + " ROLE {} WITH LOGIN PASSWORD %s").format(sql.Identifier(role)), (passwords[env],))
      # O administrador precisa ser membro do papel para criar um banco cujo dono é ele.
      cursor.execute(sql.SQL("GRANT {} TO {}").format(sql.Identifier(role), sql.Identifier(ADMIN_USER)))
      cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (database,))
      if not cursor.fetchone():
        cursor.execute(sql.SQL("CREATE DATABASE {} OWNER {}").format(sql.Identifier(database), sql.Identifier(role)))
      # Ninguém além do dono (e do administrador) se conecta ao banco do ambiente.
      cursor.execute(sql.SQL("REVOKE ALL ON DATABASE {} FROM PUBLIC").format(sql.Identifier(database)))
      print(f"{env}: usuário {role} e banco {database} prontos")
  admin.close()

  for env in ENVIRONMENTS:
    database = f"talentix_{env}"
    conn = connect(host, admin_password, database)
    conn.autocommit = True
    with conn.cursor() as cursor:
      # Só o dono cria tabelas no schema public (padrão do PostgreSQL 15+, garantido aqui).
      cursor.execute(sql.SQL("ALTER SCHEMA public OWNER TO {}").format(sql.Identifier(f"talentix_{env}")))
      cursor.execute("REVOKE CREATE ON SCHEMA public FROM PUBLIC")
    conn.close()


if __name__ == "__main__":
  if len(sys.argv) != 5:
    sys.exit(__doc__)
  main(sys.argv[1], sys.argv[2], {"dev": sys.argv[3], "prod": sys.argv[4]})
