<template>
  <div class='card' ref='gridWrapper'>
    <h1>{{$t("workflow.role.role-settings-header")}}</h1>
    <v-btn :ripple='false' @click='closeModal' class='close' color='black' icon text>
      <i class='fas fa-times close-ico'></i>
    </v-btn>
    <v-container>
      <v-row>
        <v-col class='left-input'>
          <v-form @submit.prevent='updateRole' ref='form' v-model='valid'>
            <v-text-field
              :label='$t("workflow.role.role-name")'
              :rules='nameRules'
              data-cy='role-name'
              ref='nameField'
              required
              v-model='name'
            />
          </v-form>
        </v-col>
        <v-col class='right-input'>
          <v-autocomplete
            :hide-no-data='hideNoData'
            :items='foundUsers'
            :label='this.$t("users.add-to-role")'
            :search-input.sync='search'
            @change='addToRole()'
            chips
            dense
            hide-selected
            item-text='shortName'
            item-value='guid'
            no-filter
            v-if='isDynamic != true'
            v-model='currentUserValue'
          >
            <template v-slot:selection='{ item, selected }'>
              <v-chip
                @click:close='clearValue(item)'
                @click.stop='openFormModal()'
                class='chip'
                close
              >
                <v-avatar class='grey' left>
                  <i :class='`ax-chip-icon fas fa-user`'></i>
                </v-avatar>
                {{item.shortName}}
              </v-chip>
            </template>

            <template v-slot:append>
              <v-btn @click.stop='addToRole()' small>
                <i class='fas fa-plus'></i>
                &nbsp; {{$t("users.add-to-role-btn")}}
              </v-btn>
            </template>
          </v-autocomplete>
        </v-col>
      </v-row>
    </v-container>

    <div class='ag-theme-material grid-class' ref='grid' v-if='isDynamic != true'></div>

    <div id='monacoDock' v-if='isDynamic'>
      <div id='monacoWrapper'>
        <monaco-editor
          :options='monacoOptions'
          @editorDidMount='initMonaco'
          class='monaco-editor'
          cy-data='code-editor'
          language='python'
          ref='editor'
          theme='vs-dark'
          v-model='code'
        ></monaco-editor>
      </div>
      <br />
    </div>

    <div class='actions'>
      <v-btn @click='updateRole' data-cy='update-role-btn' small>
        <i class='fas fa-pencil-alt'></i>
        &nbsp; {{$t("workflow.role.update-role-btn")}}
      </v-btn>

      <v-btn @click='deleteRole' color='error' data-cy='delete-role-btn' small text>
        <i class='fas fa-trash-alt'></i>
        &nbsp; {{$t("workflow.role.delete-role-btn")}}
      </v-btn>
    </div>
  </div>
</template>

<script>
import { Grid } from 'ag-grid-community';
import 'ag-grid-community/dist/styles/ag-grid.css';
import 'ag-grid-community/dist/styles/ag-theme-material.css';
import gql from 'graphql-tag';
import apolloClient from '@/apollo';
import MonacoEditor from 'vue-monaco';
import * as monaco from 'monaco-editor';

export default {
  name: 'TheRoleModal',
  props: {
    guid: null
  },
  components: { MonacoEditor },
  data() {
    return {
      name: '',
      valid: false,
      nameRules: [
        v => !!v || this.$t('workflow.role.role-name-required'),
        v => v.length <= 255 || this.$t('common.lenght-error', { num: 255 }),
        v =>
          this.checkRoleNameExists(v) == false ||
          this.$t('workflow.role.role-name-exists-toast', { name: this.name })
      ],
      gridObj: null,
      rowData: [],
      gridInitialized: false,
      currentUserValue: null,
      foundUsers: [],
      search: null,
      isDynamic: null,
      code: '',
      monacoOptions: null,
      fullScreenMode: false
    };
  },
  computed: {
    hideNoData() {
      if (this.search && this.search.length > 2) return false;
      return true;
    },
    roleGuid() {
      return this.guid;
    },
    allRoleNames() {
      return this.$store.getters['workflow/rolesWithColor'];
    }
  },
  watch: {
    search(newValue, oldValue) {
      if (newValue) {
        if (newValue.length > 2) {
          this.doUserSearch();
        } else if (oldValue && oldValue.length > 2 && newValue.length <= 2) {
          this.clearValue();
        }
      }
    }
  },
  created() {},
  mounted() {
    const role = this.$store.state.workflow.roles.find(
      role => role.guid === this.guid
    );
    this.name = role.name;
    this.isDynamic = role.isDynamic;
    this.$refs.nameField.focus();
    this.loadData();
  },
  methods: {
    updateRole() {
      if (this.$refs.form.validate()) {
        const data = {
          guid: this.guid,
          name: this.name,
          icon: null,
          code: this.code
        };
        this.$store.dispatch('workflow/updateRole', data).then(() => {
          const msg = this.$t('workflow.role.update-role-toast');
          this.$dialog.message.success(
            `<i class="fas fa-pencil-alt"></i> &nbsp ${msg}`
          );
          this.closeModal();
        });
      }
    },
    async deleteRole() {
      const res = await this.$dialog.confirm({
        text: this.$t('workflow.role.role-delete-confirm', { name: this.name }),
        actions: {
          false: this.$t('common.confirm-no'),
          true: {
            text: this.$t('common.confirm-yes'),
            color: 'red'
          }
        }
      });

      if (res) {
        this.$store
          .dispatch('workflow/deleteRole', {
            guid: this.guid
          })
          .then(() => {
            const msg = this.$t('workflow.role.role-deleted-toast');
            this.$dialog.message.success(
              `<i class="fas fa-trash-alt"></i> &nbsp ${msg}`
            );
            this.closeModal();
          });
      }
    },
    loadData() {
      const ROLE_USERS = gql`
        query($roleGuid: String!, $updateTime: String) {
          roleUsers(roleGuid: $roleGuid, updateTime: $updateTime) {
            guid
            email
            shortName
          }
          axRole(guid: $roleGuid, updateTime: $updateTime) {
            guid
            name
            isDynamic
            icon
            code
          }
        }
      `;

      apolloClient
        .query({
          query: ROLE_USERS,
          variables: {
            roleGuid: this.roleGuid,
            updateTime: Date.now()
          }
        })
        .then(data => {
          this.rowData = data.data.roleUsers;
          const retRole = data.data.axRole;

          if (retRole.isDynamic) {
            // For dynamic roles - show code input
            this.code = retRole.code;
          } else {
            // For normal roles - show user input
            if (!this.gridInitialized) this.initAgGrid(this.rowData);
            else {
              if (this.rowData == null) {
                this.gridObj.gridOptions.api.showNoRowsOverlay();
              }
              const filterModel = this.gridObj.gridOptions.api.getFilterModel();
              this.gridObj.gridOptions.api.setRowData(this.rowData);
              this.gridObj.gridOptions.api.setFilterModel(filterModel);
            }
          }
        })
        .catch(error => {
          this.$log.error(
            `Error in TheRoleModal => loadData apollo client => ${error}`
          );
        });
    },
    initAgGrid(data) {
      const that = this;
      // { headerName: this.$t('users.grid-email'), field: 'email' },

      const columnDefs = [
        {
          headerName: this.$t('users.grid-email'),
          field: 'email',
          cellRenderer: params => {
            var eDiv = document.createElement('div');
            const email = params.data.email;
            if (email) eDiv.innerHTML = email;
            else eDiv.innerHTML = '<i class="fas fa-users"></i>';
            return eDiv;
          }
        },
        { headerName: this.$t('users.grid-short-name'), field: 'shortName' },
        {
          headerName: '',
          field: 'guid',
          cellRenderer: params => {
            var eDiv = document.createElement('div');
            eDiv.innerHTML = '<i class="grid-btn far fa-trash-alt"></i>';
            var eButton = eDiv.querySelectorAll('.grid-btn')[0];

            eButton.addEventListener('click', function() {
              that.promptRemoveUser(params.data);
            });
            return eDiv;
          }
        }
      ];

      const gridOptions = {
        defaultColDef: {
          sortable: true,
          resizable: true,
          filter: true
        },
        columnDefs: columnDefs,
        suppressScrollOnNewData: true,
        rowData: this.rowData,
        getRowNodeId: data => data.guid
      };
      gridOptions.onCellClicked = event => {
        this.currentUserGuid = event.data.guid;
        this.$modal.show('user-modal');
      };
      this.gridObj = new Grid(this.$refs.grid, gridOptions);
      this.gridInitialized = true;
    },
    addToRole() {
      const ADD_TO_ROLE = gql`
        mutation($userGuid: String!, $roleGuid: String!) {
          addUserToRole(userGuid: $userGuid, roleGuid: $roleGuid) {
            ok
          }
        }
      `;

      apolloClient
        .mutate({
          mutation: ADD_TO_ROLE,
          variables: {
            userGuid: this.currentUserValue,
            roleGuid: this.roleGuid
          }
        })
        .then(data => {
          const msg = this.$t('users.user-added-role-toast');
          this.$dialog.message.success(
            `<i class="fas fa-plus"></i> &nbsp ${msg}`
          );
          this.clearValue();
          this.loadData();
        })
        .catch(error => {
          this.$log.error(`Error in addToRole gql => ${error}`);
          this.$dialog.message.error(`${error}`);
        });
    },
    doUserSearch() {
      const SEARCH_USERS = gql`
        query($updateTime: String, $searchString: String) {
          usersAndGroups(updateTime: $updateTime, searchString: $searchString) {
            guid
            email
            shortName
          }
        }
      `;

      apolloClient
        .query({
          query: SEARCH_USERS,
          variables: {
            searchString: this.search,
            updateTime: Date.now()
          }
        })
        .then(data => {
          this.foundUsers = data.data.usersAndGroups;
        })
        .catch(error => {
          this.$log.error(`Error in doUserSearch gql => ${error}`);
          this.$dialog.message.error(`${error}`);
        });
    },
    async promptRemoveUser(user) {
      const res = await this.$dialog.confirm({
        text: this.$t('users.remove-user-role-confirm', {
          name: user.shortName
        }),
        actions: {
          false: this.$t('common.confirm-no'),
          true: {
            text: this.$t('common.confirm-yes'),
            color: 'red'
          }
        }
      });
      if (res) this.removeUser(user.guid);
    },
    removeUser(userGuid) {
      const REMOVE_FROM_ROLE = gql`
        mutation($userGuid: String!, $roleGuid: String!) {
          removeUserFromRole(userGuid: $userGuid, roleGuid: $roleGuid) {
            ok
          }
        }
      `;

      apolloClient
        .mutate({
          mutation: REMOVE_FROM_ROLE,
          variables: {
            userGuid: userGuid,
            roleGuid: this.roleGuid
          }
        })
        .then(data => {
          const msg = this.$t('users.user-removed-role-toast');
          this.$dialog.message.success(
            `<i class="fas fa-trash-alt"></i> &nbsp ${msg}`
          );
          this.loadData();
        })
        .catch(error => {
          this.$log.error(`Error in removeUser gql => ${error}`);
          this.$dialog.message.error(`${error}`);
        });
    },
    checkRoleNameExists(name) {
      let ret_val = false;
      this.allRoleNames.forEach(role => {
        if (role.name == name && role.guid != this.guid) ret_val = true;
      });
      return ret_val;
    },
    initMonaco(editor) {
      editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KEY_S, () => {
        this.updateRole();
      });
    },
    clearValue(user) {
      this.search = null;
      this.foundUsers = [];
      this.currentUserValue = null;
    },
    closeModal() {
      this.$emit('close');
    }
  }
};
</script>

<style scoped>
.card {
  padding: 25px;
  width: 100%;
  height: 100%;
}
.close {
  position: absolute;
  right: 10px;
  top: 10px;
}
.close-ico {
  font-size: 20px;
}
.actions {
  justify-content: space-between;
  display: flex;
}
.grid-class {
  width: 100%;
  height: calc(100% - 175px);
}
.left-input div {
  width: 350px;
}
.right-input {
  margin-top: -10px;
}
.field-tag-desc {
  padding: 30px 0px;
}
.field-tag-desc span {
  margin-left: 10px;
}
.monaco-editor {
  width: 100%;
  height: 200px;
  margin-bottom: 20px;
  padding-top: 20px;
}
</style>
