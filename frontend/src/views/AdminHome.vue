<template>
  <v-app id='ax-admin'>
    <v-toolbar height='40' clipped-left fixed app>
      <v-toolbar-title align-center>
        <i class='fab fa-fantasy-flight-games logo'></i>
      </v-toolbar-title>

      <!-- <div class='breadcrumbs'> -->
      <v-layout class='breadcrumbs' align-center justify-start fill-height>
        <div>Ax</div>

        <span class='fas fa-angle-right breadcrumb-devider'></span>
        <span href='#'>
          <i class='fas fa-brain breadcrumbs-ico'></i>
          Bank RFC
          <i class='fas fa-cog breadcrumbs-action'></i>
        </span>
        
        <i class='fas fa-angle-right breadcrumb-devider'></i>
        <a>Grid constructor</a>
        
        <span class='fas fa-angle-right breadcrumb-devider'></span>
        <div class='grid-select'>
          Default grid
          <span class='very-small'>total: 4</span>
          <i class='fas fa-caret-down'></i>
        </div>
        <i class='fas fa-cog breadcrumbs-action'></i>
      </v-layout>
      <!-- </div> -->
      <v-spacer></v-spacer>

      <v-toolbar-items class='hidden-sm-and-down'>
        <v-btn color='success'>Form</v-btn>
        <v-btn>Workflow</v-btn>
        <v-btn>Grid</v-btn>

        <v-avatar class='logout' slot='activator' size='27px'>
          <img src='https://avatars0.githubusercontent.com/u/9064066?v=4&s=460'>
        </v-avatar>
      </v-toolbar-items>
    </v-toolbar>
    <v-content>
      <splitpanes class='splits'>
        <div splitpanes-default='20' splitpanes-min='20' class='drawer-first'>
          <p v-dummy='5'></p>
        </div>
        <div splitpanes-default='20' splitpanes-min='20' class='drawer-second'>
          <p v-dummy='350'></p>
        </div>
        <div splitpanes-default='60' class='content-pane'>
          <v-sheet light class='form-container' elevation='5'>
            <AxForm></AxForm>
          </v-sheet>
        </div>
      </splitpanes>
    </v-content>
  </v-app>
</template>


<script>
import axios from 'axios';
import AxForm from '@/components/AxForm.vue';
import Splitpanes from 'splitpanes';
import 'splitpanes/dist/splitpanes.css';
// import VJstree from 'vue-jstree';

export default {
  name: 'home',
  components: {
    AxForm,
    Splitpanes
  },
  data: () => ({
    drawer: null,
    dialog2: false,
    dialog3: false,
    constructor_grid_items: ['Default', 'Foo', 'Bar', 'Fizz', 'Buzz']
  }),
  props: {
    source: String
  },
  methods: {},
  created: function() {
    console.log('running ajax');
    axios
      .get('/api/hello', {
        params: {
          object_id: 12349
        }
      })
      .then(function(response) {
        console.log(response);
      })
      .catch(function(error) {
        console.log(error);
      })
      .then(function() {
        // always executed
      });
  }
};
</script>

<style scoped>
.logo {
  font-size: 1.3em;
}
.first-drawer {
  width: 255px;
  padding: 20px;
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
  margin-top: 6px;
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

.panes {
  width: 100%;
  height: 100%;
}

.drawer-first {
  background: #ffffff;
  height: 100%;
  padding: 25px;
  overflow: auto;
}
.drawer-second {
  background: #ffffff;
  height: 100%;
  padding: 25px;
  overflow: auto;
}
.content-pane {
}

.form-container {
  margin: 20px;
}
.splits {
  height: 100%;
  position: absolute;
}
</style>
