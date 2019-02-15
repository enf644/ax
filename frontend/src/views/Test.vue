<template>
  <div id='example-1'>
    <button v-on:click='counter += 1'>Add 1</button>
    <p>The button above has been clicked {{ counter }} times.</p>
  </div>
</template>

<script>
export default {
  name: 'test',
  data: () => ({
    counter: 5
  })
};
</script>

<style scoped>
</style>