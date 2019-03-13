<template>
  <div class='ax-tab'>
    <h1>{{ msg }}</h1>
    <h3>tags here 1122</h3>
  </div>
</template>

<script>
export default {
  name: 'ax-tab',
  data() {
    return {
      message: 'Hello world'
    };
  },
  props: {
    msg: String
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h3 {
  margin: 40px 0 0;
}

ul {
  list-style-type: none;
  padding: 0;
}

li {
  display: inline-block;
  margin: 0 10px;
}

a {
  color: #42b983;
}
</style>
