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
      language='python'
      ref='editor'
      theme='vs-dark'
      v-model='changedPrivateOptions.code'
    ></monaco-editor>
  </AxFieldSettings>
</template>

<script>
import AxFieldSettings from '@/components/AxFieldSettings.vue';
import i18n from '@/locale';
import MonacoEditor from 'vue-monaco';

export default {
  name: 'AxChoiseSettings',
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
    if (!this.changedPrivateOptions.code) {
      this.changedPrivateOptions.code = '# ax.value will be displayed\n';
      this.changedPrivateOptions.code += 'ax.value = f"""\n';
      this.changedPrivateOptions.code += '    <i>hello world</i>\n';
      this.changedPrivateOptions.code += '"""';
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
