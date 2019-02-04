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
            let debug_msg = "Debug this Vue"
            console.log(debug_msg);
        }
    };
</script>