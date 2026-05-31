# a versão do python que iremos começar
FROM python:3.13.11-slim

# obter a versão do uv de outro container, irei pegar de /uv e colocar em /bin/
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

# o diretorio de inicio
WORKDIR /code

# iniciar o venv a partir do path, para não usar uv run no entry point
ENV PATH="/code/.venv/bin:$PATH"

# irei salvar esses 3 arquivos no diretório de inicio
COPY pyproject.toml .python-version uv.lock ./

# irei obter todas as dependencias que eu tenho fora do container
RUN uv sync --locked

# copiar ingest_data.py para o container
COPY ingest_data.py .

# irá rodar o ingest_data.py ao digitar o comando docker run
ENTRYPOINT [ "uv", "run", "python", "ingest_data.py" ]