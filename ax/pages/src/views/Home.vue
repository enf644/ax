<template>
  <vue-drawer-layout
    :animatable='true'
    :backdrop='true'
    :backdrop-opacity-range='[0, 0.4]'
    :content-drawable='true'
    :drawer-width='300'
    :enable='drawerEnabled'
    :z-index='0'
    @mask-click='toggleMenu(false)'
    ref='drawer'
  >
    <div class='drawer-content' slot='drawer'>
      <!-- drawer-content -->
      <TheDrawerMenu />
    </div>
    <div class='content-class' slot='content'>
      <!-- main-content -->
      <TheContent />
      <resize-observer @notify='handleResize' />
    </div>
  </vue-drawer-layout>
</template>

<script>
import TheDrawerMenu from '@/components/TheDrawerMenu.vue';
import TheContent from '@/components/TheContent.vue';

export default {
  name: 'Home',
  components: { TheDrawerMenu, TheContent },
  data: () => ({
    guid: null
  }),
  computed: {
    drawerEnabled() {
      return this.$store.state.drawerEnabled;
    }
  },
  watch: {},
  mounted() {
    this.handleResize();
    const pageId = this.$route.params.pagel;
    this.$store.dispatch('loadAllPages', { guid: pageId });
  },
  methods: {
    handleResize() {
      if (this.$el.clientWidth > 768) {
        this.$store.commit('setDrawerEnabled', false);
      } else this.$store.commit('setDrawerEnabled', true);
    },
    toggleMenu(visible) {
      this.$refs.drawer.toggle(visible);
    }
  }
};
</script>

<style scoped>
.content-class {
  height: 100%;
  overflow: auto;
  -webkit-overflow-scrolling: touch;
}
</style>
