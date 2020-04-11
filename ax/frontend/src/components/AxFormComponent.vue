<template>
  <v-app id='ax-form-app'>
    <AxForm
      :db_name='db_name'
      :opened_tab='opened_tab'
      :row_guid='row_guid'
      :update_time='update_time'
    />
  </v-app>
</template>

<script>
import AxForm from '@/components/AxForm.vue';

export default {
  name: 'AxFormComponent',
  components: { AxForm },
  props: {
    db_name: null,
    row_guid: null,
    update_time: null,
    opened_tab: null
  },
  data: () => ({}),
  computed: {},
  watch: {},
  mounted() {},
  methods: {}
};
</script>

<style scoped>
</style>