<template>
  <v-toolbar app class='top-toolbar' clipped-left fixed height='40'>
    <v-toolbar-title align-center>
      <router-link to='/admin/home'>
        <i class='fas fa-tools logo'></i>
      </router-link>
    </v-toolbar-title>

    <v-layout align-center class='breadcrumbs' fill-height justify-start>
      <div>Ax</div>

      <span cy-data='current-form-breadcrumb' href='#' v-show='currentFormDbName'>
        <i class='fas fa-angle-right breadcrumb-devider'></i>
        <i :class='[currentFormIconClass]'></i>
        {{this.currentFormName}}
        <v-btn
          @click='openFormModal'
          class='breadcrumbs-action'
          color='black'
          cy-data='update-form-btn'
          flat
          icon
        >
          <i class='fas fa-cog breadcrumbs-action-i'></i>
        </v-btn>
      </span>

      <modal adaptive height='auto' name='update-form' scrollable>
        <TheNewForm :guid='this.$store.state.form.guid' @created='closeFormModal'/>
      </modal>

      <!--
      <i class='fas fa-angle-right breadcrumb-devider'></i>
      <a>Grid constructor</a>
      <i class='fas fa-angle-right breadcrumb-devider'></i>
      <div class='grid-select'>
        Default grid
        <span class='very-small'>total: 4</span>
        <i class='fas fa-caret-down'></i>
      </div>
      <i class='fas fa-cog breadcrumbs-action'></i>-->
    </v-layout>
    <v-spacer></v-spacer>
    <transition enter-active-class='animated fadeIn faster' name='fade'>
      <v-toolbar-items class='hidden-sm-and-down' v-if='this.$route.params.db_name'>
        <v-btn :to='"/admin/" + this.$route.params.db_name + "/form"' color='success'>Form</v-btn>
        <v-btn :to='"/admin/" + this.$route.params.db_name + "/workflow"'>Workflow</v-btn>
        <v-btn :to='"/admin/" + this.$route.params.db_name + "/grids/default"'>Grid</v-btn>
      </v-toolbar-items>
    </transition>
    <div>
      <v-avatar class='logout' size='27px' slot='activator'>
        <img src='https://avatars0.githubusercontent.com/u/9064066?v=4&s=460'>
      </v-avatar>
    </div>
  </v-toolbar>
</template>

<script>
import TheNewForm from '@/components/AdminHome/TheNewForm.vue';

export default {
  name: 'admin-toolbar',
  components: {
    TheNewForm
  },
  computed: {
    currentFormDbName() {
      return this.$route.params.db_name;
    },
    currentFormIconClass() {
      if (this.currentForm) {
        return `breadcrumbs-ico fas fa-${this.currentForm.icon}`;
      }
      return null;
    },
    currentForm() {
      return this.$store.state.home.forms.find(
        x => x.dbName === this.$route.params.db_name
      );
    },
    currentFormName() {
      if (this.currentForm) return this.currentForm.name;
      return null;
    }
  },
  methods: {
    openFormModal() {
      this.$modal.show('update-form');
    },
    closeFormModal() {
      this.$modal.hide('update-form');
    }
  }
};
</script>

<style scoped>
.logo {
  height: 20px;
  color: #333333;
}
.breadcrumbs {
  margin-left: 20px;
}
.breadcrumbs a {
  color: initial;
}
.breadcrumb-devider {
  margin: 0px 30px 0px 30px;
  color: #c0c0c0;
}
.breadcrumbs-ico {
  margin-right: 5px;
}
.breadcrumbs-action {
  margin: 0;
  width: 25px;
  height: 25px;
}

.breadcrumbs-action-i {
  color: #c0c0c0;
}

.breadcrumbs a {
  text-decoration: none;
  cursor: pointer;
}

.breadcrumb-dropdown {
  margin-left: 10px;
}

.logout {
  margin-left: 20px;
  cursor: pointer;
}

.grid-select {
  border-bottom: 1px solid #c0c0c0;
  margin-bottom: 3px;
  margin-right: 10px;
  cursor: pointer;
}
.grid-select i {
  margin-left: 5px;
  font-size: 1.5em;
}
.very-small {
  font-size: 0.7em;
  margin-left: 5px;
}
.top-toolbar {
  z-index: 100;
}
</style>
