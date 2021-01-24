FROM python:3.7.7-alpine3.11

WORKDIR /code

COPY Pipfile Pipfile.lock ./

RUN apk add --no-cache postgresql-libs && \
  apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
  pip install pipenv --no-cache-dir && \
  pipenv install --system && \
  apk --purge del .build-deps

EXPOSE 8080

ENTRYPOINT ["python", "manage.py"]
CMD ["runserver", "0.0.0.0:8000"]
