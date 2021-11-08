# coding-sample

## Overview

-   uses docker, docker-compose | python, flask, google vision | mongodb
-   you need to add secrets.env to the src/main/ directory consisting of your google vision api json
-   look at src/tests/tests.py to see what data and in what form the api expects to ingest

## How to Run

-   run `docker-compose up` in the root directory
-   this will create 4 containers. 2 for the dev env, 2 for the test env. each env consists on a flask container, and mongodb container.
-   the dev env is exposed at `localhost:9999` you can make requests using postman/curl/wget to it
-   look at `docker-compose.yml` and the assoc. mongodb service to see how to reach the dev mongodb container

## How to Test

-   `docker exec -it heb-coding-challenge-test /bin/bash`
-   in that container
    -   `cd tests/`
    -   `python tests.py`

## In the Future:

-   use flask testing framework
-   have api.py return flask app instead of app.run()
-   mock google vision api in tests to not add to budget
