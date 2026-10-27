"""Verifica conexao e configuracao do MySQL sem ler ou exibir senhas."""

from pathlib import Path
import subprocess
import sys


def main():
    query = """
        SELECT DATABASE(), CURRENT_USER(), VERSION(),
               @@character_set_database, @@default_storage_engine,
               @@session.time_zone, @@session.transaction_isolation,
               @@session.sql_mode;
    """
    command = [
        "docker", "compose", "exec", "-T", "db", "sh", "-c",
        'MYSQL_PWD="$MYSQL_PASSWORD" exec mysql --protocol=TCP '
        '--host=127.0.0.1 --user="$MYSQL_USER" --database="$MYSQL_DATABASE" '
        '--batch --skip-column-names',
    ]
    try:
        result = subprocess.run(
            command,
            cwd=Path(__file__).resolve().parent.parent,
            input=query,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print("Nao foi possivel executar a verificacao. Confira o Docker Desktop.")
        return 1
    if result.returncode:
        print("Falha na conexao. Confira Docker Desktop e docker compose ps.")
        print(result.stderr.strip())
        return 1

    fields = result.stdout.strip().split("\t")
    if len(fields) != 8:
        print("Resposta inesperada do MySQL.")
        return 1
    database, user, version, charset, engine, timezone, isolation, sql_mode = fields
    checks = {
        "Banco selecionado": bool(database) and database != "NULL",
        "Usuario de aplicacao (sem root)": not user.startswith("root@"),
        "MySQL 8.4": version.startswith("8.4."),
        "Unicode utf8mb4": charset == "utf8mb4",
        "Transacoes InnoDB": engine.upper() == "INNODB",
        "Horario UTC": timezone == "+00:00",
        "Isolamento READ-COMMITTED": isolation == "READ-COMMITTED",
        "Modo SQL estrito": bool(
            {"STRICT_TRANS_TABLES", "STRICT_ALL_TABLES"} & set(sql_mode.split(","))
        ),
    }
    for description, passed in checks.items():
        print(f"{'OK' if passed else 'FALHOU'}: {description}")
    print(f"Versao do servidor: {version}")
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
