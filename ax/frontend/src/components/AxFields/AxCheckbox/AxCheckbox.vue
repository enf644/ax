<template>
  <v-checkbox :label='name' :value='value' @change='$emit("update:value", $event)'></v-checkbox>
</template>

<script>
export default {
  name: 'AxCheckbox',
  props: {
    name: null,
    dbName: null,
    tag: null,
    optionsJson: null,
    value: null
  },
  watch: {
    value() {
      // console.log(newValue);
    }
  }
};
</script>

<style scoped>
</style>
