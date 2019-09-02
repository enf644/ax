<template>
  <splitpanes class='ax-admin-splits' watch-slots>
    <div class='ax-admin-drawer-first' splitpanes-min='20' splitpanes-size='20'>
      <TheExplorerDrawer />
    </div>
    <div class='ax-admin-content-pane' splitpanes-min='30' splitpanes-size='80'>
      <TheExplorerContent />
    </div>
  </splitpanes>
</template>


<script>
// import axios from 'axios';
import Splitpanes from 'splitpanes';
import 'splitpanes/dist/splitpanes.css';
import TheExplorerContent from '@/components/GridsExplorer/TheExplorerContent.vue';
import TheExplorerDrawer from '@/components/GridsExplorer/TheExplorerDrawer.vue';

export default {
  name: 'GridsExplorer',
  components: {
    Splitpanes,
    TheExplorerContent,
    TheExplorerDrawer
  },
  data: () => ({}),
  props: {
    source: String
  },
  methods: {},
  created() {}
};
</script>

<style scoped>
</style>
