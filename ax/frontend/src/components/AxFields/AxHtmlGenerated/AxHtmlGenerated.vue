<template>
  <div>
    <div v-html='value'></div>
    <v-alert
      :value='this.value == null'
      type='warning'
    >{{locale("common.no-field-settings-error", {name: this.name})}}</v-alert>
  </div>
</template>

<script>
import i18n from '@/locale';

export default {
  name: 'AxHtmlGenerated',
  props: {
    name: null,
    dbName: null,
    tag: null,
    optionsJson: null,
    value: null
  },
  computed: {
    currentName() {
      if (!this.name) return '';
      return this.name;
    }
  },
  methods: {
    locale(key, params) {
      return i18n.t(key, params);
    }
  }
};
</script>

<style scoped>
</style>
