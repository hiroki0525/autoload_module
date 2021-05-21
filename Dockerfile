FROM python:3.7.10-alpine
COPY tests/main.py .
COPY tests/ tests
RUN pip install -U pip \
    && pip install -i https://test.pypi.org/simple/ autoload-module \
    && rm tests/main.py
ENTRYPOINT ["python", "main.py"]