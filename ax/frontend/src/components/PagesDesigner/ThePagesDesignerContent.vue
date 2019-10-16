<template>
  <div class='pages-preview' v-html='html'></div>
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
    html() {
      if (this.$store.state.pages.currentPage) {
        if (this.$store.state.pages.currentPage.html) {
          return this.$store.state.pages.currentPage.html;
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