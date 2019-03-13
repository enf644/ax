<template>
  <div>TheUsersList
    <div>
      <button v-on:click='counter += 1'>Add 1</button>
      <p>The button above has been clicked {{ counter }} times.</p>
    </div>
  </div>
</template>

<script>
export default {
  data: () => ({
    counter: 644
  })
};
</script>

<style scoped>
</style>
