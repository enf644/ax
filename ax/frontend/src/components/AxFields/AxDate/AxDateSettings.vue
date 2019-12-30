<template>
  <AxFieldSettings :guid='guid' :options='changedOptions' @closed='$emit("closed")'>
    <v-switch :label='locale("types.AxDate.defaultNow-label")' v-model='changedOptions.defaultNow'></v-switch>
  </AxFieldSettings>
</template>

<script>
import AxFieldSettings from '@/components/AxFieldSettings.vue';
import i18n from '@/locale.js';

export default {
  name: 'AxDateSettings',
  components: { AxFieldSettings },
  props: {
    guid: null,
    options: null
  },
  data: () => ({
    changedOptions: {},
    errors: []
  }),
  created() {
    this.changedOptions = this.options;
  },
  methods: {
    locale(key) {
      return i18n.t(key);
    }
  }
};
</script>

<style scoped>
</style>
