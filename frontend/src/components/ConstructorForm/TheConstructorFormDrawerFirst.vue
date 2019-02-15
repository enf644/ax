<template>
  <div>
    <p v-dummy='5'></p>
    <v-dialog max-width='80%' scrollable v-model='dialog'>
      <v-btn color='primary' dark slot='activator'>Open Dialog</v-btn>
      <v-card>
        <AxForm></AxForm>
      </v-card>
    </v-dialog>
    <h1>{{ this.$route.params.db_name }}</h1>
  </div>
</template>

<script>
import AxForm from '@/components/AxForm.vue';

export default {
  components: {
    AxForm
  },
  data: () => ({
    dialog: false
  })
};
</script>

<style scoped>
</style>
