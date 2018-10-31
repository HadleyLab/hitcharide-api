## Develop
```
cp .env_example .env
```

Setup variables in .env

```
docker-compose up
```

## Deploy

To import cities and places:

git clone https://gitlab.bro.engineering/hitcharide/dataset.git

docker-compose run --rm api ./manage.py import_usa_cities
docker-compose run --rm api ./manage.py import_usa_places

