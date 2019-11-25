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
    <br />

    <!-- 
      message - You invited message
      message - All branch approval is recieved. Action needed.
      message - Reviwer made action
      bool - comment needed on approve
      bool - comment needed on reject


    -->
  </AxFieldSettings>
</template>

<script>
import AxFieldSettings from '@/components/AxFieldSettings.vue';
import i18n from '@/locale.js';
import MonacoEditor from 'vue-monaco';

export default {
  name: 'AxApprovalSettings',
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
      const defaultItems = {
        x: ['one', 'two', 'three'],
        y: ['Bad', 'Normal', 'Good']
      };
      this.changedOptions.items = JSON.stringify(defaultItems, null, 4);
    }
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
.editor {
  width: 100%;
  height: 400px;
}
</style>
