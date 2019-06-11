<template>
  <div>Current state: {{value}}</div>
</template>

<script>
export default {
  name: 'AxState',
  props: {
    name: null,
    dbName: null,
    tag: null,
    optionsJson: null,
    value: null
  }
};
</script>

<style scoped>
</style>
