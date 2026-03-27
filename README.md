# Sample MCP Server - Skills & Documents

Este é um servidor MCP (Model Context Protocol) construído em Python utilizando a biblioteca **FastMCP**. O objetivo deste servidor é fornecer ferramentas (skills) personalizadas por usuário e funcionalidades robustas para extração, armazenamento e busca de documentos.

A arquitetura do projeto segue princípios de **Clean Architecture**, isolando as lógicas de Repositório (`repositories`), Serviço (`services`) e Exposição MCP (`mcp_tools`).

## 🚀 Funcionalidades Principais

- **Skill Management:**
  - `register_skill`: Registra uma nova habilidade/instrução em texto para um usuário específico.
  - `read_skill`: Lê uma habilidade salva.
  - `list_skills`: Lista todas as habilidades salvas de um usuário.

- **Document Management:**
  - `download_document`: Faz download de um documento de uma URL e salva localmente. Suporta download nativo diretamente do **Google Drive** usando validação via Token.
  - `save_base64_document`: Permite enviar um arquivo em base64 (como PDFs e imagens) e salvá-lo de forma segura e encapsulada.
  - `list_recent_documents`: Busca documentos que foram criados ou atualizados em uma janela definida (limite N minutos atrás).
  - `search_documents`: Procura todos os documentos de um usuário utilizando buscas com padrões no nome.

## 🛠️ Tecnologias Utilizadas
- **Python 3.11+**
- **FastMCP**
- **uv** (para gerenciamento ultrarrápido de pacotes)
- **Pytest** (cobertura total do código validada agressivamente >90%)
- **Terraform**, **Docker**, e **Google Artifact Registry / Cloud Run** com **GCS FUSE** para armazenamento de informações persistentes (`skills/` e `docs/`).

---

## 💻 Como rodar LOCALMENTE

Para executar o sistema localmente na sua máquina para testes ou integração com clientes MCP:

1. **Instalando o `uv`**
   Certifique-se de que possua a ferramenta [uv](https://github.com/astral-sh/uv) instalada.

2. **Configurando as Variáveis de Ambiente**
   Crie um arquivo `.env` na raiz do projeto (ou adicione as variáveis no seu terminal):
   ```bash
   PATH_SKILLS="./data/skills"
   PATH_DOCS="./data/docs"
   ```

3. **Iniciando o Servidor MCP**
   Inicie o servidor para se comunicar com clientes MCP pelo terminal (`stdio`):
   ```bash
   uv run sample-mcp-server-skills
   ```
   *Ou manualmente pelo módulo Python:*
   ```bash
   uv run python -m src.main
   ```

4. **Rodando os Testes Unitários**
   Para rodar a suíte completa de testes (mockando requests do Google e do filesystem) e inspecionar os relatórios de cobertura:
   ```bash
   uv run pytest --cov=src --cov-report=term-missing tests/test_*.py
   ```

---

## ☁️ Como rodar na NUVEM (Google Cloud Run)

Este projeto já está inteiramente preparado para ser conteinerizado via Docker e subir sem fricções para o GCP Cloud Run de forma automatizada pelo **Terraform**. A persistência de dados das skills e documentos fica garantida mesmo quando os containers da núvem morrem e renascem graças à montagem direta do Bucket integrado do Cloud Storage FUSE.

### Pré-requisitos Cloud
- É preciso ter a CLI do Google Cloud (`gcloud`) instalada e autenticada com sua conta.
- O **Terraform CLI** precisa de disponibilidade no seu Path de desenvolvedor.

### 1. Verificando os Parâmetros (Opcional)
Se precisar, entre no arquivo em `terraform/variables.tf` e nos scripts shell e confira os parâmetros (como nome do projeto `tutto-assistants`, a tag pretendida, etc).

### 2. Build da Imagem Oficial
Realize o upload/build seguro da aplicação utilizando o Cloud Build:
```bash
# Isso subirá a imagem e depositará na sua Registry associada
./build.sh latest
```

### 3. Provisionamento as-code
O nosso shell script executa os comandos base do Terraform lidando ativamente com os environments:

```bash
# Aplica toda a construção no GCP 
./terraform.sh apply
```

O GCP provisionará a sua imagem perfeitamente envelopada em um container acessível publicamente via HTTP!
Para limpar a infraestrutura por completo depois, basta utilizar o mesmo script:
```bash
./terraform.sh destroy <sua_area>
```
