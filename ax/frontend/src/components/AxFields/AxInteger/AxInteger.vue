<template>
  <v-text-field
    :error-messages='errors'
    :hint='options.hint'
    :label='name'
    @keyup='isValid'
    type='number'
    v-model='currentValue'
  ></v-text-field>
</template>

<script>
import i18n from '../../../locale.js';

export default {
  name: 'AxInteger',
  props: {
    name: null,
    dbName: null,
    tag: null,
    options: null,
    value: null,
    isRequired: null
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
        if (!this.currentValue || this.currentValue.length === 0) {
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
