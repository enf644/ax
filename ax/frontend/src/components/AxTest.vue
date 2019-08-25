<template>
  <div>
    <h1>WTF - {{locale('common.field-required')}}</h1>
  </div>
</template>

<script>
import i18n from '@/locale';

export default {
  mounted() {
    console.log(i18n.t('common.field-required'));
  },
  methods: {
    locale(key) {
      return i18n.t(key);
    }
  }
};
</script>

<style scoped>
</style>
