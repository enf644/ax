<template>
  <div>
    <span class='label'>{{currentName}}</span>
    <div class='value-div'>{{value}}</div>
    <hr>
  </div>
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
  },
  computed: {
    currentName() {
      if (!this.name) return '';
      return this.name;
    }
  }
};
</script>

<style scoped>
.label {
  font-size: 13px;
  color: #000;
  opacity: 0.54;
}
.value-div {
  min-height: 26px;
  font-size: 16px;
  font-weight: bold;
}
</style>
