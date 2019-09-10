<template>
  <AxFieldSettings
    :guid='guid'
    :options='changedOptions'
    :privateOptions='changedPrivateOptions'
    @closed='$emit("closed")'
  >
    <v-text-field
      :hint='locale("types.AxNum.settings-counter-hint")'
      :label='locale("types.AxNum.settings-counter-key")'
      :rules='keyRules'
      persistent-hint
      v-model='changedPrivateOptions.counterKey'
    ></v-text-field>
    <br />
    {{locale("types.AxNum.settings-algorithm")}}:
    <monaco-editor
      class='editor'
      language='python'
      ref='editor'
      theme='vs-dark'
      v-model='changedPrivateOptions.algorithm'
    ></monaco-editor>
    <v-radio-group v-model='changedOptions.comparator'>
      <v-radio :label='locale("types.AxNum.settings-string-comparator")' value='string'></v-radio>
      <v-radio :label='locale("types.AxNum.settings-number-comparator")' value='number'></v-radio>
    </v-radio-group>
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
    options: null,
    privateOptions: null
  },
  data: () => ({
    changedOptions: {},
    changedPrivateOptions: {},
    errors: [],
    keyRules: [v => !!v || i18n.t('common.field-required')]
  }),
  computed: {
    formGuid() {
      return this.$store.state.form.guid;
    }
  },
  created() {
    this.changedOptions = this.options;
    if (!this.changedOptions.comparator) {
      this.changedOptions.comparator = 'string';
    }

    if (this.privateOptions) {
      this.changedPrivateOptions = this.privateOptions;
    }
    if (!this.changedPrivateOptions.algorithm) {
      this.changedPrivateOptions.algorithm = '\n# first value of counter';
      this.changedPrivateOptions.algorithm += 'if not ax_counter:';
      this.changedPrivateOptions.algorithm += '\n    ax_counter=1';
      this.changedPrivateOptions.algorithm
        += '# ax_num will be the value of field';
      this.changedPrivateOptions.algorithm += '\nax_num=f"{ax_counter}"';
      this.changedPrivateOptions.algorithm += '\n# Increment counter';
      this.changedPrivateOptions.algorithm
        += '\nax_counter=str(int(ax_counter) + 1)';
    }
    if (!this.changedPrivateOptions.counterKey) {
      this.changedPrivateOptions.counterKey = this.formGuid;
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
