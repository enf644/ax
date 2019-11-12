<template>
  <v-radio-group
    :column='isColumn'
    :disabled='isReadonly'
    :error-messages='errors'
    :hint='options.hint'
    :label='name'
    :row='isRow'
    @change='isValid'
    v-model='currentValue'
  >
    <v-radio :key='item.value' :label='item.text' :value='item.value' v-for='item in items'></v-radio>
  </v-radio-group>
</template>

<script>
export default {
  name: 'AxRadio',
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
    items() {
      if (this.options.items) return JSON.parse(this.options.items);

      const defaultItems = [
        { text: 'One', value: 'one_value' },
        { text: 'Two', value: 'two_value' },
        { text: 'Three', value: 'three_value' }
      ];
      return defaultItems;
    },
    isColumn() {
      if (this.options && this.options.horizontal) return false;
      return true;
    },
    isRow() {
      if (this.options && this.options.horizontal) return true;
      return false;
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
