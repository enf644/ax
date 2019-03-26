<template>
  <splitpanes class='ax-admin-splits' watch-slots>
    <div class='ax-admin-drawer-first' splitpanes-default='20' splitpanes-min='20'>
      <TheUsersManagerDrawer></TheUsersManagerDrawer>
    </div>
    <div class='ax-admin-drawer-second' splitpanes-default='80' splitpanes-min='50'>
      <TheUsersList></TheUsersList>
    </div>
  </splitpanes>
</template>

<script>
import TheUsersManagerDrawer from '@/components/UsersManager/TheUsersManagerDrawer.vue';
import TheUsersList from '@/components/UsersManager/TheUsersList.vue';
import Splitpanes from 'splitpanes';
import 'splitpanes/dist/splitpanes.css';

export default {
  name: 'users-manager',
  components: {
    TheUsersManagerDrawer,
    TheUsersList,
    Splitpanes
  }
};
</script>

<style scoped>
</style>
