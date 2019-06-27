<template>
  <AxFieldSettings :guid='guid' :options='changedOptions' @closed='$emit("closed")'>
    <v-text-field
      :hint='locale("types.AxFiles.settings-max-size-hint")'
      :label='locale("types.AxFiles.settings-max-size-label")'
      persistent-hint
      settings-max-size-hint
      type='number'
      v-model='changedOptions.maxFileSize'
    ></v-text-field>
    <br>
    <v-text-field
      :label='locale("types.AxFiles.settings-max-number-label")'
      type='number'
      v-model='changedOptions.maxNumberOfFiles'
    ></v-text-field>
    <br>
    <v-text-field
      :label='locale("types.AxFiles.settings-min-number-label")'
      type='number'
      v-model='changedOptions.minNumberOfFiles'
    ></v-text-field>
    <br>
    <v-text-field
      :hint='locale("types.AxFiles.settings-types-hint")'
      :label='locale("types.AxFiles.settings-types-label")'
      type='number'
      v-model='changedOptions.allowedFileTypes'
    ></v-text-field>
    <br>
    <v-switch
      :label='this.$t("types.AxFiles.settings-enable-webcam-label")'
      cy-data='settings-enableModal'
      v-model='changedOptions.enableWebcam'
    ></v-switch>
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
    if (
      this.changedOptions.enableWebcam == null
      || this.changedOptions.enableWebcam === undefined
    ) {
      this.changedOptions.enableWebcam = true;
    }
  },
  methods: {
    locale(key) {
      return i18n.t(key);
    },
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
