<template>
  <v-app class='ax-form-app' id='ax-form' ref='formApp'>
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
          v-show='!drawerIsHidden'
        >
          <v-list class='drawer-folder-list'>
            <v-list-tile
              :class='getTabClass(tab.guid)'
              :key='tab.guid'
              @click='openTab(tab.guid)'
              avatar
              ripple
              v-for='tab in tabs'
            >
              <v-list-tile-content class='drawer-folder-item'>
                <v-list-tile-title>{{ tab.name }}</v-list-tile-title>
              </v-list-tile-content>
              <v-list-tile-avatar>
                <transition
                  enter-active-class='animated flipInY'
                  leave-active-class='animated flipOutY'
                >
                  <div class='tab-errors' v-show='tab.errors'>{{tab.errors}}</div>
                </transition>
              </v-list-tile-avatar>
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
            <v-badge
              class='drawer-toggle'
              color='red'
              overlap
              v-bind:class='{ "hidden": !drawerIsFloating }'
              v-model='formIsNotValid'
            >
              <template v-slot:badge>
                <span class='drawer-toggle-errors'>{{errorsCount}}</span>
              </template>
              <v-btn @click='toggleDrawer' fab small>
                <i class='fas fa-bars'></i>
              </v-btn>
            </v-badge>
            <i :class='iconClass'></i>
            &nbsp; {{name}}
            <resize-observer @notify='handleResize'/>
          </div>
          <v-container fluid grid-list-xl>
            <v-layout align-center justify-center row wrap>
              <AxField
                :dbName='field.dbName'
                :isRequired='field.isRequired'
                :isWholeRow='field.isWholeRow'
                :key='field.guid'
                :name='field.name'
                :optionsJson='field.optionsJson'
                :ref='getFieldRef(field.guid)'
                :tag='field.fieldType.tag'
                :value.sync='field.value'
                @update:value='updateValue'
                v-for='field in this.fields'
                v-show='isFieldVisible(field)'
              ></AxField>

              <v-flex xs12>
                <v-btn :disabled='!formIsValid' @click='submitTest' small>
                  <i class='fas fa-vial'></i>
                  &nbsp; {{$t("form.test-from")}}
                </v-btn>
                <!-- <v-btn @click='openForm()' color='primary' outline>text</v-btn> -->
              </v-flex>
            </v-layout>
          </v-container>
        </div>
      </v-layout>
    </v-sheet>
    <modal adaptive height='auto' name='test-value' scrollable width='50%'>
      <v-card class='test-value'>
        <pre>{{value}}</pre>
      </v-card>
    </modal>

    <modal :pivotX='0.52' adaptive height='auto' name='sub-form' scrollable width='70%'>
      <v-card>
        <AxForm no_margin></AxForm>
      </v-card>
    </modal>
  </v-app>
</template>

<script>
// import AxGrid from './AxGrid.vue';
import smoothReflow from 'vue-smooth-reflow';
import apolloClient from '../apollo';
import AxField from '@/components/AxField.vue';
import gql from 'graphql-tag';

export default {
  name: 'AxForm',
  mixins: [smoothReflow],
  components: { AxField },
  props: {
    no_margin: {
      type: Boolean,
      default: false
    },
    db_name: {
      type: String,
      default: null
    },
    row_guid: {},
    update_time: null,
    opened_tab: null
  },
  data() {
    return {
      drawerIsFloating: false,
      drawerIsHidden: true,
      overlayIsHidden: true,
      dialogIsOpen: false,
      guid: null,
      name: null,
      dbName: null,
      icon: null,
      tabs: [],
      fields: [],
      actions: [],
      currentTabGuid: null,
      tabFields: [],
      activeTab: null,
      value: null,
      formIsValid: true,
      errorsCount: 0,
      currentWidth: null
    };
  },
  computed: {
    iconClass() {
      return `fas fa-${this.icon}`;
    },
    formIsNotValid() {
      return !this.formIsValid;
    }
  },
  watch: {
    db_name(newValue) {
      if (newValue) this.loadData(newValue);
    },
    update_time() {
      if (this.db_name) this.loadData(this.db_name);
    },
    tabs(newValue, oldValue) {
      if (oldValue) {
        this.drawerIsFloating = true;
        this.drawerIsHidden = true;
        this.overlayIsHidden = true;
      }
      this.handleResize(true);
    }
  },
  created() {},
  mounted() {
    if (this.db_name) this.loadData(this.db_name);
    // setTimeout(() => {
    //   this.handleResize();
    // }, 30);
    this.$smoothReflow({ el: this.$refs.sheet.$el });
  },
  methods: {
    updateValue() {
      const result = {};
      this.fields.forEach(field => {
        result[field.dbName] = field.value;
      });
      this.value = result;
      this.$emit('update:value', result);
      if (!this.formIsValid) this.isValid();
    },
    isValid() {
      let formIsValid = true;
      const tabErrors = {};
      let errorsCount = 0;

      // Validate each field
      this.fields.forEach(field => {
        const ref = this.getFieldRef(field.guid);
        if (this.$refs[ref]) {
          const fieldObject = this.$refs[ref][0];
          if (fieldObject.isValid() === false) {
            // TODO: error counter on tabs
            if (!tabErrors[field.parent]) tabErrors[field.parent] = 1;
            else tabErrors[field.parent] += 1;
            formIsValid = false;
          }
        }
      });

      for (let index = 0; index < this.tabs.length; index += 1) {
        const tab = this.tabs[index];
        if (tabErrors[tab.guid]) {
          tab.errors = tabErrors[tab.guid];
          errorsCount += tabErrors[tab.guid];
        } else tab.errors = 0;
      }

      this.errorsCount = errorsCount;
      this.formIsValid = formIsValid;
      return formIsValid;
    },
    submitTest() {
      this.isValid();
      if (this.formIsValid) this.$modal.show('test-value');
    },
    getFieldRef(guid) {
      return `field-${guid}`;
    },
    isFieldVisible(field) {
      if (field.parent === this.activeTab) return true;
      return false;
    },
    getTabClass(tabGUid) {
      let retClass = 'drawer-folder-list-tile';
      if (this.activeTab === tabGUid) retClass += ' highlighted';
      return retClass;
    },
    openTab(guid) {
      this.activeTab = guid;
      this.$emit('update:tab', guid);
      this.hideDrawer();
    },
    loadData(dbName, rowGuid = null) {
      const GET_DATA = gql`
        query($dbName: String!, $rowGuid: String, $updateTime: String) {
          formData(
            dbName: $dbName
            rowGuid: $rowGuid
            updateTime: $updateTime
          ) {
            guid
            name
            dbName
            parent
            icon
            fields {
              edges {
                node {
                  guid
                  name
                  dbName
                  position
                  fieldType {
                    tag
                    icon
                    valueType
                  }
                  isTab
                  isRequired
                  isWholeRow
                  parent
                  optionsJson
                  value
                }
              }
            }
            actions {
              edges {
                node {
                  guid
                  name
                  icon
                }
              }
            }
          }
        }
      `;

      apolloClient
        .query({
          query: GET_DATA,
          variables: {
            rowGuid,
            dbName,
            updateTime: Date.now()
          }
        })
        .then(data => {
          const currentFormData = data.data.formData;
          this.guid = currentFormData.guid;
          this.name = currentFormData.name;
          this.dbName = currentFormData.dbName;
          this.icon = currentFormData.icon;
          this.actions = currentFormData.actions.edges.map(edge => edge.node);
          const fields = currentFormData.fields.edges.map(edge => edge.node);
          this.tabs = [];
          this.fields = [];
          fields.forEach(field => {
            const thisField = field;
            if (field.isRequired) thisField.name = `${field.name} *`;
            if (field.isTab) this.tabs.push(thisField);
            else this.fields.push(thisField);
          });
          if (this.opened_tab) this.activeTab = this.opened_tab;
          else this.activeTab = this.tabs[0].guid;
          this.updateValue();
        })
        .catch(error => {
          this.$log.error(
            `Error in AxForm GQL query - apollo client => ${error}`
          );
        });
    },
    openForm() {
      this.$log.info(' OPEN FORM');
      this.$modal.show('sub-form');
    },
    handleResize(force = false) {
      if (
        this.currentWidth
        && this.currentWidth === this.$el.clientWidth
        && !force
      ) {
        // console.log('prevent');
        return false;
      }

      this.currentWidth = this.$el.clientWidth;
      const breakingPoint = 800;

      const foldersWithField = [];
      this.fields.forEach(field => {
        if (!foldersWithField.find(f => f === field.parent)) {
          foldersWithField.push(field.parent);
        }
      });

      if (foldersWithField.length < 2) {
        this.drawerIsFloating = false;
        this.drawerIsHidden = true;
        this.overlayIsHidden = true;
        // console.log('no tabs');
        return true;
      }

      if (
        this.drawerIsFloating === false
        && this.currentWidth * 1 < breakingPoint
      ) {
        this.drawerIsFloating = true;
        this.drawerIsHidden = true;
        this.overlayIsHidden = true;
        // console.log('small');
        return true;
      }

      if (
        this.drawerIsFloating === true
        && this.currentWidth * 1 > breakingPoint
      ) {
        this.drawerIsFloating = false;
        this.drawerIsHidden = false;
        this.overlayIsHidden = true;
        // console.log('big');
        return true;
      }
      // console.log(
      //   `nothing -> this.drawerIsFloating=${
      //     this.drawerIsFloating
      //   } this.currentWidth=${this.currentWidth}`
      // );
      return false;
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
.drawer-toggle-errors {
  line-height: 19px;
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
.form-container {
  margin: 20px;
}
.form-container-no-margin {
  margin: 0px;
}
.highlighted {
  background: #e0e0e0;
}
.test-value {
  padding: 25px;
}
.tab-errors {
  background: #f44336;
  width: 30px;
  height: 30px;
  line-height: 30px;
  font-size: 13px;
  color: white;
  border-radius: 15px;
}
</style>
