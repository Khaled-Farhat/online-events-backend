# Features
- Manage events and talks.
- Real-time events and chats.

# How to Run

- Set the environment variables: `cp -r .env.example/ .env/`

- Run for production: `docker compose up -d --build`

- Run for development:
    - `chmod +x app/entrypoints/entrypoint-dev.sh`
    - `chmod +x app/entrypoints/entrypoint-dev-celery.sh`
    - `docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build`
- Stopping the containers: `docker compose down`

# Usage

### Running the tests (Only in the development container)

`docker compose exec django-asgi pytest`

### API docs (Only in the development container)

`http://0.0.0.0:8080/api/v1/docs/`


### Publishing a stream
- From the speaker account, get the talk stream key from `/api/v1/talks/{talk_id}/key/`.
- Use WHIP protocol for ingestion (WebRTC-HTTP Ingestion Protocol)
  - Send a post request to `/rtc/v1/whip/?app=live&stream=talk_id&token=stream_key`. The body must contain the local SDP. The content type must be `application/sdp`.
  - The server will respond with the remote SDP.
  - Note that the event must be published, and the talk must be ongoing and approved by the speaker.

### Playing a stream
- Get a key from `/api/v1/users/{username}/play-stream-key/`.
- Play the stream using the HLS protocol. Stream URL: `/live/talk_id.m3u8?token=play_stream_key`.
  - Note that the user should have booked the event to be able to play its talks.
  
### Chat
- Get a key from `/api/v1/users/{username}/chat-key/`.
- Open a WebSocket connection with `ws/chats/talks/{talk_id}/?token=chat_key`.
- To send a message, send a json object of the form `{"message": "value"}`.

# Materials

- [Presentation Slides](https://docs.google.com/presentation/d/1gr2xp48faiGR6rzVcBh1AzplfjYG3UPV0HEZyhhzu7c/edit?usp=sharing).
- [Arabic Docs](https://docs.google.com/document/d/1PzhLFJWVGeptuDke-dM4d_J2AbReJcLaGwZ7jFw09yg/edit?usp=sharing).
