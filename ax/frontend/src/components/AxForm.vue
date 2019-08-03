<template>
  <v-app class='ax-form-app' id='ax-form' ref='formApp'>
    <!-- <transition enter-active-class='animated fadeIn'> -->
    <v-sheet
      :class='no_margin ? "form-container-no-margin" : "form-container"'
      elevation='5'
      light
      ref='sheet'
      v-if='!this.guidNotFound'
      v-show='formIsLoaded'
    >
      <v-layout align-space-between class='form-layout' justify-start row>
        <transition :enter-active-class='drawerAnimationClass'>
          <div
            :class='{
              "drawer-floating": drawerIsFloating,
              "drawer-hidden": drawerIsHidden,
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
        </transition>
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
            <resize-observer @notify='handleResize' />
          </div>
          <v-container class='form-container' fluid grid-list-xl>
            <v-layout align-left justify-left row wrap>
              <AxField
                :class='getWidthClass(field)'
                :dbName='field.dbName'
                :fieldGuid='field.guid'
                :formDbName='db_name'
                :formGuid='formGuid'
                :isRequired='field.isRequired'
                :isWholeRow='field.isWholeRow'
                :key='field.guid'
                :name='field.name'
                :optionsJson='field.optionsJson'
                :ref='getFieldRef(field.guid)'
                :rowGuid='currentRowGuid'
                :tag='field.fieldType.tag'
                :value.sync='field.value'
                @update:value='updateValue'
                v-for='field in this.fields'
                v-show='isFieldVisible(field)'
              ></AxField>

              <transition enter-active-class='animated fadeIn'>
                <v-alert :value='true' type='warning' v-show='showSubscribtionWarning'>
                  {{$t("form.record-modifyed-warning")}}
                  &nbsp;
                  <v-btn @click='reloadData' small>
                    <i class='fas fa-sync-alt'></i>
                    &nbsp;
                    {{$t("form.reload-data")}}
                  </v-btn>
                </v-alert>
              </transition>

              <v-flex xs12>
                <v-btn :disabled='!formIsValid' @click='submitTest' small v-if='isConstructorMode'>
                  <i class='fas fa-vial'></i>
                  &nbsp; {{$t("form.test-from")}}
                </v-btn>

                <v-btn
                  :disabled='!formIsValid'
                  :key='action.guid'
                  @click='doAction(action)'
                  small
                  v-for='action in this.actions'
                  v-show='isConstructorMode == false'
                >
                  <i :class='getActionIconClass(action)'></i>
                  &nbsp;
                  {{ action.name }}
                </v-btn>
                <!-- <v-btn @click='openForm()' color='primary' outline>text</v-btn> -->
              </v-flex>
            </v-layout>
          </v-container>
        </div>
      </v-layout>
    </v-sheet>
    <div v-if='this.guidNotFound'>
      <h1 class='not-found'>
        <i class='far fa-sad-cry'></i>
        &nbsp;
        {{$t("form.guid-not-found", {num: this.guid})}}
      </h1>
    </div>
    <!-- </transition> -->
    <modal adaptive height='auto' name='test-value' scrollable width='50%'>
      <v-card class='test-value'>
        <pre>{{value}}</pre>
      </v-card>
    </modal>

    <modal
      :name='`sub-form-${this.modalGuid}`'
      :pivotX='0.52'
      adaptive
      height='auto'
      scrollable
      width='70%'
    >
      <v-card>
        <AxForm no_margin></AxForm>
      </v-card>
    </modal>
  </v-app>
</template>

<script>
// import AxGrid from './AxGrid.vue';
// import smoothReflow from 'vue-smooth-reflow';
import apolloClient from '../apollo';
import AxField from '@/components/AxField.vue';
import gql from 'graphql-tag';
import uuid4 from 'uuid4';
// import { settings } from 'cluster';

export default {
  name: 'AxForm',
  // mixins: [smoothReflow],
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
    guid: null, // CAN BE guid OR AxNum
    row: null,
    action_guid: null,
    update_time: null,
    opened_tab: null,
    constructor_mode: null
  },
  data() {
    return {
      drawerIsFloating: false,
      drawerIsHidden: true,
      overlayIsHidden: true,
      dialogIsOpen: false,
      formGuid: null,
      rowGuid: null,
      name: null,
      dbName: null,
      icon: null,
      tabs: [],
      fields: [],
      actions: [],
      currentTabGuid: null,
      tabFields: [],
      activeTab: null,
      secureValue: null,
      get value() {
        return this.secureValue;
      },
      // eslint-disable-next-line vue/no-dupe-keys
      set value(value) {
        this.secureValue = value;
      },
      formIsValid: true,
      errorsCount: 0,
      currentWidth: null,
      isMobile: false,
      formIsLoaded: false,
      modalGuid: null,
      insertedGuid: null,
      showSubscribtionWarning: false,
      guidNotFound: false
    };
  },
  computed: {
    currentRowGuid() {
      if (this.rowGuid) return this.rowGuid;
      if (this.guid) return this.guid;
      return this.insertedGuid;
    },
    drawerAnimationClass() {
      if (this.formIsLoaded) return 'drawer-animation';
      return 'not-exist';
    },
    iconClass() {
      return `fas fa-${this.icon}`;
    },
    formIsNotValid() {
      return !this.formIsValid;
    },
    isConstructorMode() {
      return this.constructor_mode !== undefined;
    }
  },
  watch: {
    db_name(newValue) {
      if (newValue) this.loadData(newValue, this.currentRowGuid);
    },
    update_time(newValue) {
      if (newValue && this.db_name) {
        this.loadData(this.db_name, this.currentRowGuid);
      }
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
  created() {
    this.modalGuid = uuid4();
  },
  mounted() {
    if (this.db_name) this.loadData(this.db_name, this.currentRowGuid);
  },
  methods: {
    reloadData() {
      setTimeout(() => {
        this.loadData(this.db_name, this.currentRowGuid);
        this.showSubscribtionWarning = false;
      }, 1000);
    },
    getWidthClass(field) {
      if (field.isWholeRow || this.isMobile) return 'xs12';
      return 'xs6';
    },
    updateValue() {
      const result = {
        guid: this.currentRowGuid
      };
      this.fields.forEach(field => {
        if (!field.fieldType.isVirtual && !field.fieldType.isReadonly) {
          result[field.dbName] = field.value;
        }
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
    loadData(dbName, rowGuid) {
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
            rowGuid
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
                    isVirtual
                    isReadonly
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
            avalibleActions {
              guid
              name
              icon
              confirmText
              closeModal
              fromStateGuid
              toStateGuid
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
          this.rowGuid = currentFormData.rowGuid;
          this.formGuid = currentFormData.guid;
          this.name = currentFormData.name;
          this.dbName = currentFormData.dbName;
          this.icon = currentFormData.icon;
          this.actions = currentFormData.avalibleActions;
          if (this.action_guid && !this.insertedGuid) {
            this.actions = this.actions.filter(
              action => action.guid === this.action_guid
            );
          }

          this.guidNotFound = false;
          if (this.guid && !currentFormData.rowGuid) this.guidNotFound = true;

          const fields = currentFormData.fields.edges.map(edge => edge.node);
          this.tabs = [];
          this.fields = [];
          fields.forEach(field => {
            const thisField = field;
            if (
              !field.isTab
              && field.value
              && field.fieldType.valueType === 'JSON'
            ) {
              thisField.value = JSON.parse(field.value);
            }
            if (field.isRequired) thisField.name = `${field.name} *`;
            if (field.isTab) this.tabs.push(thisField);
            else this.fields.push(thisField);
          });
          if (this.opened_tab) this.activeTab = this.opened_tab;
          else this.activeTab = this.tabs[0].guid;
          this.updateValue();
          this.subscribeToActions();
          this.subscribeToConsole();

          setTimeout(() => {
            this.formIsLoaded = true;
            // this.$smoothReflow({ el: this.$refs.sheet.$el });
          }, 10);
        })
        .catch(error => {
          this.$log.error(
            `Error in AxForm GQL query - apollo client => ${error}`
          );
        });
    },
    openForm() {
      this.$modal.show(`sub-form-${this.modalGuid}`);
    },
    handleResize(force = false) {
      if (
        this.currentWidth
        && this.currentWidth === this.$el.clientWidth
        && !force
      ) {
        return false;
      }

      this.currentWidth = this.$el.clientWidth;
      const drawerBreakingPoint = 800;
      const mobileBreakingPoint = 520;

      if (this.currentWidth < mobileBreakingPoint) this.isMobile = true;
      else this.isMobile = false;

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
        return true;
      }

      if (
        this.drawerIsFloating === false
        && this.currentWidth * 1 < drawerBreakingPoint
      ) {
        this.drawerIsFloating = true;
        this.drawerIsHidden = true;
        this.overlayIsHidden = true;
        return true;
      }

      if (
        this.drawerIsFloating === true
        && this.currentWidth * 1 > drawerBreakingPoint
      ) {
        this.drawerIsFloating = false;
        this.drawerIsHidden = false;
        this.overlayIsHidden = true;
        return true;
      }
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
    },
    getActionIconClass(action) {
      if (action.icon) return `fas fa-${action.icon}`;
      if (action.toStateGuid === action.fromStateGuid) return 'fas fa-redo';
      return 'far fa-arrow-alt-circle-right';
    },
    async doAction(action) {
      this.isValid();
      if (!this.formIsValid) return false;

      if (action.confirmText) {
        const comfirmed = await this.$dialog.confirm({
          text: action.confirmText,
          actions: {
            false: this.$t('common.confirm-no'),
            true: {
              text: this.$t('common.confirm-yes'),
              color: 'red'
            }
          }
        });

        if (!comfirmed) return false;
      }

      const DO_ACTION = gql`
        mutation(
          $formGuid: String!
          $rowGuid: String
          $actionGuid: String!
          $values: String
          $modalGuid: String
        ) {
          doAction(
            formGuid: $formGuid
            rowGuid: $rowGuid
            actionGuid: $actionGuid
            values: $values
            modalGuid: $modalGuid
          ) {
            form {
              guid
              dbName
            }
            newGuid
            messages
            ok
          }
        }
      `;

      apolloClient
        .mutate({
          mutation: DO_ACTION,
          variables: {
            formGuid: this.formGuid,
            rowGuid: this.currentRowGuid,
            actionGuid: action.guid,
            values: JSON.stringify(this.value),
            modalGuid: this.modalGuid
          }
        })
        .then(data => {
          const dataRowGuid = data.data.doAction.newGuid;
          if (!dataRowGuid) this.guidNotFound = true;

          let retGuid = this.guid;
          if (!this.guid && dataRowGuid) {
            this.insertedGuid = dataRowGuid.replace(/-/g, '');
            retGuid = this.insertedGuid;
          }
          const messages = JSON.parse(data.data.doAction.messages);

          this.showMessagesAndEmit({
            messages,
            retGuid,
            closeModal: action.closeModal
          });
          const msg = this.$t('form.action-ok-toast', { action: action.name });
          this.$dialog.message.success(
            `<i class="far fa-arrow-alt-circle-right"></i> &nbsp ${msg}`
          );
        })
        .catch(error => {
          this.$log.error(
            `Error in AxGrid => doAction apollo client => ${error}`
          );
        });
      return true;
    },
    async showMessagesAndEmit(actionResult) {
      try {
        let res = false;
        if (actionResult.messages && actionResult.messages.error) {
          res = await this.$dialog.error({
            text: actionResult.messages.error,
            persistent: false
          });
        } else if (actionResult.messages && actionResult.messages.exception) {
          const msg = this.$t('workflow.action.action-error', {
            error_class: actionResult.messages.exception.error_class,
            line_number: actionResult.messages.exception.line_number,
            action_name: actionResult.messages.exception.action_name,
            detail: actionResult.messages.exception.detail
          });
          res = await this.$dialog.error({
            text: msg,
            persistent: false
          });
        } else if (actionResult.messages && actionResult.messages.info) {
          res = await this.$dialog.warning({
            text: actionResult.messages.info,
            persistent: false,
            actions: {
              true: this.$t('common.ok')
            }
          });
        } else res = true;

        if (res) {
          if (actionResult.closeModal) {
            this.$emit('close', actionResult.retGuid);
          } else {
            setTimeout(() => {
              this.loadData(this.db_name, this.currentRowGuid);
              this.$emit('updated', actionResult.retGuid);
            }, 100);
          }
        }
      } catch (err) {
        this.$log.error(`Vue error in AxForm -> showMessagesAndEmit: ${err}`);
      }
    },
    subscribeToActions() {
      const ACTION_SUBSCRIPTION_QUERY = gql`
        subscription($formDbName: String!, $rowGuid: String) {
          actionNotify(formDbName: $formDbName, rowGuid: $rowGuid) {
            guid
            dbName
            rowGuid
            modalGuid
          }
        }
      `;

      apolloClient
        .subscribe({
          query: ACTION_SUBSCRIPTION_QUERY,
          variables: {
            formDbName: this.dbName,
            rowGuid: this.guid
          }
        })
        .subscribe(
          data => {
            if (data.data.actionNotify.modalGuid !== this.modalGuid) {
              setTimeout(() => {
                this.showSubscribtionWarning = true;
              }, 1000);
            }
          },
          {
            error(error) {
              this.$log.error(`ERRROR in GQL subscribeToActions => ${error}`);
            }
          }
        );
    },
    subscribeToConsole() {
      const CONSOLE_SUBSCRIPTION_QUERY = gql`
        subscription($modalGuid: String!) {
          consoleNotify(modalGuid: $modalGuid) {
            modalGuid
            text
          }
        }
      `;

      apolloClient
        .subscribe({
          query: CONSOLE_SUBSCRIPTION_QUERY,
          variables: {
            modalGuid: this.modalGuid
          }
        })
        .subscribe(
          data => {
            console.log(data.data.consoleNotify);
          },
          {
            error(error) {
              this.$log.error(`ERRROR in GQL subscribeToConsole => ${error}`);
            }
          }
        );
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
  z-index: 5;
}
.drawer-animation {
  animation: slideIn 200ms 1 ease forwards;
}
.notransition {
  -webkit-transition: none !important;
  -moz-transition: none !important;
  -o-transition: none !important;
  transition: none !important;
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
.form-container-no-margin {
  margin: 0px;
}
.form {
  width: 100%;
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
.not-found {
  top: 50%;
  position: absolute;
  left: 30%;
}
.not-found i {
  font-size: 3em;
}
</style>
