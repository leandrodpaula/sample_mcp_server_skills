FROM python:3.11-slim

# Evitar gravação de bytecode e forçar log unbuffered
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Configurações do UV para o Docker
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

WORKDIR /app

# Instalar 'uv' utilizando o script oficial no path
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copiar arquivos de projeto
COPY pyproject.toml uv.lock ./

# Instalar dependências de forma gerenciada
RUN uv sync --frozen --no-cache

# Copiar a aplicação para dentro do contâiner
COPY src/ /app/src/

# Garantir que o módulo 'src' seja encontrado pelo Python
ENV PYTHONPATH=/app

# Variável usada no Google Cloud Run
ENV SERVER_PORT=8000
ENV MCP_TRANSPORT=http
ENV PATH_SKILLS=/app/data/skills
ENV PATH_DOCS=/app/data/docs

# Iniciar a aplicação utilizando o UV executando o modulo main
CMD ["uv", "run", "python", "-m", "src.main"]
