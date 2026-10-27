**Leilao Digital — desafio Verzel**

Casa de leiloes com Python/Django, React/Next.js e MySQL. Desenvolvimento acompanhado por etapas; as funcionalidades de negocio ainda nao foram implementadas.

- [Escopo e regras](docs/ESCOPO.md)
- [Checklist de todas as etapas](docs/ETAPAS.md)
- [Guia didatico do ambiente](docs/AMBIENTE.md)

**Comecar pelo ambiente**

Com Git, Python e Docker Desktop instalados e o engine Linux iniciado, execute na raiz do projeto:

```powershell
python scripts/setup_env.py
docker compose config --quiet
docker compose up -d --wait db
python scripts/check_database.py
```

O script gera `.env` sem mostrar as credenciais e sem substituir arquivos existentes. O MySQL e publicado em `127.0.0.1:3307`, usa usuario de aplicacao separado do root e persiste dados em volume. Nao versione `.env` e nao use `docker compose down -v`, que remove os dados.

Nesta etapa somente o banco esta configurado. Django e Next.js serao adicionados nas proximas etapas. Consulte o guia de ambiente para os detalhes, acesso por cliente SQL e comandos de versionamento.
