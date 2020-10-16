<template>
  <v-text-field
    :disabled="isReadonly"
    :error-messages="errors"
    :hint="options.hint"
    :label="name"
    @keyup="isValid"
    data-cy="input"
    v-model="currentValue"
  ></v-text-field>
</template>

<script>
import i18n from '@/locale.js';

export default {
  name: 'AxString',
  props: {
    name: null,
    dbName: null,
    tag: null,
    options: null,
    value: null,
    isRequired: null,
    isReadonly: null,
  },
  data: () => ({
    currentValue: null,
    errors: [],
  }),
  computed: {},
  watch: {
    currentValue(newValue) {
      this.$emit('update:value', newValue);
    },
    value(newValue) {
      this.currentValue = newValue;
    },
  },
  created() {
    this.currentValue = this.value;
  },
  methods: {
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
      if (this.options.regexp) {
        let regexp = null;
        const regParts = this.options.regexp.match(/^\/(.*?)\/([gim]*)$/);
        if (regParts) {
          regexp = new RegExp(regParts[1], regParts[2]);
        } else {
          regexp = new RegExp(this.options.regexp);
        }
        const pattern = new RegExp(regexp);
        if (!pattern.test(this.currentValue) && this.currentValue.length > 0) {
          this.errors.push(this.options.regexp_error);
          return false;
        }
        this.errors = [];
        return true;
      }
      return true;
    },
  },
};
</script>

<style scoped>
</style>
