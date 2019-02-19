<template>
  <div>
    <h1>{{ count }}</h1>
    <v-btn @click='increment'>+</v-btn>
    <v-btn @click='decrement'>-</v-btn>
  </div>
</template>

<script>
export default {
  computed: {
    count() {
      return this.$store.state.test.count;
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
