<template>
  <v-app-bar :height='40' app class='top-toolbar' clipped-left>
    <v-toolbar-title align-center class='logo-div'>
      <router-link to='/admin/home'>
        <img class='logo' src='../../assets/small_axe.png' />
      </router-link>
    </v-toolbar-title>

    <!-- <v-row no-gutters class='breadcrumbs'> -->
    <div class='buttons-div'>
      <v-btn
        :disabled='isNotConstructorPath'
        :to='"/admin/" + this.$route.params.db_name + "/form"'
        class='constructor-button'
        small
        text
      >
        <i class='fab fa-wpforms'></i>
        &nbsp; {{$t("home.toolbar.form-btn")}}
      </v-btn>
      <v-btn
        :disabled='isNotConstructorPath'
        :to='"/admin/" + this.$route.params.db_name + "/workflow"'
        class='constructor-button'
        small
        text
      >
        <i class='fas fa-project-diagram'></i>
        &nbsp; {{$t("home.toolbar.workflow-btn")}}
      </v-btn>
      <v-btn
        :disabled='isNotConstructorPath'
        :to='"/admin/" + this.$route.params.db_name + "/grids/" + defaultGridDbName'
        class='constructor-button'
        small
        text
      >
        <i class='fas fa-columns'></i>
        &nbsp; {{$t("home.toolbar.grids-btn")}}
      </v-btn>
    </div>

    <div
      class='current-form-breadcrumb'
      cy-data='current-form-breadcrumb'
      id='grids-toolbar'
      v-show='currentFormDbName'
    >
      <i class='fas fa-angle-right breadcrumb-devider'></i>
      <i :class='[currentFormIconClass]'></i>
      {{this.currentFormName}}
      <v-btn
        @click='openFormModal'
        class='breadcrumbs-action'
        color='black'
        cy-data='update-form-btn'
        icon
        text
      >
        <i class='fas fa-cog breadcrumbs-action-i'></i>
      </v-btn>
    </div>

    <modal adaptive height='auto' name='update-form' scrollable>
      <TheNewForm :guid='this.$store.state.form.guid' @created='closeFormModal' />
    </modal>

    <v-menu offset-y>
      <template v-slot:activator='{ on }'>
        <v-btn
          @click='openGridModal'
          class='breadcrumbs-action'
          color='black'
          cy-data
          icon
          text
          v-show='isGridsRoute'
        >
          <i class='fas fa-cog breadcrumbs-action-i'></i>
        </v-btn>

        <div class='grid-select' v-on='on' v-show='isGridsRoute'>
          {{currentGridName}}
          <span class='very-small'>total: {{totalGrids}}</span>
          <i class='fas fa-caret-down'></i>
        </div>
        <i class='fas fa-angle-right breadcrumb-devider' v-show='isGridsRoute'></i>
      </template>
      <v-card class='grids-card'>
        <v-list>
          <v-list-item
            :key='index'
            @click='gotoGrid(grid.dbName)'
            v-for='(grid, index) in allGrids'
          >
            <v-list-item-title>
              {{ grid.name }}
              &nbsp;
              <i class='far fa-star' v-show='grid.isDefaultView'></i>
            </v-list-item-title>
          </v-list-item>
        </v-list>

        <v-btn @click='createGrid' small>
          <i class='fas fa-plus'></i>
          &nbsp;
          {{$t("home.create-new-grid-btn")}}
        </v-btn>
      </v-card>
    </v-menu>

    <modal adaptive height='auto' name='update-grid' scrollable>
      <TheGridModal :guid='this.$store.state.grids.guid' @updated='closeGridModal' />
    </modal>

    <v-spacer></v-spacer>
    <transition enter-active-class='animated fadeIn faster' name='fade'></transition>
    <div>
      <v-avatar class='logout' size='27px' slot='activator'>
        <img src='https://avatars0.githubusercontent.com/u/9064066?v=4&s=460' />
      </v-avatar>
    </div>
  </v-app-bar>
</template>

<script>
import TheNewForm from '@/components/AdminHome/TheNewForm.vue';
import TheGridModal from '@/components/ConstructorGrids/TheGridModal.vue';

export default {
  name: 'admin-toolbar',
  components: {
    TheNewForm,
    TheGridModal
  },
  computed: {
    allGrids() {
      const gridsList = [...this.$store.state.form.grids];
      return gridsList.sort((a, b) => a.name.localeCompare(b.name));
    },
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
    },
    currentGridName() {
      const { name } = this.$store.state.grids;
      if (!name) return this.defaultGridDbName;
      return this.$store.state.grids.name;
    },
    defaultGridDbName() {
      const defaultGrid = this.$store.state.form.grids.find(
        grid => grid.isDefaultView === true
      );
      return defaultGrid ? defaultGrid.dbName : null;
    },
    isNotConstructorPath() {
      if (this.currentFormDbName) return false;
      return true;
    },
    isFormRoute() {
      return this.$route.path.includes('/form');
    },
    isWorkflowRoute() {
      return this.$route.path.includes('/workflow');
    },
    isGridsRoute() {
      return this.$route.path.includes('/grids');
    },
    totalGrids() {
      return this.$store.state.form.grids.length;
    },
    defaultGridName() {
      const defGrid = this.$store.state.form.grids.find(
        grid => grid.isDefaultView === true
      );
      if (defGrid) return defGrid.name;
      return null;
    }
  },
  methods: {
    gotoGrid(dbName) {
      const url = `/admin/${this.currentFormDbName}/grids/${dbName}`;
      this.$store.commit('home/setRedirectNeededUrl', url);
    },
    createGrid() {
      this.$store.dispatch('grids/createGrid').then(() => {
        const msg = this.$t('grids.grid-created-toast');
        this.$dialog.message.success(
          `<i class="fas fa-columns"></i> &nbsp ${msg}`
        );
      });
    },
    openGridModal() {
      this.$modal.show('update-grid');
    },
    closeGridModal() {
      this.$modal.hide('update-grid');
    },
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
.breadcrumbs a {
  color: initial;
}
.breadcrumb-devider {
  margin: 0px 30px 0px 30px;
  color: #eee;
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
.buttons-div {
  vertical-align: middle;
  line-height: 25px;
  /* margin-left: 60px; */
  margin-right: 20px;
  padding-right: 20px;
  /* background: #eee; */
  white-space: nowrap;
}
.constructor-button {
  margin-left: 10px !important;
}
.logo {
  height: 25px;
  margin-top: 6px;
  margin-left: 25px;
}
.grids-card {
  padding: 20px;
}
.current-form-breadcrumb {
  white-space: nowrap;
}
.logo-div {
  width: 10%;
}
</style>
