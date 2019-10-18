<template>
  <span>
    <slot v-if='loading'></slot>
    <span class='formated' ref='valueSpan'></span>
  </span>
</template>

<script>
import AutoNumeric from 'autonumeric';

export default {
  name: 'AxDecimalColumn',
  props: {
    options_json: null
  },
  data: () => ({
    loading: true,
    formatedValue: null,
    options: null
  }),
  mounted() {
    const value = this.$slots.default[0].elm.innerText;
    this.formatedValue = value;
    this.$refs.valueSpan.innerText = value;
    this.initAutoNumeric();
    this.loading = false;
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

      if (this.options_json) {
        this.options = JSON.parse(this.options_json);

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
      }

      this.numericObject = new AutoNumeric(
        this.$refs.valueSpan,
        autoNumberOptions
      );
    }
  }
};
</script>

<style scoped>
</style>
