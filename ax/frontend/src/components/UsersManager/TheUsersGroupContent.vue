<template>
  <div class='grid-wrapper'>
    <v-container>
      <v-row>
        <v-col>
          <v-row>
            <div>
              <h1>
                <i class='fas fa-users'></i>
                &nbsp; {{ this.groupName}}
              </h1>
            </div>
            <div class='ico-btn'>
              <v-btn @click='promptRenameGroup' icon text>
                <i class='fas fa-pencil-alt'></i>
              </v-btn>
            </div>
            <div class='ico-btn'>
              <v-btn @click='promptDeleteGroup' icon text>
                <i class='fas fa-trash'></i>
              </v-btn>
            </div>
          </v-row>
        </v-col>
        <v-col>
          <v-autocomplete
            :hide-no-data='hideNoData'
            :items='foundUsers'
            :label='this.$t("users.add-to-group")'
            :search-input.sync='search'
            @change='addToGroup()'
            chips
            dense
            hide-selected
            item-text='shortName'
            item-value='guid'
            no-filter
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
              <v-btn @click.stop='addToGroup()' small>
                <i class='fas fa-plus'></i>
                &nbsp; {{$t("users.add-to-group-btn")}}
              </v-btn>
            </template>
          </v-autocomplete>
        </v-col>
      </v-row>
    </v-container>

    <div class='ag-theme-material grid-class' ref='grid'></div>
  </div>
</template>

<script>
import { Grid } from 'ag-grid-community';
import 'ag-grid-community/dist/styles/ag-grid.css';
import 'ag-grid-community/dist/styles/ag-theme-material.css';
import gql from 'graphql-tag';
import apolloClient from '@/apollo';

export default {
  name: 'TheUsersGroupContent',
  data: () => ({
    gridObj: null,
    rowData: [],
    gridInitialized: false,
    currentUserValue: null,
    foundUsers: [],
    search: null
  }),
  computed: {
    groupGuid() {
      return this.$route.params.group_alias;
    },
    groupName() {
      if (this.groupGuid) {
        const user = this.$store.state.users.groups.find(
          x => x.guid === this.groupGuid
        );
        if (user) return user.shortName;
      }
      return null;
    },
    hideNoData() {
      if (this.search && this.search.length > 2) return false;
      return true;
    }
  },
  watch: {
    groupGuid(newValue) {
      if (newValue) this.loadData();
    },
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
  mounted() {
    if (this.groupGuid) this.loadData();
  },
  methods: {
    loadData() {
      const GROUP_USERS = gql`
        query($groupGuid: String!, $updateTime: String) {
          groupUsers(groupGuid: $groupGuid, updateTime: $updateTime) {
            guid
            email
            shortName
          }
        }
      `;

      apolloClient
        .query({
          query: GROUP_USERS,
          variables: {
            groupGuid: this.groupGuid,
            updateTime: Date.now()
          }
        })
        .then(data => {
          this.rowData = data.data.groupUsers;

          if (!this.gridInitialized) this.initAgGrid(this.rowData);
          else {
            if (this.rowData == null) {
              this.gridObj.gridOptions.api.showNoRowsOverlay();
            }
            const filterModel = this.gridObj.gridOptions.api.getFilterModel();
            this.gridObj.gridOptions.api.setRowData(this.rowData);
            this.gridObj.gridOptions.api.setFilterModel(filterModel);
          }
        })
        .catch(error => {
          this.$log.error(
            `Error in TheUsersGroupContent => loadData apollo client => ${error}`
          );
        });
    },
    initAgGrid(data) {
      const that = this;
      const columnDefs = [
        { headerName: this.$t('users.grid-email'), field: 'email' },
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
    async promptRenameGroup() {
      const res = await this.$dialog.prompt({
        text: this.$t('users.rename-group-prompt', { name: this.groupName }),
        actions: {
          true: {
            text: this.$t('common.confirm')
          }
        }
      });
      if (res) {
        this.renameGroup(res);
      }
    },
    renameGroup(groupName) {
      const UPDATE_GROUP = gql`
        mutation($guid: String!, $shortName: String) {
          updateGroup(guid: $guid, shortName: $shortName) {
            user {
              guid
              shortName
              parent
            }
            ok
            msg
          }
        }
      `;

      apolloClient
        .mutate({
          mutation: UPDATE_GROUP,
          variables: {
            guid: this.groupGuid,
            shortName: groupName
          }
        })
        .then(data => {
          if (data.data.updateGroup.ok) {
            const msg = this.$t('users.group-updated-toast');
            this.$dialog.message.success(
              `<i class="fas fa-plus"></i> &nbsp ${msg}`
            );
            this.$store.commit('users/updateGroup', data.data.updateGroup.user);
          } else {
            this.$dialog.message.error(this.$t(data.data.updateGroup.msg));
          }
        })
        .catch(error => {
          this.$log.error(`Error in updateGroup gql => ${error}`);
          this.$dialog.message.error(`${error}`);
        });
    },
    async promptDeleteGroup(e) {
      e.preventDefault();
      const res = await this.$dialog.confirm({
        text: this.$t('users.group-delete-confirm', { name: this.groupName }),
        actions: {
          false: this.$t('common.confirm-no'),
          true: {
            text: this.$t('common.confirm-yes'),
            color: 'red'
          }
        }
      });
      if (res) this.deleteGroup(this.guid);
    },
    deleteGroup(guid) {
      const DELETE_GROUP = gql`
        mutation($guid: String!) {
          deleteUser(guid: $guid) {
            deleted
          }
        }
      `;

      apolloClient
        .mutate({
          mutation: DELETE_GROUP,
          variables: {
            guid: this.groupGuid
          }
        })
        .then(data => {
          const msg = this.$t('users.group-deleted-toast');
          this.$dialog.message.success(
            `<i class="fas fa-trash-alt"></i> &nbsp ${msg}`
          );
          const url = `/admin/users`;
          this.$router.push({ path: url });
        })
        .catch(error => {
          this.$log.error(`Error in deleteGroup gql => ${error}`);
          this.$dialog.message.error(`${error}`);
        });
    },
    openFormModal(e) {
      console.log(e);
    },
    addToGroup() {
      const ADD_TO_GROUP = gql`
        mutation($userGuid: String!, $groupGuid: String!) {
          addUserToGroup(userGuid: $userGuid, groupGuid: $groupGuid) {
            ok
          }
        }
      `;

      apolloClient
        .mutate({
          mutation: ADD_TO_GROUP,
          variables: {
            userGuid: this.currentUserValue,
            groupGuid: this.groupGuid
          }
        })
        .then(data => {
          const msg = this.$t('users.user-added-group-toast');
          this.$dialog.message.success(
            `<i class="fas fa-plus"></i> &nbsp ${msg}`
          );
          this.clearValue();
          this.loadData();
        })
        .catch(error => {
          this.$log.error(`Error in addUserToGroup gql => ${error}`);
          this.$dialog.message.error(`${error}`);
        });
    },
    doUserSearch() {
      const SEARCH_USERS = gql`
        query($updateTime: String, $searchString: String) {
          allUsers(updateTime: $updateTime, searchString: $searchString) {
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
          this.foundUsers = data.data.allUsers;
        })
        .catch(error => {
          this.$log.error(`Error in doUserSearch gql => ${error}`);
          this.$dialog.message.error(`${error}`);
        });
    },
    async promptRemoveUser(user) {
      const res = await this.$dialog.confirm({
        text: this.$t('users.remove-user-confirm', { name: user.shortName }),
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
      const REMOVE_FROM_GROUP = gql`
        mutation($userGuid: String!, $groupGuid: String!) {
          removeUserFromGroup(userGuid: $userGuid, groupGuid: $groupGuid) {
            ok
          }
        }
      `;

      apolloClient
        .mutate({
          mutation: REMOVE_FROM_GROUP,
          variables: {
            userGuid: userGuid,
            groupGuid: this.groupGuid
          }
        })
        .then(data => {
          const msg = this.$t('users.user-removed-group-toast');
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
    clearValue(user) {
      this.search = null;
      this.foundUsers = [];
      this.currentUserValue = null;
    }
  }
};
</script>

<style scoped>
.grid-wrapper {
  width: 100%;
  height: 100%;
}
.grid-class {
  width: 100%;
  height: calc(100% - 100px);
}
.ico-btn {
  margin-left: 10px;
}
</style>
