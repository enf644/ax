<template>
  <div>
    <h1>{{ count }}</h1>
    <v-btn @click='increment'>+</v-btn>
    <v-btn @click='decrement'>-</v-btn>

    <hr>

    <ul id='example-1'>
      <li v-for='user in users'>{{ user.name }} -> {{ user.email }}</li>
    </ul>
  </div>
</template>

<script>
export default {
  created() {
    this.$store.dispatch('users/getAllUsers');
    console.log(`users == ${this.$store.state.users.all}`);
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
    }
  }
};
</script>

<style scoped>
</style>
