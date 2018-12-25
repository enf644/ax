<template>
  <div class="home">
    <img alt="Vue logo" src="../assets/logo.png">
    <HelloWorld msg="Welcome to Your Vue.js App"/>
    
    <ax-grid name="Hello grid" />
  </div>
</template>

<script>
    import axios from 'axios';
    import HelloWorld from "@/components/HelloWorld.vue";

    export default {
        name: "home",
        components: {
            HelloWorld
        },
        methods: {

        },
        created: function() {
            axios.get('/api/hello', {
                    params: {
                        object_id: 12345
                    }
                })
                .then(function(response) {
                    console.log(response);
                })
                .catch(function(error) {
                    console.log(error);
                })
                .then(function() {
                    // always executed
                });
        }
    }

    ;
</script>
