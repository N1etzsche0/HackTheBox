const express = require("express");
const app = express();
const path = require("path");
app.use(express.static(path.join(__dirname, "../dist/")));
app.get("/", function(req, res) {
  res.sendFile(path.join(__dirname, "../dist/", "index.html"));
});

const httpServer = require("http").createServer(app);
const Redis = require("ioredis");
const redisClient = new Redis(6379, "redis");

const io = require("socket.io")(httpServer, {
  adapter: require("socket.io-redis")({
    pubClient: redisClient,
    subClient: redisClient.duplicate(),
  }),
});

const { setupWorker } = require("@socket.io/sticky");
const crypto = require("crypto");
const randomId = () => crypto.randomBytes(16).toString("hex");

const { RedisSessionStore } = require("./sessionStore");
const sessionStore = new RedisSessionStore(redisClient);

const { authenticate } = require("ldap-authentication");


async function authenticate_user(username, password, authserver) {

  if (username === 'guest' && password === 'guest') return true;

  if (!/^[a-zA-Z0-9]+$/.test(username)) return false;
  
  let options = {
    ldapOpts: { url: `ldap://${authserver}` },
    userDn: `uid=${username},ou=users,dc=response,dc=htb`,
    userPassword: password,
  }
  try {
    return await authenticate(options);
  } catch { }
  return false;

}

io.use(async (socket, next) => {
  const sessionID = socket.handshake.auth.sessionID;
  if (sessionID) {
    const session = await sessionStore.findSession(sessionID);
    if (session) {
      socket.sessionID = sessionID;
      socket.username = session.username;
      return next();
    }
  }
  const username = socket.handshake.auth.username;
  if (!username) {
    return next(new Error("missing username"));
  }
  const password = socket.handshake.auth.password;
  if (!password) {
    return next(new Error("missing password"));
  }
  const authserver = socket.handshake.auth.authserver;
  if (!authserver) {
    return next(new Error("missing authserver"));
  }
  if (!await authenticate_user(username, password, authserver)) {
    return next(new Error("authentication error"));
  }

  socket.sessionID = randomId();
  socket.username = username;
  next();
});

io.on("connection", async (socket) => {
  // persist session
  sessionStore.saveSession(socket.sessionID, {
    username: socket.username,
    connected: true,
  });

  // emit session details
  socket.emit("session", {
    sessionID: socket.sessionID,
    username: socket.username,
  });

  // join the "username" room
  socket.join(socket.username);

  // fetch existing users
  const users = [];
  const sessions = await sessionStore.findAllSessions();
  sessions.forEach((session) => {
    // username not added yet ?
    if (users.filter(o => { return o.username === session.username}).length === 0) {
      // does this user have any active session?
      let active_session = sessions.filter(o => { return o.username === session.username && o.connected }).length > 0;
      users.push({
        username: session.username,
        connected: active_session,
      });
    }
  });
  socket.emit("users", users);

  // notify existing users
  socket.broadcast.emit("user connected", {
    username: socket.username,
    connected: true,
    messages: [],
  });

  // forward the private message to the right recipient (and to other tabs of the sender)
  socket.on("private message", ({ content, to }) => {
    const message = {
      content,
      from: socket.username,
      to,
    };
    socket.to(to).to(socket.username).emit("private message", message);
  });

  // notify users upon disconnection
  socket.on("disconnect", async () => {
    const matchingSockets = await io.in(socket.username).allSockets();
    const isDisconnected = matchingSockets.size === 0;
    if (isDisconnected) {
      // notify other users
      socket.broadcast.emit("user disconnected", socket.username);
      // update the connection status of the session
      sessionStore.saveSession(socket.sessionID, {
        username: socket.username,
        connected: false,
      });
    }
  });
});

setupWorker(io);
