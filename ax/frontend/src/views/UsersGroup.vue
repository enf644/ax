<template>
  <splitpanes class='ax-admin-splits' watch-slots>
    <div class='ax-admin-drawer-first' splitpanes-min='20' splitpanes-size='20'>
      <TheUsersManagerDrawer></TheUsersManagerDrawer>
    </div>
    <div class='ax-admin-drawer-second' splitpanes-min='50' splitpanes-size='80'>
      <TheUsersGroupContent></TheUsersGroupContent>
    </div>
  </splitpanes>
</template>

<script>
import TheUsersManagerDrawer from '@/components/UsersManager/TheUsersManagerDrawer.vue';
import TheUsersGroupContent from '@/components/UsersManager/TheUsersGroupContent.vue';
import Splitpanes from 'splitpanes';
import 'splitpanes/dist/splitpanes.css';

export default {
  name: 'users-manager',
  components: {
    TheUsersManagerDrawer,
    TheUsersGroupContent,
    Splitpanes
  }
};
</script>

<style scoped>
</style>
