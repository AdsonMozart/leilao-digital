**Etapa 1 — Ambiente de desenvolvimento**

Objetivo: iniciar um MySQL persistente com usuario de aplicacao e credenciais locais protegidas. A etapa termina quando o Compose estiver valido e o banco responder a verificacao. Django e Next.js entram nas etapas seguintes, para explicar cada parte separadamente.

**Ferramentas encontradas**

Git 2.53.0, Python 3.14.6 e 3.12, Node.js 24.18.0, npm 11.16.0, Docker CLI 29.2.0 e Compose 5.0.2. O Docker Desktop precisa estar aberto no modo de containers Linux. Nao e necessario instalar MySQL diretamente no Windows.

No PowerShell, utilize `npm.cmd`: o comando `npm` pode selecionar um arquivo `.ps1` bloqueado pela politica de execucao. Nao e necessario alterar essa politica. Os scripts desta etapa usam apenas a biblioteca padrao do Python. A versao de Python para executar Django sera fixada na proxima etapa, considerando as dependencias; o escopo sugere 3.13, mas esta maquina possui 3.12 e 3.14.

**Passo 1: criar configuracao local**

No PowerShell, na raiz do projeto:

```powershell
Set-Location E:\Projetos\leilao-digital
python scripts/setup_env.py
```

O script copia o contrato de `.env.example`, gera senhas e chaves diferentes e grava `.env` sem mostrar os valores. Se o arquivo ja existir, preserva seu conteudo. Ele nao cria o banco nem troca senhas de um banco existente.

`.env.example` pode ir ao Git; `.env` nunca. `.gitignore` protege o versionamento e `.dockerignore` impede copiar segredos para o contexto de build. A chave Django e a chave de auditoria ja sao geradas para as proximas etapas, mas o container MySQL recebe somente as variaveis do banco.

**Passo 2: validar e iniciar o banco**

```powershell
docker compose config --quiet
docker compose up -d --wait db
docker compose ps
python scripts/check_database.py
```

`config --quiet` valida sem imprimir a configuracao com senhas. `up -d` inicia em segundo plano; `--wait` aguarda o healthcheck. A primeira execucao baixa a imagem e inicializa os dados, por isso pode demorar. A verificacao deve mostrar todos os itens como `OK`.

O healthcheck testa uma consulta autenticada por TCP com o usuario de aplicacao. Isso confirma que o banco terminou a inicializacao e aceita consultas, em vez de verificar somente a existencia do processo. [Inicializacao de servicos no Compose](https://docs.docker.com/compose/how-tos/startup-order/).

**Entendendo compose.yaml**

| Configuracao | Finalidade |
|---|---|
| `image: mysql:8.4@sha256:...` | MySQL 8.4.13 validado e fixado por digest, identificador imutavel da imagem baixada |
| `MYSQL_DATABASE` | Nome do banco criado na primeira inicializacao |
| `MYSQL_USER` / `MYSQL_PASSWORD` | Credenciais da aplicacao, sem usar root |
| `MYSQL_ROOT_PASSWORD` | Senha administrativa independente; o backend nao recebera essa senha |
| `127.0.0.1:3307:3306` | Porta 3307 acessivel somente no proprio computador, encaminhada a porta 3306 do container |
| `mysql_data` | Volume que mantem os dados quando o container e recriado |
| `utf8mb4` | Armazenamento de caracteres Unicode |
| `InnoDB` | Suporte a transacoes e bloqueios exigidos pelos lances |
| `+00:00` | Horario UTC no banco |
| `READ-COMMITTED` | Nivel de isolamento a ser usado pela aplicacao |

O Compose le `.env` para substituir `${VAR}`. No healthcheck, `$${VAR}` adia a expansao ate o comando executar dentro do container. As senhas nao ficam escritas no YAML. Variaveis de ambiente sao visiveis a quem administra o Docker; `.env` nao e criptografia nem um cofre de segredos.

A imagem oficial cria banco e usuario quando inicializa um diretorio de dados vazio. Alterar `.env` depois disso nao modifica automaticamente as credenciais persistidas. Nao apague o volume para tentar corrigir senha. [Imagem oficial do MySQL](https://hub.docker.com/_/mysql).

**Passo 3: conectar pelo cliente SQL, se desejar**

Pode usar um cliente que ja possua, como MySQL Workbench ou DBeaver:

| Campo | Valor |
|---|---|
| Host | `127.0.0.1` |
| Porta | `3307`, ou o valor de `MYSQL_PORT` |
| Banco | `leilao_digital` |
| Usuario | `leilao_app` |
| Senha | Valor de `MYSQL_PASSWORD` no seu `.env`, consultado somente localmente |

Nao envie a senha pelo chat. Dentro de futuros containers do projeto, Django usara host `db` e porta `3306`; `localhost` dentro de um container aponta para ele mesmo.

**Uso diario e problemas comuns**

```powershell
# Parar o banco, preservando os dados.
docker compose stop db

# Iniciar e aguardar ficar saudavel novamente.
docker compose up -d --wait db

# Remover containers e rede, preservando o volume de dados.
docker compose down
```

Nao adicione `-v` ao comando `down`: isso remove o volume e seus dados. Reiniciar containers nao equivale a backup.

Se o Docker nao conectar, abra o Docker Desktop e aguarde o engine Linux iniciar. Se a porta 3307 estiver ocupada, ajuste somente `MYSQL_PORT` no `.env` e recrie o servico. Se a autenticacao falhar depois de editar senhas, lembre-se de que o volume conserva as credenciais anteriores. Em caso de falha de inicializacao, examine `docker compose logs --tail 60 db` localmente, removendo qualquer dado sensivel antes de compartilhar logs.

**Passo 4: versionar o marco validado**

O repositorio sera inicializado com a branch `main`, sem criar commits automaticamente. Confira primeiro o que vai entrar:

```powershell
git status --short
git check-ignore .env
```

Para manter dois commits claros, comece pelo escopo:

```powershell
git add docs/ESCOPO.md
git diff --cached --stat
git commit -m "docs(scope): define requisitos e plano de entrega"
```

Depois versione o ambiente:

```powershell
git add .gitignore .dockerignore .editorconfig .gitattributes .env.example compose.yaml scripts/setup_env.py scripts/check_database.py README.md docs/ETAPAS.md docs/AMBIENTE.md
git diff --cached
git commit -m "chore(env): configura ambiente local e MySQL com Docker"
```

Revisar o diff e parte do trabalho: `.env` nao pode aparecer entre os arquivos preparados. A conexao ao GitHub sera feita com o endereco real do seu repositorio, sem inventar um remote.

**Criterios de aceite**

- [x] Docker Desktop funcionando com containers Linux.
- [x] `.env` gerado e ignorado pelo Git.
- [x] Compose validado sem exibir segredos.
- [x] MySQL com estado `healthy`.
- [x] Verificacao de conexao/configuracao aprovada.
- [x] Imagem validada fixada por digest.
- [ ] Commits revisados e realizados pelo candidato.

Validacao local em 24/10/2026: MySQL 8.4.13 saudavel; conexao pelo usuario de aplicacao, Unicode, InnoDB, UTC, READ-COMMITTED e modo estrito aprovados. Reexecutar o gerador de ambiente preservou todas as credenciais existentes.
