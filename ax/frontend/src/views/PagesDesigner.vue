<template>
  <splitpanes class='ax-admin-splits' watch-slots>
    <div class='ax-admin-drawer-first' splitpanes-default='20' splitpanes-min='20'>
      <ThePagesDesignerDrawer></ThePagesDesignerDrawer>
    </div>
    <div class='ax-admin-drawer-second' splitpanes-default='80' splitpanes-min='50'>
      <ThePagesDesignerContent></ThePagesDesignerContent>
    </div>
  </splitpanes>
</template>

<script>
import ThePagesDesignerContent from '@/components/PagesDesigner/ThePagesDesignerContent.vue';
import ThePagesDesignerDrawer from '@/components/PagesDesigner/ThePagesDesignerDrawer.vue';
import Splitpanes from 'splitpanes';
import 'splitpanes/dist/splitpanes.css';

export default {
  name: 'deck-designer',
  components: {
    ThePagesDesignerContent,
    ThePagesDesignerDrawer,
    Splitpanes
  }
};
</script>

<style scoped>
</style>
