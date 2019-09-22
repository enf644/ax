<template>
  <div class='grid-wrapper'>
    <h1>{{$t("users.all-users-header")}}</h1>
    <div class='ag-theme-material grid-class' ref='grid'></div>
    <v-btn @click='openNewUserModal' class='mb-3' data-cy='create-form-btn' small>
      <i class='fas fa-users-plus'></i>
      &nbsp; {{$t("users.create-user-btn")}}
    </v-btn>

    <!--  transition='animated flipInX faster' -->
    <modal adaptive class='mb-3' height='auto' name='user-modal' scrollable>
      <TheUserModal :guid='currentUserGuid' @close='closeModals' @closeAndReload='closeAndReload' />
    </modal>
  </div>
</template>

<script>
import TheUserModal from '@/components/UsersManager/TheUserModal.vue';
import { Grid } from 'ag-grid-community';
import 'ag-grid-community/dist/styles/ag-grid.css';
import 'ag-grid-community/dist/styles/ag-theme-material.css';
import gql from 'graphql-tag';
import apolloClient from '@/apollo';

export default {
  name: 'TheUsersList',
  data: () => ({
    currentUserGuid: null,
    gridObj: null,
    rowData: [],
    gridInitialized: false
  }),
  components: { TheUserModal },
  mounted() {
    this.loadData();
  },
  methods: {
    openNewUserModal() {
      this.currentUserGuid = null;
      this.$modal.show('user-modal');
    },
    closeModals() {
      this.$modal.hide('user-modal');
    },
    closeAndReload() {
      this.$modal.hide('user-modal');
      setTimeout(() => {
        this.loadData();
      }, 200);
    },
    loadData() {
      const ALL_USERS = gql`
        query($updateTime: String!) {
          allUsers(updateTime: $updateTime) {
            guid
            email
            shortName
          }
        }
      `;

      apolloClient
        .query({
          query: ALL_USERS,
          variables: {
            updateTime: Date.now()
          }
        })
        .then(data => {
          this.rowData = data.data.allUsers;

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
          this.gqlException = true;
          logger.error(
            `Error in TheUsersList => loadData apollo client => ${error}`
          );
        });
    },
    initAgGrid(data) {
      const columnDefs = [
        { headerName: this.$t('users.grid-email'), field: 'email' },
        { headerName: this.$t('users.grid-short-name'), field: 'shortName' }
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
  height: calc(100% - 50px);
}
</style>
