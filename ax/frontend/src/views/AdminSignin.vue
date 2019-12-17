<template>
  <div class='wrapper'>
    <ax-sign-in @signin='gotoAdmin()'></ax-sign-in>
  </div>
</template>

<script>
export default {
  name: 'AdminSignin',

  components: {},
  data() {
    return {};
  },
  computed: {},
  watch: {},
  mounted() {},
  methods: {
    gotoAdmin(url) {
      this.$router.push({ path: '/admin/home' });
      // console.log(`goto -> ${url}`);
      // window.location.href = url;
    }
  }
};
</script>

<style scoped>
</style>
