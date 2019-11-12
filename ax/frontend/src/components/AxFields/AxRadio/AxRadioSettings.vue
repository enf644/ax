<template>
  <AxFieldSettings :guid='guid' :options='changedOptions' @closed='$emit("closed")'>
    {{locale("types.AxRadio.items-editor-title")}}:
    <monaco-editor
      class='editor'
      language='json'
      ref='editor'
      theme='vs-dark'
      v-model='changedOptions.items'
    ></monaco-editor>
    <v-switch
      :label='locale("types.AxRadio.horizontal-setting")'
      cy-data='multiple-input'
      v-model='changedOptions.horizontal'
    ></v-switch>
  </AxFieldSettings>
</template>

<script>
import AxFieldSettings from '@/components/AxFieldSettings.vue';
import i18n from '../../../locale.js';
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
    if (!this.changedOptions.items) {
      const defaultItems = [
        { text: 'One', value: 'one_value' },
        { text: 'Two', value: 'two_value' },
        { text: 'Three', value: 'three_value' }
      ];
      this.changedOptions.items = JSON.stringify(defaultItems, null, 4);
    }
  },
  mounted() {},
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
.editor {
  width: 100%;
  height: 400px;
}
</style>
