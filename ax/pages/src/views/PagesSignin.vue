<template>
  <div>
    <ax-sign-in @signin='gotoPages()'></ax-sign-in>
  </div>
</template>

<script>
// import CatalogItem from '@/components/CatalogItem.vue';

export default {
  name: 'PagesSignin',
  components: {},
  data: () => ({}),
  computed: {},
  watch: {},
  mounted() {},
  methods: {
    gotoPages() {
      this.$router.push({ path: '/' });
    }
  }
};
</script>

<style scoped>
</style>
