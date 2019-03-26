<template>
  <splitpanes class='ax-admin-splits' watch-slots>
    <div class='ax-admin-drawer-first' splitpanes-default='20' splitpanes-min='20'>
      <TheConstructorGridsDrawerFirst></TheConstructorGridsDrawerFirst>
    </div>
    <div class='ax-admin-drawer-second' splitpanes-default='20' splitpanes-min='20'>
      <TheConstructorGridsDrawerSecond></TheConstructorGridsDrawerSecond>
    </div>
    <div class='ax-admin-content-pane' splitpanes-default='60' splitpanes-min='30'>
      <TheConstructorGridsContent></TheConstructorGridsContent>
    </div>
  </splitpanes>
</template>

<script>
import TheConstructorGridsContent from '@/components/ConstructorGrids/TheConstructorGridsContent.vue';
import TheConstructorGridsDrawerFirst from '@/components/ConstructorGrids/TheConstructorGridsDrawerFirst.vue';
import TheConstructorGridsDrawerSecond from '@/components/ConstructorGrids/TheConstructorGridsDrawerSecond.vue';
import Splitpanes from 'splitpanes';
import 'splitpanes/dist/splitpanes.css';

export default {
  name: 'constructor-grids',
  components: {
    TheConstructorGridsDrawerFirst,
    TheConstructorGridsDrawerSecond,
    TheConstructorGridsContent,
    Splitpanes
  }
};
</script>

<style scoped>
</style>
