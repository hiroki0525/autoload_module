FROM python:3.8-alpine
RUN pip install -U pip \
    && pip install -i https://test.pypi.org/simple/ autoload-module \
    && pip list | grep autoload-module
COPY tests/ .
ENTRYPOINT ["python", "main.py"]