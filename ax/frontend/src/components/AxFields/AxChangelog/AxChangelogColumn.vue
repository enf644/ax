<template>
  <span>
    {{i18n.t('common.no-column', {name: 'AxChangelog'})}}
    <slot v-show='false'></slot>
  </span>
</template>

<script>
export default {
  name: 'AxChangelogColumn',
  data: () => ({
    num: null
  }),
  mounted() {},
  methods: {}
};
</script>

<style scoped>
</style>
