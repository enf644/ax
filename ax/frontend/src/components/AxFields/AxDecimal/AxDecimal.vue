<template>
  <v-text-field
    :disabled='isReadonly'
    :error-messages='errors'
    :hint='options.hint'
    :label='name'
    @keyup='isValid'
    cy-data='input'
    ref='field'
    v-model='formatedValue'
  ></v-text-field>
</template>

<script>
import i18n from '@/locale.js';
import AutoNumeric from 'autonumeric';

export default {
  name: 'AxDecimal',
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
    formatedValue: null,
    errors: [],
    numericObject: null
  }),
  computed: {},
  watch: {
    formatedValue(newValue) {
      if (this.currentValue != this.numericObject.getNumericString())
        this.currentValue = this.numericObject.getNumericString();
    },
    currentValue(newValue) {
      this.$emit('update:value', newValue);
    },
    value(newValue) {
      this.currentValue = newValue;
      this.numericObject.set(newValue);
    },
    options(newValue) {
      this.initAutoNumeric();
    }
  },
  created() {
    if (this.value) {
      this.currentValue = this.value;
      this.formatedValue = this.value;
    }
  },
  mounted() {
    this.initAutoNumeric();
  },
  methods: {
    initAutoNumeric() {
      let autoNumberOptions = {
        currencySymbol: '',
        decimalCharacter: ',',
        decimalPlaces: 2,
        decimalPlacesRawValue: 2,
        digitGroupSeparator: ' ',
        wheelStep: 1,
        minimumValue: 0,
        formulaMode: true
      };

      if (this.options.currencySymbol)
        autoNumberOptions.currencySymbol = this.options.currencySymbol;

      if (this.options.decimalCharacter)
        autoNumberOptions.decimalCharacter = this.options.decimalCharacter;

      if (this.options.decimalPlaces) {
        autoNumberOptions.decimalPlaces = this.options.decimalPlaces * 1;
        autoNumberOptions.decimalPlacesRawValue =
          this.options.decimalPlaces * 1;
      }

      if (this.options.digitGroupSeparator)
        autoNumberOptions.digitGroupSeparator = this.options.digitGroupSeparator;

      if (this.options.wheelStep)
        autoNumberOptions.wheelStep = this.options.wheelStep * 1;

      if (this.options.minimumValue)
        autoNumberOptions.minimumValue = this.options.minimumValue * 1;

      if (this.options.maximumValue)
        autoNumberOptions.maximumValue = this.options.maximumValue * 1;

      if (!this.numericObject) {
        setTimeout(() => {
          this.numericObject = new AutoNumeric(
            this.$refs.field.$refs.input,
            autoNumberOptions
          );
        }, 10);
      } else {
        this.numericObject.update(autoNumberOptions);
      }
    },
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
