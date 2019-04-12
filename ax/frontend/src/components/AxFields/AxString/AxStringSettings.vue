<template>
  <AxFieldSettings :guid='guid' :options='changedOptions' @closed='$emit("closed")'>
    <v-text-field
      hint='www.example.com/page'
      label='Regular expression'
      persistent-hint
      v-model='changedOptions.regexp'
    ></v-text-field>
  </AxFieldSettings>
</template>

<script>
import AxFieldSettings from '@/components/AxFieldSettings.vue';

export default {
  name: 'AxStringSettings',
  components: { AxFieldSettings },
  props: {
    guid: null,
    options: null
  },
  data: () => ({
    changedOptions: {}
  }),
  created() {
    this.changedOptions = this.options;
  }
};
</script>

<style scoped>
</style>
