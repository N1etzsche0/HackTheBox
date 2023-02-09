<template>
  <div class="select-username">
    <h1>Login</h1>
    <form @submit.prevent="onSubmit">
      <input ref="username" v-model="username" placeholder="Your username..."/>
      <input type="password" v-model="password" placeholder="Your password..."/>
      <input type="hidden" v-model="authserver"/><br/>
      <button :disabled="!isValid">Login</button>
    </form>
  </div>
</template>

<script>
export default {
  name: "SelectUsername",
  data() {
    return {
      username: "",
      password: "",
      authserver: "ldap.response.htb",
    };
  },
  computed: {
    isValid() {
      return (this.username.length > 2) && (this.password.length > 4);
    },
  },
  methods: {
    onSubmit() {
      this.$emit("input", this.username, this.password, this.authserver);
    },
  },
  mounted() {
    this.$refs.username.focus();
  }
};
</script>

<style scoped>
.select-username {
  width: 300px;
  margin: 200px auto 0;
}
.select-username input {
  margin-top:10px;
}
.select-username button {
  margin-top:10px;
}
</style>
