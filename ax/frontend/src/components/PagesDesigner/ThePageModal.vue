<template>
  <div class='card' ref='gridWrapper'>
    <h1>{{$t("pages.page-modal-header")}}</h1>
    <v-btn :ripple='false' @click='closeModal' class='close' color='black' icon text>
      <i class='fas fa-times close-ico'></i>
    </v-btn>
    <v-container>
      <v-form @submit.prevent='updatePage()' ref='form' v-model='valid'>
        <v-row>
          <v-col class>
            <v-text-field
              :label='$t("pages.modal-name-field")'
              :rules='rules.name'
              data-cy='page-name'
              ref='nameField'
              required
              v-model='name'
            />
          </v-col>
          <v-col class>
            <v-text-field
              :hint='$t("pages.modal-dbname-field-hint")'
              :label='$t("pages.modal-dbname-field")'
              :rules='rules.dbName'
              data-cy='page-dbname'
              ref='dbNameField'
              v-model='dbName'
            />
          </v-col>
          <v-col class='right-input'>
            <v-autocomplete
              :hide-no-data='hideNoData'
              :items='foundUsers'
              :label='this.$t("users.add-to-role")'
              :search-input.sync='search'
              @change='addToPage()'
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
                  @click.stop='openUserModal()'
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
                <v-btn @click.stop='addToPage()' small>
                  <i class='fas fa-plus'></i>
                  &nbsp; {{$t("pages.add-to-page-btn")}}
                </v-btn>
              </template>
            </v-autocomplete>
          </v-col>
        </v-row>
      </v-form>
    </v-container>

    <div class='ag-theme-material grid-class' ref='grid'></div>

    <div class='actions'>
      <v-btn @click='updatePage()' data-cy='update-page-btn' small>
        <i class='fas fa-pencil-alt'></i>
        &nbsp; {{$t("pages.update-page-btn")}}
      </v-btn>

      <v-btn @click='deletePage()' color='error' data-cy='delete-page-btn' small text>
        <i class='fas fa-trash-alt'></i>
        &nbsp; {{$t("pages.delete-page-btn")}}
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

export default {
  name: 'ThePageModal',
  props: {
    guid: null
  },
  data() {
    return {
      name: '',
      dbName: null,
      valid: false,
      rules: {
        name: [
          v => !!v || this.$t('common.field-required'),
          v => v.length <= 255 || this.$t('common.lenght-error', { num: 255 })
        ],
        dbName: [
          v =>
            /^([a-z0-9]+)*([A-Z][a-z0-9]*)*$/.test(v) ||
            this.$t('pages.modal-db-name-error')
        ]
      },
      gridObj: null,
      rowData: [],
      gridInitialized: false,
      currentUserValue: null,
      foundUsers: [],
      search: null
    };
  },
  computed: {
    hideNoData() {
      if (this.search && this.search.length > 2) return false;
      return true;
    },
    pageGuid() {
      return this.guid;
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
    this.$refs.nameField.focus();
    this.name = this.$store.state.pages.currentPage.name;
    this.dbName = this.$store.state.pages.currentPage.dbName;
    this.loadData();
  },
  methods: {
    updatePage() {
      if (this.$refs.form.validate()) {
        const UPDATE_PAGE = gql`
          mutation($guid: String!, $name: String, $dbName: String) {
            updatePage(guid: $guid, name: $name, dbName: $dbName) {
              page {
                guid
                name
                dbName
                code
                parent
              }
              ok
            }
          }
        `;

        apolloClient
          .mutate({
            mutation: UPDATE_PAGE,
            variables: {
              guid: this.$store.state.pages.currentPage.guid,
              name: this.name,
              dbName: this.dbName
            }
          })
          .then(data => {
            const page = data.data.updatePage.page;
            this.$store.commit('pages/setCurrentPage', page);
            this.$store.commit('pages/updatePageInList', page);

            const msg = this.$t('pages.page-updated-toast');
            this.$dialog.message.success(
              `<i class="fas fa-pencil-alt"></i> &nbsp ${msg}`
            );
            this.closeModal();
          })
          .catch(error => {
            this.$log.error(`Error in updatePage gql => ${error}`);
            this.$dialog.message.error(`${error}`);
          });
      }
    },
    async deletePage() {
      const res = await this.$dialog.confirm({
        text: this.$t('pages.page-delete-confirm', { name: this.name }),
        actions: {
          false: this.$t('common.confirm-no'),
          true: {
            text: this.$t('common.confirm-yes'),
            color: 'red'
          }
        }
      });

      if (res) {
        const DELETE_PAGE = gql`
          mutation($guid: String!) {
            deletePage(guid: $guid) {
              deleted
            }
          }
        `;

        apolloClient
          .mutate({
            mutation: DELETE_PAGE,
            variables: {
              guid: this.$store.state.pages.currentPage.guid
            }
          })
          .then(data => {
            const deletedGuid = data.data.deletePage.deleted;
            this.$store.commit('pages/deletePageFromList', deletedGuid);

            const parent = this.$store.state.pages.currentPage.parent;
            this.$store.dispatch('pages/loadPageData', { guid: parent });

            const msg = this.$t('pages.page-deleted-toast');
            this.$dialog.message.success(
              `<i class="fas fa-trash-alt"></i> &nbsp ${msg}`
            );
            this.closeModal();
          })
          .catch(error => {
            this.$log.error(`Error in deletePage gql => ${error}`);
            this.$dialog.message.error(`${error}`);
          });
      }
    },
    loadData() {
      const PAGE_USERS = gql`
        query($pageGuid: String!, $updateTime: String) {
          pageUsers(pageGuid: $pageGuid, updateTime: $updateTime) {
            guid
            email
            shortName
          }
        }
      `;

      apolloClient
        .query({
          query: PAGE_USERS,
          variables: {
            pageGuid: this.pageGuid,
            updateTime: Date.now()
          }
        })
        .then(data => {
          this.rowData = data.data.pageUsers;

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
            `Error in ThePageModal => loadData apollo client => ${error}`
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
    addToPage() {
      const ADD_TO_PAGE = gql`
        mutation($userGuid: String!, $pageGuid: String!) {
          addUserToPage(userGuid: $userGuid, pageGuid: $pageGuid) {
            ok
          }
        }
      `;

      apolloClient
        .mutate({
          mutation: ADD_TO_PAGE,
          variables: {
            userGuid: this.currentUserValue,
            pageGuid: this.pageGuid
          }
        })
        .then(data => {
          const msg = this.$t('users.user-added-page-toast');
          this.$dialog.message.success(
            `<i class="fas fa-plus"></i> &nbsp ${msg}`
          );
          this.clearValue();
          this.loadData();
        })
        .catch(error => {
          this.$log.error(`Error in addToPage gql => ${error}`);
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
        text: this.$t('users.remove-user-page-confirm', {
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
      const REMOVE_FROM_PAGE = gql`
        mutation($userGuid: String!, $pageGuid: String!) {
          removeUserFromPage(userGuid: $userGuid, pageGuid: $pageGuid) {
            ok
          }
        }
      `;

      apolloClient
        .mutate({
          mutation: REMOVE_FROM_PAGE,
          variables: {
            userGuid: userGuid,
            pageGuid: this.pageGuid
          }
        })
        .then(data => {
          const msg = this.$t('users.user-removed-page-toast');
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
</style>
