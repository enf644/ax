<template>
  <div>
    <v-sheet class='test-container' elevation='5' light ref='sheet'>
      <ul data-cy='user-list'>
        <li :key='user.guid' v-for='user in users'>{{ user.name }} -> {{ user.email }}</li>
      </ul>

      <br>

      <v-btn
        @click='createNewUser'
        color='success'
        data-cy='add-new-user'
      >{{$t("users.add-new-user")}}</v-btn>

      <br>
      <br>
      <h1>{{ $t("hello")}}</h1>
      <br>
    </v-sheet>
  </div>
</template>

<script>
export default {
  name: 'admin-toolbar',
  created() {
    // this.$log.info(this.$language.available);
    if (!this.$store.state.users.isUsersLoaded) {
      this.$store.dispatch('users/getAllUsers');
      this.$store.dispatch('users/subscribeToUsers');
    }
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
.test-container {
  margin: 20px;
  padding: 20px;
}
</style>
