<template>
  <span>
    <slot v-show='false'></slot>
    <i class='fas fa-check' v-if='currentValue == true'></i>
    <i class='fas fa-times' v-if='currentValue == false'></i>
  </span>
</template>

<script>
export default {
  name: 'AxCheckboxColumn',
  data: () => ({
    currentValue: null
  }),
  mounted() {
    const value = this.$slots.default[0].elm.innerText;
    if (value == 'true' || value == '1' || value == 'True') {
      this.currentValue = true;
    } else {
      this.currentValue = false;
    }
    this.$slots.default[0].elm.innerText = '';
  },
  methods: {}
};
</script>

<style scoped>
</style>
