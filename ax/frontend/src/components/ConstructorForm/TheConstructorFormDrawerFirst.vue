<template>
  <div>
    <p v-dummy='5'></p>
    <h1>{{ this.$route.params.db_name }}</h1>
  </div>
</template>

<script>
export default {
  components: {},
  data: () => ({
    dialog: false
  })
};
</script>

<style scoped>
</style>
