<template>
  <v-app class='form-wrapper' id='ax-form-viewer'>
    <AxForm :db_name='formDbName' :guid='rowNumGuid' :row='rowNumGuid'></AxForm>
  </v-app>
</template>

<script>
import AxForm from '@/components/AxForm.vue';

export default {
  name: 'FormView',
  components: { AxForm },
  computed: {
    rowNumGuid() {
      return this.$route.params.num_guid;
    },
    formDbName() {
      return this.$route.params.db_name;
    }
  }
};
</script>

<style scoped>
.form-wrapper {
  background: white;
  padding-top: 25px;
  padding-bottom: 25px;
  padding-left: 10%;
  padding-right: 10%;
}
</style>
