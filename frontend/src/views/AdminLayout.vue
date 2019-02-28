<template>
  <v-app id='ax-admin'>
    <TheToolbar></TheToolbar>
    <v-content>
      <transition enter-active-class='animated fadeIn faster' name='fade'>
        <router-view></router-view>
      </transition>
    </v-content>
  </v-app>
</template>

<script>
import TheToolbar from '@/components/AdminHome/TheToolbar.vue';

export default {
  name: 'admin-layout',
  components: { TheToolbar }
};
</script>

<style scoped>
</style>
