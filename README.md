## How to run

#### Set the environment variables

`cp -r .env.example/ .env/`

#### Run for production

`docker compose up -d --build`

#### Run for development

`chmod +x app/entrypoints/entrypoint-dev.sh`

`docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build`

#### Stopping the containers

`docker compose down`
