<template>
  <splitpanes class='ax-admin-splits' watch-slots>
    <div class='ax-admin-drawer-first' splitpanes-min='20' splitpanes-size='20'>
      <TheUsersManagerDrawer></TheUsersManagerDrawer>
    </div>
    <div class='ax-admin-drawer-second' splitpanes-min='50' splitpanes-size='80'>
      <TheUsersList v-if='isBlockedList == false'></TheUsersList>
      <TheBlockedUsersList v-if='isBlockedList'></TheBlockedUsersList>
    </div>
  </splitpanes>
</template>

<script>
import TheUsersManagerDrawer from '@/components/UsersManager/TheUsersManagerDrawer.vue';
import TheUsersList from '@/components/UsersManager/TheUsersList.vue';
import TheBlockedUsersList from '@/components/UsersManager/TheBlockedUsersList.vue';
import Splitpanes from 'splitpanes';
import 'splitpanes/dist/splitpanes.css';

export default {
  name: 'users-manager',
  components: {
    TheUsersManagerDrawer,
    TheUsersList,
    TheBlockedUsersList,
    Splitpanes
  },
  computed: {
    isBlockedList() {
      if (this.$route.name == 'blocked-users-manager') return true;
      return false;
    }
  },
  mounted() {}
};
</script>

<style scoped>
</style>
