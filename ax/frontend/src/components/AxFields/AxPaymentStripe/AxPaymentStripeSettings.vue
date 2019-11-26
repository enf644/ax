<template>
  <AxFieldSettings :guid='guid' :options='changedOptions' @closed='$emit("closed")'>
    <v-text-field
      :label='locale("types.AxPaymentStripe.button-text-setting")'
      v-model='changedOptions.buttonText'
    ></v-text-field>
    <br />
    <v-text-field
      :label='locale("types.AxPaymentStripe.success-message-setting")'
      v-model='changedOptions.successMessage'
    ></v-text-field>
  </AxFieldSettings>
</template>

<script>
import AxFieldSettings from '@/components/AxFieldSettings.vue';
import i18n from '@/locale.js';
import MonacoEditor from 'vue-monaco';

export default {
  name: 'AxRadioSettings',
  components: { AxFieldSettings, MonacoEditor },
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
    if (!this.changedOptions.buttonText)
      this.changedOptions.buttonText = this.locale(
        'types.AxPaymentStripe.button-default'
      );
    if (!this.changedOptions.successMessage)
      this.changedOptions.successMessage = this.locale(
        'types.AxPaymentStripe.success-message-default'
      );
    if (!this.changedOptions.requiredText)
      this.changedOptions.requiredText = this.locale(
        'types.AxPaymentStripe.required-default'
      );
  },
  mounted() {},
  methods: {
    locale(key) {
      return i18n.t(key);
    }
  }
};
</script>

<style scoped>
</style>
