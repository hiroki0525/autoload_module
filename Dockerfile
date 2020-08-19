# for test.
FROM ubuntu:19.10
FROM python:3.8.1-alpine
ENV PYTHONUNBUFFERED 1
RUN pip install --upgrade pip
RUN mkdir /code
WORKDIR /code
COPY ./src /code/
COPY tests /code/
VOLUME ./src /code/src/
VOLUME ./tests /code/tests/
CMD ["python", "-m", "unittest", "/code/tests/base/test_autoload_module"]