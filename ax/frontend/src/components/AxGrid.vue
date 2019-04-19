<template>
  <v-app class='ax-grid-app' id='ax-grid'>
    <div class='ag-theme-material grid' ref='grid'></div>
    <!-- <modal adaptive height='auto' name='sub-form' scrollable width='70%'>
      <v-card>
        <AxForm no_margin></AxForm>
      </v-card>
    </modal>-->
  </v-app>
</template>

<script>
import { Grid } from 'ag-grid-community';
import 'ag-grid-community/dist/styles/ag-grid.css';
import 'ag-grid-community/dist/styles/ag-theme-material.css';
// import smoothReflow from 'vue-smooth-reflow';
import gql from 'graphql-tag';
import apolloClient from '../apollo';
import logger from '../logger';
// import i18n from '../locale';
// import AxForm from './AxForm.vue';

export default {
  name: 'AxGrid',
  components: {},
  props: {
    form: null,
    grid: {
      type: String,
      default: 'default'
    },
    update_time: null
  },
  data() {
    return {
      gridObj: null,
      rowData: [],
      name: null,
      dbName: null,
      formGuid: null,
      columns: null,
      options: null
    };
  },
  computed: {
    columnDefs() {
      const columnDefs = [];
      this.columns.forEach(column => {
        columnDefs.push({
          headerName: column.field.name,
          field: column.field.dbName
        });
      });
      return columnDefs;
    }
  },
  watch: {},
  mounted() {
    this.loadOptions(this.form, this.grid);
  },
  methods: {
    openForm(event) {
      this.$modal.show('sub-form');
      this.$log.info(event);
      // this.dialogIsOpen = true;
      // this.$modal.open(AxGridModal);
    },
    loadOptions(formDbName, gridDbName) {
      const GET_GRID_DATA = gql`
        query($formDbName: String!, $gridDbName: String!) {
          grid(formDbName: $formDbName, gridDbName: $gridDbName) {
            guid
            name
            dbName
            formGuid
            columns {
              edges {
                node {
                  guid
                  position
                  field {
                    guid
                    dbName
                    name
                    fieldType {
                      tag
                      icon
                    }
                  }
                  columnType
                  aggregationType
                  optionsJson
                }
              }
            }
            optionsJson
            isDefaultView
          }
        }
      `;

      apolloClient
        .query({
          query: GET_GRID_DATA,
          variables: {
            formDbName,
            gridDbName
          }
        })
        .then(data => {
          const gridData = data.data.grid;
          this.guid = gridData.guid;
          this.name = gridData.name;
          this.dbName = gridData.dbName;
          this.formGuid = gridData.formGuid;
          this.options = JSON.parse(gridData.optionsJson);
          this.columns = gridData.columns
            ? gridData.columns.edges.map(edge => edge.node)
            : null;

          this.loadData();
        })
        .catch(error => {
          logger.error(
            `Error in AxGrid => loadOptions apollo client => ${error}`
          );
        });
    },
    loadData() {
      const GRID_DATA = placeholder => gql`
        query {
          ${this.form} {
              ${placeholder}
          }
        }
      `;
      let placeholder = 'guid';
      this.columns.forEach(column => {
        placeholder += `, ${column.field.dbName}`;
      });
      const dataQuery = GRID_DATA(placeholder);

      apolloClient
        .query({
          query: dataQuery,
          variables: {}
        })
        .then(data => {
          this.rowData = data.data[this.form];
          this.initAgGrid();
        })
        .catch(error => {
          logger.error(`Error in AxGrid => loadData apollo client => ${error}`);
        });
    },
    initAgGrid() {
      const gridOptions = {
        columnDefs: this.columnDefs,
        rowData: this.rowData
      };
      gridOptions.onRowDoubleClicked = event => this.openForm(event);
      this.gridObj = new Grid(this.$refs.grid, gridOptions);
    }
  }
};
</script>

<style scoped>
.grid {
  width: 100%;
  height: 100%;
}
</style>
