<template>
  <splitpanes class='ax-admin-splits' watch-slots>
    <div class='ax-admin-drawer-first' splitpanes-default='20' splitpanes-min='20'>
      <TheConstructorWorkflowDrawer></TheConstructorWorkflowDrawer>
    </div>
    <div class='ax-admin-drawer-second' splitpanes-default='80' splitpanes-min='50'>
      <TheConstructorWorkflowContent></TheConstructorWorkflowContent>
    </div>
  </splitpanes>
</template>

<script>
import TheConstructorWorkflowContent from '@/components/ConstructorWorkflow/TheConstructorWorkflowContent.vue';
import TheConstructorWorkflowDrawer from '@/components/ConstructorWorkflow/TheConstructorWorkflowDrawer.vue';
import Splitpanes from 'splitpanes';
import 'splitpanes/dist/splitpanes.css';

export default {
  name: 'constructor-workflow',
  components: {
    TheConstructorWorkflowContent,
    TheConstructorWorkflowDrawer,
    Splitpanes
  }
};
</script>

<style scoped>
</style>
