<template>
  <span>
    <slot v-show='false'></slot>
  </span>
</template>

<script>
export default {
  name: 'AxIntegerColumn',
  data: () => ({
    num: null
  }),
  mounted() {
    const value = this.$slots.default[0].elm.innerText;
    this.$slots.default[0].elm.innerText = value
      .replace(
        new RegExp(
          `^(\\d{${value.length % 3 ? value.length % 3 : 0}})(\\d{3})`,
          'g'
        ),
        '$1 $2'
      )
      .replace(/(\d{3})+?/gi, '$1 ')
      .trim();
  },
  methods: {}
};
</script>

<style lang="scss" scoped>
</style>
