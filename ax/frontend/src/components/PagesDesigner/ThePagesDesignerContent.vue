<template>
  <div class='pages-preview' v-html='code'></div>
</template>

<script>
// import CatalogItem from '@/components/CatalogItem.vue';

export default {
  name: 'ThePagesDesignerContent',
  components: {},
  data: () => ({
    guid: null
  }),
  computed: {
    code() {
      if (this.$store.state.pages.currentPage) {
        if (this.$store.state.pages.currentPage.code) {
          return this.$store.state.pages.currentPage.code;
        }
        return '';
      }
      return 'loading...';
    }
  },
  watch: {},
  mounted() {},
  methods: {}
};
</script>

<style scoped>
.pages-preview {
  height: 100%;
}
</style>