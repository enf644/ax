<template>
  <splitpanes @resized='redrawMonaco()' class='ax-admin-splits' watch-slots>
    <div class='ax-admin-drawer-first' splitpanes-min='20' splitpanes-size='20'>
      <ThePagesDesignerDrawerFirst></ThePagesDesignerDrawerFirst>
    </div>
    <div class='ax-admin-content-pane' splitpanes-min='30' splitpanes-size='40'>
      <ThePagesDesignerDrawerSecond ref='monacoDrawer'></ThePagesDesignerDrawerSecond>
    </div>
    <div class='ax-admin-content-pane page-preview' splitpanes-min='30' splitpanes-size='40'>
      <ThePagesDesignerContent></ThePagesDesignerContent>
    </div>
  </splitpanes>
</template>

<script>
import ThePagesDesignerContent from '@/components/PagesDesigner/ThePagesDesignerContent.vue';
import ThePagesDesignerDrawerFirst from '@/components/PagesDesigner/ThePagesDesignerDrawerFirst.vue';
import ThePagesDesignerDrawerSecond from '@/components/PagesDesigner/ThePagesDesignerDrawerSecond.vue';
import Splitpanes from 'splitpanes';
import 'splitpanes/dist/splitpanes.css';

export default {
  name: 'pages-designer',
  components: {
    ThePagesDesignerContent,
    ThePagesDesignerDrawerFirst,
    ThePagesDesignerDrawerSecond,
    Splitpanes
  },
  methods: {
    redrawMonaco() {
      this.$refs.monacoDrawer.handleResize();
    }
  }
};
</script>

<style scoped>
.page-preview {
  padding: 25px;
  background: #fff;
}
</style>
