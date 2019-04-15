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
  components: { TheToolbar },
  computed: {
    currentFormDbName() {
      return this.$route.params.db_name;
    },
    redirectNeeded() {
      return this.$store.state.home.redirectNeeded;
    }
  },
  watch: {
    currentFormDbName(newValue) {
      if (newValue) {
        this.$store.dispatch('form/getFormData', { dbName: newValue });
      }
    },
    redirectNeeded(newValue) {
      this.$router.push({ path: newValue });
    }
  },
  created() {
    if (!this.$store.state.home.isFormsLoaded) {
      this.$store.dispatch('home/getAllForms');
      this.$store.dispatch('form/getFieldTypes');
      if (this.$route.params.db_name) {
        this.$store.dispatch('form/getFormData', {
          dbName: this.$route.params.db_name
        });
      }
    }
  }
};
</script>

<style scoped>
</style>
