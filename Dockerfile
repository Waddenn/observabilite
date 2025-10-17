ARG PYTHON_IMAGE_TAG="3.13-slim-bullseye"

FROM python:${PYTHON_IMAGE_TAG}

WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt && \
    opentelemetry-bootstrap -a install
COPY ./src/app.py /code
ENTRYPOINT  ["opentelemetry-instrument", "python", "app.py" ]
