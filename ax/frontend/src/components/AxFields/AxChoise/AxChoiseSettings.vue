<template>
  <AxFieldSettings :guid='guid' :options='changedOptions' @closed='$emit("closed")'>
    {{locale("types.AxChoise.items-editor-title")}}:
    <monaco-editor
      class='editor'
      language='json'
      ref='editor'
      theme='vs-dark'
      v-model='changedOptions.items'
    ></monaco-editor>
    <v-switch
      :label='locale("types.AxChoise.multiple-setting")'
      data-cy='multiple-input'
      v-model='changedOptions.multiple'
    ></v-switch>
    <v-switch
      :label='locale("types.AxChoise.clearable-setting")'
      v-model='changedOptions.clearable'
    ></v-switch>
    <v-text-field
      :hint='locale("types.AxChoise.placeholder-hint")'
      :label='locale("types.AxChoise.placeholder-setting")'
      persistent-hint
      v-model='changedOptions.placeholder'
    ></v-text-field>
  </AxFieldSettings>
</template>

<script>
import AxFieldSettings from '@/components/AxFieldSettings.vue';
import i18n from '../../../locale.js';
import MonacoEditor from 'vue-monaco';

export default {
  name: 'AxChoiseSettings',
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
      this.changedOptions.items = `[
  { "text": "One", "value": "one" },
  { "text": "Two", "value": "two" },
  { "text": "Three", "value": "three" }
]      
      `;
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
