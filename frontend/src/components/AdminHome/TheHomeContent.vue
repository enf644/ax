<template>
  <div>
    <h1>{{ count }}</h1>
    <v-btn @click='increment'>+</v-btn>
    <v-btn @click='decrement'>-</v-btn>

    <hr>

    <ul id='example-1'>
      <li :key='user.guid' v-for='user in users'>{{ user.name }} -> {{ user.email }}</li>
    </ul>

    <br>
    <br>
    <br>
    <br>
    <v-btn @click='createNewUser' color='success'>Add new user</v-btn>
  </div>
</template>

<script>
export default {
  created() {
    this.$store.dispatch('users/getAllUsers');
    this.$store.dispatch('users/subscribeToUsers');
  },
  computed: {
    count() {
      return this.$store.state.test.count;
    },
    users() {
      return this.$store.state.users.all;
    }
  },
  methods: {
    increment() {
      this.$store.commit('test/increment');
    },
    decrement() {
      this.$store.commit('test/decrement');
    },
    createNewUser() {
      this.$store.dispatch('users/createNewUser');
    }
  }
};
</script>

<style scoped>
</style>
