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
    currentGridDbName() {
      return this.$route.params.grid_alias;
    },
    redirectNeededUrl() {
      return this.$store.state.home.redirectNeededUrl;
    }
  },
  watch: {
    currentFormDbName(newValue) {
      if (newValue) {
        this.$store.dispatch('form/getFormData', {
          dbName: newValue,
          updateTime: Date.now()
        });
      }
    },
    currentGridDbName(newValue) {
      if (newValue) {
        this.$store.dispatch('grids/getGridData', {
          formDbName: this.$route.params.db_name,
          gridDbName: newValue,
          updateTime: Date.now()
        });
        this.$store.commit('grids/setFormDbName', this.currentFormDbName);
      }
    },
    redirectNeededUrl(newValue) {
      this.$router.push({ path: newValue });
    }
  },
  created() {
    if (!this.$store.state.home.isFormsLoaded) {
      this.$store.dispatch('home/getAllForms');
      this.$store.dispatch('form/getFieldTypes');
      if (this.$route.params.db_name) {
        this.$store.dispatch('form/getFormData', {
          dbName: this.$route.params.db_name,
          updateTime: Date.now()
        });
      }
      if (this.$route.params.grid_alias) {
        this.$store.dispatch('grids/getGridData', {
          formDbName: this.$route.params.db_name,
          gridDbName: this.$route.params.grid_alias,
          updateTime: Date.now()
        });
        this.$store.commit('grids/setFormDbName', this.currentFormDbName);
      }
    }
  }
};
</script>

<style scoped>
</style>
