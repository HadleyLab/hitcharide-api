## Develop
```
cp .env_example .env
```

Setup variables in .env

```
docker-compose up
```

## Deploy

To import cities:

docker-compose run --rm api ./manage.py import_usa_cities
