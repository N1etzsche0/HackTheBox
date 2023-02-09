# Response Scanning Solutions - Internal Chat Application

This repository contains the Response Scanning Solutions internal chat application.

The application is based on the following article: https://socket.io/get-started/private-messaging-part-1/.

## How to deploy

Make sure `redis` server is running and configured in `server/index.js`.

Adjust `socket.io` URL in `src/socket.js`.

Install and build the frontend:

```bash
$ npm install
$ npm run build
```

Install and run the server:

```bash
$ cd server
$ npm install
$ npm start
```
