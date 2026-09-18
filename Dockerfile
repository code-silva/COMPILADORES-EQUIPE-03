FROM python:3.12-slim

WORKDIR /app

# Instala git e pipenv limpando o cache do apt no mesmo passo
RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir pipenv

# Copia APENAS os arquivos de dependência primeiro (Aproveitamento de Cache)
COPY Pipfile Pipfile.lock /app/

# Usa a cache do pip do Docker para não baixar dependências repetidas
RUN --mount=type=cache,target=/root/.cache/pip \
    pipenv install --system --deploy

# Copia o restante do código por último
COPY . /app/

EXPOSE 8000

# Imprime a URL amigável no terminal usando printf para formatar as quebras de linha
CMD ["sh", "-c", "printf '\n==================================================\n🚀 Documentação pronta! Acesse em: http://localhost:8000\n==================================================\n\n' && mkdocs serve -a 0.0.0.0:8000"]