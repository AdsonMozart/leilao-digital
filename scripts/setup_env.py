"""Cria credenciais locais sem exibi-las nem substituir um .env existente."""

from pathlib import Path
import secrets


def main():
    project_dir = Path(__file__).resolve().parent.parent
    env_path = project_dir / ".env"
    if env_path.exists():
        print("O arquivo .env ja existe. Credenciais preservadas.")
        return

    contents = (project_dir / ".env.example").read_text(encoding="utf-8")
    secret_names = {
        "MYSQL_PASSWORD",
        "MYSQL_ROOT_PASSWORD",
        "DJANGO_SECRET_KEY",
        "AUDIT_HMAC_KEY",
    }
    lines = []
    for line in contents.splitlines():
        name, separator, _ = line.partition("=")
        if separator and name in secret_names:
            line = f"{name}={secrets.token_urlsafe(48)}"
        lines.append(line)

    # Modo x impede sobrescrita, mesmo se outra execucao criar o arquivo.
    with env_path.open("x", encoding="utf-8", newline="\n") as env_file:
        env_file.write("\n".join(lines) + "\n")
    print("Arquivo .env criado com senhas e chaves independentes.")
    print("Os valores nao foram exibidos. Nao versione nem compartilhe o .env.")


if __name__ == "__main__":
    main()
