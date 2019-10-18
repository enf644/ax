<template>
  <div>
    <v-subheader class='pl-0'>{{name}}</v-subheader>
    <v-slider
      :disabled='isReadonly'
      :error-messages='errors'
      :max='currentMax'
      :min='currentMin'
      :step='currentStep'
      :thumb-size='25'
      cy-data='input'
      height='55'
      thumb-label='always'
      v-model='currentValue'
    ></v-slider>
  </div>
</template>

<script>
import i18n from '@/locale.js';

export default {
  name: 'AxIntSlider',
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
  computed: {
    currentMin() {
      if (this.options.minValue) return this.options.minValue;
      else return 0;
    },
    currentMax() {
      if (this.options.maxValue) return this.options.maxValue;
      else return 100;
    },
    currentStep() {
      if (this.options.step) return this.options.step;
      else return 1;
    }
  },
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
          let msg = i18n.t('common.field-required');
          if (this.options.required_text) msg = this.options.required_text;
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
