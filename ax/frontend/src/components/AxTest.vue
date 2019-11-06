<template>
  <div>
    <!-- <v-autocomplete :items='components' label='Components'></v-autocomplete> -->
    {{propD}}
  </div>
</template>

<script>
export default {
  props: {
    propD: {
      type: String,
      default: 'wtf'
    }
  },
  mounted() {},
  data() {
    return {};
  },
  mounted() {
    // console.log(this.$vuetify.lang.t('wtf'));
    // console.log(this.echo('wtf'));
    setTimeout(() => {
      console.log(this.$vuetify);
    }, 1000);
  },
  methods: {}
};
</script>

<style scoped>
</style>
