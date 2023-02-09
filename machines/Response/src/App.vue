<template>
  <div id="app">
    <select-username
      v-if="!loggedIn"
      @input="onUsernameSelection"
    />
    <chat v-else />
  </div>
</template>

<script>
import SelectUsername from "./src/components/SelectUsername";
import Chat from "./src/components/Chat";
import socket from "./socket";

export default {
  name: "App",
  components: {
    Chat,
    SelectUsername,
  },
  data() {
    return {
      loggedIn: false,
    };
  },
  methods: {
    onUsernameSelection(username, password, authserver) {
      document.getElementById('div_download').style.display = 'none';
      this.loggedIn = true;
      socket.auth = { username, password, authserver };
      socket.connect();
    },
  },
  created() {
    const sessionID = localStorage.getItem("sessionID");

    if (sessionID) {
      document.getElementById('div_download').style.display = 'none';
      this.loggedIn = true;
      socket.auth = { sessionID };
      socket.connect();
    }

    socket.on("session", ({ sessionID, username }) => {
      // attach the session ID to the next reconnection attempts
      socket.auth = { sessionID };
      // store it in the localStorage
      localStorage.setItem("sessionID", sessionID);
      // save the username of the user
      socket.username = username;
    });

    socket.on("connect_error", () => {
        this.loggedIn = false;
    });
  },
  destroyed() {
    socket.off("connect_error");
  }
};
</script>

<style>
body {
  margin: 0;
}

@font-face {
  font-family: Lato;
  src: url("/machines/Response/src/fonts/Lato-Regular.ttf");
}

#app {
  font-family: Lato, Arial, sans-serif;
  font-size: 14px;
}
</style>
