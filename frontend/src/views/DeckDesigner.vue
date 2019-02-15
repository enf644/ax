<template>
  <splitpanes class='ax-admin-splits' watch-slots>
    <div class='ax-admin-drawer-first' splitpanes-default='20' splitpanes-min='20'>
      <TheDeckDesignerDrawer></TheDeckDesignerDrawer>
    </div>
    <div class='ax-admin-drawer-second' splitpanes-default='80' splitpanes-min='50'>
      <TheDeckDesignerContent></TheDeckDesignerContent>
    </div>
  </splitpanes>
</template>

<script>
import TheDeckDesignerContent from '@/components/DeckDesigner/TheDeckDesignerContent.vue';
import TheDeckDesignerDrawer from '@/components/DeckDesigner/TheDeckDesignerDrawer.vue';
import Splitpanes from 'splitpanes';

export default {
  name: 'deck-designer',
  components: {
    TheDeckDesignerContent,
    TheDeckDesignerDrawer,
    Splitpanes
  }
};
</script>

<style scoped>
</style>
