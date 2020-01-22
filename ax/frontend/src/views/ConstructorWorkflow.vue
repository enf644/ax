<template>
  <splitpanes class='ax-admin-splits' watch-slots>
    <div
      class='ax-admin-drawer-first workflow-first'
      splitpanes-max='20'
      splitpanes-min='20'
      splitpanes-size='20'
    >
      <TheConstructorWorkflowDrawer></TheConstructorWorkflowDrawer>
    </div>
    <div class='ax-admin-content-pane' splitpanes-min='50' splitpanes-size='80'>
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
.workflow-first {
  min-width: 230px;
}
</style>
