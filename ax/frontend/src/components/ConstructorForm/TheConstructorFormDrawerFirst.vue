<template>
  <div>
    <p v-dummy='5'></p>

    <v-dialog max-width='80%' scrollable v-model='dialog'>
      <v-btn color='primary' dark slot='activator'>Open Dialog</v-btn>
      <v-card>
        <ax-form no_margin></ax-form>
      </v-card>
    </v-dialog>
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
