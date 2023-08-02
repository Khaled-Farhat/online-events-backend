## How to run

#### Set the environment variables

`cp .app.env.example .app.env`

`cp .db.env.example .db.env`

#### Run for production

`docker compose up -d --build`

#### Run for development

`chmod +x app/entrypoint-dev.sh`

`docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build`

#### Migrate the database

`docker compose exec -it app bash`

`python3 manage.py migrate`

#### Stopping the containers

`docker compose down`
