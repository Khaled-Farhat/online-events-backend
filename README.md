## How to run

#### Set the environment variables

`cp .app.env.example .app.env`

`cp .db.env.example .db.env`

#### Run for production

`docker compose up -d --build`

#### Run for development

`docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build`

#### Stopping the containers

`docker compose down`
