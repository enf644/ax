<template>
  <AxFieldSettings :guid='guid' :options='changedOptions' @closed='$emit("closed")'>
    <v-text-field
      :hint='regExpHint'
      :label='regExpLabel'
      persistent-hint
      v-model='changedOptions.regexp'
    ></v-text-field>
    <v-text-field
      :hint='errorHint'
      :label='errorLabel'
      persistent-hint
      v-model='changedOptions.regexp_error'
    ></v-text-field>
    <br>
    {{testerHint}}:
    <br>
    <v-text-field
      :error-messages='errors'
      :label='testerLabel'
      @keyup='checkTester'
      v-model='testerValue'
    ></v-text-field>
  </AxFieldSettings>
</template>

<script>
import AxFieldSettings from '@/components/AxFieldSettings.vue';
import i18n from '../../../locale.js';

export default {
  name: 'AxStringSettings',
  components: { AxFieldSettings },
  props: {
    guid: null,
    options: null
  },
  data: () => ({
    changedOptions: {},
    regExpLabel: null,
    regExpHint: null,
    errorLabel: null,
    errorHint: null,
    testerHint: null,
    testerLabel: null,
    testerValue: null,
    errors: []
  }),
  created() {
    this.changedOptions = this.options;
    this.regExpLabel = i18n.t('types.AxString.regexp-label');
    this.regExpHint = i18n.t('types.AxString.regexp-hint', {
      example: '/^[a-zA-Z\\d][\\w]{0,127}$/'
    });
    this.errorLabel = i18n.t('types.AxString.error-label');
    this.errorHint = i18n.t('types.AxString.error-hint');
    this.testerHint = i18n.t('types.AxString.tester-hint');
    this.testerLabel = i18n.t('types.AxString.tester-label');
  },
  methods: {
    checkTester() {
      let regexp = null;
      const regParts = this.changedOptions.regexp.match(/^\/(.*?)\/([gim]*)$/);
      if (regParts) {
        regexp = new RegExp(regParts[1], regParts[2]);
      } else {
        regexp = new RegExp(this.changedOptions.regexp);
      }
      const pattern = new RegExp(regexp);
      if (!pattern.test(this.testerValue)) {
        this.errors.push(this.changedOptions.regexp_error);
      } else this.errors = [];
    }
  }
};
</script>

<style scoped>
</style>
