<template>
  <AxFieldSettings
    :guid='guid'
    :options='changedOptions'
    :privateOptions='changedPrivateOptions'
    @closed='$emit("closed")'
  >
    {{locale("types.AxHtml.settings-code")}}:
    <monaco-editor
      class='editor'
      language='html'
      ref='editor'
      theme='vs-dark'
      v-model='changedOptions.code'
    ></monaco-editor>
  </AxFieldSettings>
</template>

<script>
import AxFieldSettings from '@/components/AxFieldSettings.vue';
import i18n from '@/locale';
import MonacoEditor from 'vue-monaco';

export default {
  name: 'AxHtmlSettings',
  components: { AxFieldSettings, MonacoEditor },
  props: {
    guid: null,
    options: null,
    privateOptions: null
  },
  data: () => ({
    changedOptions: {},
    changedPrivateOptions: {},
    errors: []
  }),
  computed: {},
  created() {
    this.changedOptions = this.options;
    if (this.privateOptions) {
      this.changedPrivateOptions = this.privateOptions;
    }
    if (!this.changedOptions.code) {
      this.changedOptions.code = '<i>hello world</i>\n';
    }
  },
  mounted() {},
  methods: {
    locale(key, param) {
      return i18n.t(key, param);
    }
  }
};
</script>

<style scoped>
.editor {
  width: 100%;
  height: 400px;
  margin-bottom: 15px;
}
</style>
