<template>
  <v-toolbar app class='top-toolbar' clipped-left fixed height='40'>
    <v-toolbar-title align-center>
      <router-link to='/admin/home'>
        <!-- <i class='fab fa-fantasy-flight-games logo'></i> -->
        <font-awesome-icon class='logo' icon='hammer'/>
      </router-link>
    </v-toolbar-title>

    <v-layout align-center class='breadcrumbs' fill-height justify-start>
      <div>Ax</div>

      <font-awesome-icon class='breadcrumb-devider' icon='angle-right'/>
      <span href='#'>
        <font-awesome-icon class='breadcrumbs-ico' icon='brain'/>Bank RFC
        <font-awesome-icon class='breadcrumbs-action' icon='cog'/>
      </span>
      <font-awesome-icon class='breadcrumb-devider' icon='angle-right'/>
      <a>Grid constructor</a>
      <font-awesome-icon class='breadcrumb-devider' icon='angle-right'/>
      <div class='grid-select'>
        Default grid
        <span class='very-small'>total: 4</span>
        <i class='fas fa-caret-down'></i>
      </div>
      <font-awesome-icon class='breadcrumbs-action' icon='cog'/>
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
export default {
  name: 'admin-toolbar'
};
</script>

<style scoped>
.logo {
  height: 20px;
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
  margin-left: 5px;
  color: #c0c0c0;
  cursor: pointer;
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
