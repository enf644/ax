<template>
  <div>
    <h4>{{ name }}</h4>
  </div>
</template>

<script>
export default {
  props: {
    name: null
  },
  created() {
    const debugMsg = 'Debug this Vue';
    this.$log.info(debugMsg);
  }
};
</script>
