<template>
  <v-text-field
    :disabled='isReadonly'
    :error-messages='errors'
    :hint='options.hint'
    :label='name'
    @keyup='isValid'
    cy-data='input'
    v-model='currentValue'
  ></v-text-field>
</template>

<script>
import i18n from '@/locale.js';

export default {
  name: 'AxEmail',
  props: {
    name: null,
    dbName: null,
    tag: null,
    options: null,
    value: null,
    isRequired: null,
    isReadonly: null
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
    locale(key, params = null) {
      return i18n.t(key, params);
    },
    isValid() {
      if (this.requiredIsValid() && this.regexpIsValid()) return true;
      return false;
    },
    requiredIsValid() {
      if (this.isRequired) {
        if (!this.currentValue || this.currentValue.length === 0) {
          let msg = i18n.t('common.field-required');
          if (this.options.required_text) msg = this.options.required_text;
          this.errors.push(msg);
          return false;
        }
        this.errors = [];
        return true;
      }
      return true;
    },
    regexpIsValid() {
      const pattern = /^(([^<>()\[\]\.,;:\s@\"]+(\.[^<>()\[\]\.,;:\s@\"]+)*)|(\".+\"))@(([^<>()[\]\.,;:\s@\"]+\.)+[^<>()[\]\.,;:\s@\"]{2,})$/i;
      if (
        this.currentValue &&
        this.currentValue.length > 0 &&
        !pattern.test(this.currentValue)
      ) {
        this.errors.push(this.locale('types.AxEmail.email-invalid'));
        return false;
      }
      this.errors = [];
      return true;
    }
  }
};
</script>

<style scoped>
</style>
