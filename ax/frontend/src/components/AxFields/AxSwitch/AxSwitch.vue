<template>
  <v-switch :disabled='isReadonly' :error-messages='errors' :label='name' v-model='currentValue'></v-switch>
</template>

<script>
import i18n from '@/locale.js';

export default {
  name: 'AxSwitch',
  props: {
    name: null,
    dbName: null,
    tag: null,
    options: null,
    value: null,
    isRequired: null,
    isReadonly: null,
    formDbName: null
  },
  data: () => ({
    currentValue: null,
    errors: []
  }),
  watch: {
    currentValue(newValue) {
      this.$emit('update:value', newValue);
    },
    value(newValue) {
      this.currentValue = newValue;
    }
  },
  created() {
    this.currentValue = this.value;
  },
  methods: {
    isValid() {
      if (this.requiredIsValid()) return true;
      return false;
    },
    requiredIsValid() {
      if (this.isRequired) {
        if (!this.currentValue) {
          const msg = i18n.t('common.field-required');
          this.errors.push(msg);
          return false;
        }
        this.errors = [];
        return true;
      }
      return true;
    }
  }
};
</script>

<style scoped>
</style>
