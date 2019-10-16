<template>
  <div class='content-wrapper h-full w-full flex flex-row'>
    <div class='menu-wrapper' v-if='drawerEnabled === false'>
      <TheDrawerMenu />
    </div>
    <div class='loading-div' v-if='currentHtml == null'>
      <i class='loading-spinner fas fa-circle-notch fa-spin'></i>
      <img class='loading-logo' src='@/assets/small_axe.png' />
    </div>
    <div class='current-page h-full w-full' v-html='currentHtml'></div>
  </div>
</template>

<script>
import TheDrawerMenu from '@/components/TheDrawerMenu.vue';
import * as showdown from 'showdown';

export default {
  name: 'TheContent',
  components: { TheDrawerMenu },
  data: () => ({
    guid: null,
    converter: null
  }),
  computed: {
    pageId() {
      return this.$route.params.page;
    },
    currentHtml() {
      if (this.$store.state.currentPage && this.$store.state.currentPage.html) {
        const { html } = this.$store.state.currentPage;
        return html;
      }
      return null;
    },
    drawerEnabled() {
      return this.$store.state.drawerEnabled;
    }
  },
  watch: {
    pageId(newValue) {
      if (newValue) {
        this.$store.dispatch('loadPageData', { guid: newValue });
      }
    }
  },
  mounted() {
    this.converter = new showdown.Converter();
  },
  methods: {}
};
</script>

<style scoped>
.current-page {
  padding: 25px;
}
.menu-wrapper {
  min-width: 300px;
  width: 20%;
  padding: 25px;
}
.loading-div {
  padding-top: 100px;
}
.loading-spinner {
  position: absolute;
  font-size: 220px;
  color: #ccc;
}
.loading-logo {
  position: absolute;
  width: 100px;
  margin-left: 57px;
  margin-top: 58px;
}
</style>
