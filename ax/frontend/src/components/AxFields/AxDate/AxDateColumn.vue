<template>
  <span v-show='loaded'>
    <slot v-show='false'></slot>
  </span>
</template>

<script>
export default {
  name: 'AxDateColumn',
  data: () => ({
    loaded: false
  }),
  mounted() {
    const value = this.$slots.default[0].elm.innerText;
    if (value && value != 'null') {
      this.$slots.default[0].elm.innerText = this.timestampToStr(value);
    } else {
      this.$slots.default[0].elm.innerText = '';
    }
    this.loaded = true;
  },
  methods: {
    timestampToStr(timestamp) {
      if (timestamp) {
        let date = new Date(timestamp * 1000),
          month = '' + (date.getMonth() + 1),
          day = '' + date.getDate(),
          year = date.getFullYear();

        if (month.length < 2) month = '0' + month;
        if (day.length < 2) day = '0' + day;

        return [year, month, day].join('-');
      }
      return null;
    }
  }
};
</script>

<style scoped>
</style>
