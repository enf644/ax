<template>
  <AxFieldSettings :guid='guid' :options='changedOptions' @closed='$emit("closed")'>
    <v-text-field
      :hint='locale("types.AxTelephone.mask-hint")'
      :label='locale("types.AxTelephone.mask-label")'
      persistent-hint
      v-model='changedOptions.mask'
    ></v-text-field>
  </AxFieldSettings>
</template>

<script>
import AxFieldSettings from '@/components/AxFieldSettings.vue';
import i18n from '@/locale.js';

export default {
  name: 'AxTelephoneSettings',
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
    if (!this.changedOptions.mask)
      this.changedOptions.mask = '+1 (###) ###-##-##';
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
