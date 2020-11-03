FROM python:3.8-alpine
RUN pip install -U pip \
    && pip install -i https://test.pypi.org/simple/ autoload-module
COPY tests/main.py .
COPY tests/ tests
RUN rm tests/main.py
ENTRYPOINT ["python", "main.py"]