<template>
  <v-text-field :label='name' v-model='currentValue'></v-text-field>
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
    currentValue: null
  }),
  watch: {
    currentValue(newValue) {
      this.$emit('update:value', newValue);
    }
  },
  created() {
    this.currentValue = this.value;
  }
};
</script>

<style scoped>
</style>
