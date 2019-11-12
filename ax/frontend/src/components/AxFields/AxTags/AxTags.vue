<template>
  <!-- <v-radio-group
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
  </v-radio-group>-->

  <v-combobox
    :clearable='clearable'
    :disabled='isReadonly'
    :error-messages='errors'
    :hint='options.hint'
    :items='items'
    :label='name'
    :search-input.sync='search'
    @change='isValid'
    hide-selected
    multiple
    small-chips
    v-model='currentValue'
  ></v-combobox>
</template>

<script>
export default {
  name: 'AxTags',
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
    errors: [],
    search: null
  }),
  computed: {
    items() {
      if (this.options.items) return JSON.parse(this.options.items);

      const defaultItems = ['one', 'two', 'three'];
      return defaultItems;
    },
    clearable() {
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
        if (!this.currentValue || this.currentValue.length == 0) {
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
