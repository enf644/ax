<template>
  <v-select
    :clearable='options.clearable'
    :error-messages='errors'
    :hint='options.hint'
    :items='items'
    :label='name'
    :multiple='options.multiple'
    :placeholder='options.placeholder'
    @change='isValid'
    v-model='currentValue'
  ></v-select>
</template>

<script>
export default {
  name: 'AxChoise',
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
  computed: {
    items() {
      if (this.options.items) return JSON.parse(this.options.items);

      const defaultItems = [
        { text: 'One', value: 'one_value' },
        { text: 'Two', value: 'two_value' },
        { text: 'Three', value: 'three_value' }
      ];
      return defaultItems;
    }
  },
  watch: {
    currentValue(newValue) {
      this.$emit('update:value', newValue);
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
          this.errors.push(this.options.required_text);
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
