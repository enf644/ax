<template>
  <v-app id='ax-admin'>
    <TheToolbar></TheToolbar>
    <v-content class='content'>
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
    },
    authToken() {
      return this.$store.state.auth.accessToken;
    }
  },
  watch: {
    authToken(newValue) {
      if (newValue == null || newValue == 'null') {
        this.checkAuth(newValue);
      }
    },
    currentFormDbName(newValue) {
      let title = '';
      if (newValue) title = `[${newValue}] `;

      document.title = `${title}Ax workflow app constructor`;
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
        this.$store.commit('grids/setFormDbName', this.$route.params.db_name);
      }
    },
    redirectNeededUrl(newValue) {
      if (newValue) {
        this.$router.push({ path: newValue });
        this.$store.commit('home/setRedirectNeededUrl', null);
      }
    }
  },
  created() {
    this.checkAuth(this.$store.state.auth.accessToken);

    if (!this.$store.state.home.isFormsLoaded) {
      this.$store.dispatch('home/getAllForms', {
        updateTime: Date.now()
      });
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
  },
  methods: {
    checkAuth(accessToken) {
      if (accessToken == null || accessToken == 'null') {
        const fromUrl = this.$route.fullPath;
        this.$store.commit('home/setRedirectFromUrl', fromUrl);
        setTimeout(() => {
          const url = `/signin`;
          this.$router.push({ path: url });
        }, 100);
      }
    }
  }
};
</script>

<style scoped>
</style>
