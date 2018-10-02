#!/usr/bin/env bash
docker-compose run --rm api sh -c 'coverage run ./manage.py test && coverage report && coverage html'
