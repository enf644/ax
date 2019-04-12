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
              :class='getTabClass(tab.guid)'
              :key='tab.name'
              @click='openTab(tab.guid)'
              ripple
              v-for='tab in tabs'
            >
              <v-list-tile-content class='drawer-folder-item'>
                <v-list-tile-title>{{ tab.name }}</v-list-tile-title>
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
              <i class='fas fa-bars'></i>
            </v-btn>
            <i :class='iconClass'></i>
            &nbsp; {{name}}
            <resize-observer @notify='handleResize'/>
          </div>
          <v-container fluid grid-list-xl>
            <v-layout align-center justify-center row wrap>
              <AxField
                :dbName='field.dbName'
                :key='field.guid'
                :name='field.name'
                :optionsJson='field.optionsJson'
                :tag='field.fieldType.tag'
                :value.sync='field.value'
                @update:value='updateValue'
                v-for='field in this.fields'
                v-show='isFieldVisible(field)'
              ></AxField>

              <v-flex xs12>
                <v-btn @click='submitTest' small>
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
import apolloClient from '../apollo';
import AxField from '@/components/AxField.vue';
import gql from 'graphql-tag';

export default {
  name: 'AxForm',
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
    update_time: null
  },
  data() {
    return {
      drawerIsFloating: false,
      drawerIsHidden: false,
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
      value: null
    };
  },
  computed: {
    iconClass() {
      return `fas fa-${this.icon}`;
    }
  },
  watch: {
    db_name(newValue) {
      if (newValue) this.loadData(newValue);
    },
    update_time() {
      if (this.db_name) this.loadData(this.db_name);
    }
  },
  created() {},
  mounted() {
    if (this.db_name) this.loadData(this.db_name);
    this.$nextTick(() => {
      this.handleResize();
    });
  },
  methods: {
    updateValue() {
      const result = {};
      this.fields.forEach(field => {
        result[field.dbName] = field.value;
      });
      this.value = result;
      this.$emit('update:value', result);
    },
    submitTest() {
      this.$modal.show('test-value');
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
                  valueType
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
            if (field.isTab) this.tabs.push(field);
            else this.fields.push(field);
          });
          this.activeTab = this.tabs[0].guid;
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
</style>
