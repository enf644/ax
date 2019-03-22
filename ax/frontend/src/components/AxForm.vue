<template>
  <v-app class='ax-form-app' id='ax-form'>
    <v-sheet
      :class='no_margin ? "form-container-no-margin" : "form-container"'
      elevation='5'
      light
      ref='sheet'
    >
      <v-layout align-space-between class='form-layout' justify-start row>
        <div
          :class='{
            "drawer-floating": drawerIsFloating,
            "drawer-hidden": drawerIsHidden
          }'
          class='drawer'
        >
          <v-list class='drawer-folder-list'>
            <v-list-tile
              :key='folder.title'
              @click='openFolder(folder.title)'
              class='drawer-folder-list-tile'
              ripple
              v-bind:class='{ "drawer-folder-active": folder.isActive }'
              v-for='folder in folders'
            >
              <v-list-tile-content class='drawer-folder-item'>
                <v-list-tile-title>{{ folder.title }}</v-list-tile-title>
              </v-list-tile-content>
            </v-list-tile>
          </v-list>
        </div>
        <div class='form'>
          <div
            @click='hideDrawer'
            class='overlay'
            id='overlay'
            v-bind:class='{ "hidden": overlayIsHidden }'
          ></div>
          <div class='header'>
            <v-btn
              @click='toggleDrawer'
              class='drawer-toggle'
              fab
              small
              v-bind:class='{ "hidden": !drawerIsFloating }'
            >
              <font-awesome-icon icon='bars'/>
            </v-btn>
            <i class='fas fa-brain'></i> &nbsp; Bank RFC
            <resize-observer @notify='handleResize'/>
          </div>
          <div class='content'>
            <v-container fluid grid-list-xl>
              <v-layout align-center justify-center row wrap>
                <v-flex>
                  <div class='ax-field'>
                    <v-text-field label='First Name'></v-text-field>
                  </div>
                </v-flex>
                <v-flex>
                  <div class='ax-field'>
                    <v-text-field label='Last Name'></v-text-field>
                  </div>
                </v-flex>
                <v-flex>
                  <div class='ax-field'>
                    <v-text-field label='E-mail'></v-text-field>
                  </div>
                </v-flex>
                <v-flex>
                  <div class='ax-field'>
                    <v-text-field label='Address'></v-text-field>
                  </div>
                </v-flex>
                <v-btn @click='openForm()' color='primary' outline>text</v-btn>
              </v-layout>
            </v-container>

            <p v-dummy='1500'></p>
          </div>
        </div>
      </v-layout>
    </v-sheet>

    <!-- <v-dialog class='dialog' lazy max-width='70%' scrollable v-model='dialogIsOpen'>
      <v-card>
        <AxForm no_margin></AxForm>
      </v-card>
    </v-dialog>-->
    <modal :pivotX='0.52' adaptive height='auto' name='sub-form' scrollable width='70%'>
      <v-card>
        <AxForm no_margin></AxForm>
      </v-card>
    </modal>
  </v-app>
</template>

<script>
// import AxGrid from './AxGrid.vue';

export default {
  name: 'AxForm',
  components: {},
  props: {
    no_margin: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      drawerIsFloating: false,
      drawerIsHidden: false,
      overlayIsHidden: true,
      dialogIsOpen: false,
      folders: [
        { title: 'Home1', isActive: true },
        { title: 'About' },
        { title: 'Active members' },
        { title: 'Realy long name that will break your menu' },
        { title: 'Do it later' },
        { title: 'Wim Hof' }
      ]
    };
  },
  created() {},
  mounted() {
    this.$nextTick(() => {
      this.handleResize();
    });
  },
  methods: {
    openForm() {
      this.$log.info(' OPEN FORM');
      this.$modal.show('sub-form');

      // this.dialogIsOpen = true;
      // this.$modal.show(AxForm);
      // this.$modal.show({
      //   template: '<AxForm no_margin />'
      // });
    },
    openFolder(_id) {
      this.$log.info(`Open folder - ${_id}`);
    },
    handleResize() {
      const currentWidth = this.$el.clientWidth;
      const breakingPoint = 800;

      if (this.drawerIsFloating === false && currentWidth < breakingPoint) {
        this.drawerIsFloating = true;
        this.drawerIsHidden = true;
        this.overlayIsHidden = true;
      }

      if (this.drawerIsFloating === true && currentWidth > breakingPoint) {
        this.drawerIsFloating = false;
        this.drawerIsHidden = false;
        this.overlayIsHidden = true;
      }
    },
    toggleDrawer() {
      if (this.drawerIsFloating && this.drawerIsHidden) {
        this.drawerIsHidden = false;
        this.overlayIsHidden = false;
      } else if (this.drawerIsFloating && this.drawerIsHidden === false) {
        this.drawerIsHidden = true;
        this.overlayIsHidden = true;
      }
    },
    hideDrawer() {
      if (this.drawerIsFloating === true && this.drawerIsHidden === false) {
        this.drawerIsHidden = true;
        this.overlayIsHidden = true;
      }
    }
  }
};
</script>

<style scoped>
.drawer {
  min-width: 255px;
  border-right: 1px solid #cccccc;
  background: #fafafa;
  margin-left: 0px;
  animation: slideIn 200ms 1 ease forwards;
  z-index: 5;
}
@keyframes slideIn {
  0% {
    margin-left: -255px;
  }
  100% {
    margin-left: -0px;
  }
}
.drawer-floating {
  position: absolute;
  height: 100%;
}
.drawer-hidden {
  margin-left: -255px;
  animation: slideOut 300ms ease forwards;
}
@keyframes slideOut {
  0% {
    margin-left: 0px;
  }
  99% {
    margin-left: -254px;
    left: auto;
  }
  100% {
    margin-left: -255px;
    opacity: 0;
    left: -255px;
  }
}
.drawer-toggle {
  margin: 0px 25px 15px 0px;
}
.drawer-folder-list {
  background: #fafafa !important;
}

.drawer-folder-item {
  padding: 0px 10px 0px 10px;
}
.drawer-folder-active {
  background: #cccccc;
}
.overlay {
  position: absolute;
  width: 100%;
  height: 100%;
  background: black;
  opacity: 0.5;
  z-index: 1;
}
.hidden {
  display: none;
}
.form-layout {
  min-height: 300px;
}
.header {
  font-size: 1.2em;
  height: 40px;
  line-height: 40px;
  vertical-align: middle;
  padding-left: 25px;
  margin-top: 25px;
}
.content {
  padding: 10px 25px 25px 25px;
}
.ax-field {
  min-width: 240px;
}
.form-container {
  margin: 20px;
}
.form-container-no-margin {
  margin: 0px;
}
</style>
