<template>
  <v-text-field :error-messages='errors' :label='name' @keyup='checkRegexp' v-model='currentValue'></v-text-field>
</template>

<script>
export default {
  name: 'AxString',
  props: {
    name: null,
    dbName: null,
    tag: null,
    optionsJson: null,
    value: null
  },
  data: () => ({
    currentValue: null,
    options: null,
    errors: []
  }),
  watch: {
    currentValue(newValue) {
      this.$emit('update:value', newValue);
    }
  },
  created() {
    this.currentValue = this.value;
    this.options = JSON.parse(this.optionsJson);
  },
  methods: {
    checkRegexp() {
      if (this.options.regexp) {
        let regexp = null;
        const regParts = this.options.regexp.match(/^\/(.*?)\/([gim]*)$/);
        if (regParts) {
          regexp = new RegExp(regParts[1], regParts[2]);
        } else {
          regexp = new RegExp(this.options.regexp);
        }
        const pattern = new RegExp(regexp);
        if (!pattern.test(this.currentValue)) {
          this.errors.push(this.options.regexp_error);
        } else this.errors = [];
      }
    }
  }
};
</script>

<style scoped>
</style>
