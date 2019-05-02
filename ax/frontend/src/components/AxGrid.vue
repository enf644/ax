<template>
  <v-app class='ax-grid-app' id='ax-grid'>
    <v-sheet class='sheet' elevation='5' light ref='sheet'>
      <v-text-field
        class='quick-search'
        cy-data='quicksearch'
        label='Quick search'
        v-model='quickSearch'
        v-show='quickSearchEnabled'
      ></v-text-field>
      <div :class='gridClass' ref='grid'></div>
      <div class='actions' v-show='actionsEnabled'>
        <v-btn @click='testAction' small>
          <i class='fas fa-tractor'></i>
          &nbsp; {{$t("grids.test-action")}}
        </v-btn>
      </div>
    </v-sheet>
    <modal adaptive height='auto' name='sub-form' scrollable width='70%'>
      <v-card>
        <AxForm :db_name='form' :guid='selectedGuid' no_margin></AxForm>
      </v-card>
    </modal>
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
import AxForm from './AxForm.vue';
// import { print } from 'graphql/language/printer';

export default {
  name: 'AxGrid',
  components: { AxForm },
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
      options: null,
      selectedGuid: null,
      quickSearch: null,
      gridInitialized: false
    };
  },
  computed: {
    quickSearchEnabled() {
      if (!this.options) return false;
      return this.options.enableQuickSearch;
    },
    actionsEnabled() {
      if (!this.options) return false;
      return this.options.enableActions;
    },
    gridClass() {
      const themeClass = 'ag-theme-material';
      if (this.options) {
        if (this.options.enableQuickSearch && this.options.enableActions) {
          return `${themeClass} grid-search-actions`;
        }
        if (this.options.enableQuickSearch && !this.options.enableActions) {
          return `${themeClass} grid-search`;
        }
        if (!this.options.enableQuickSearch && this.options.enableActions) {
          return `${themeClass} grid-actions`;
        }
      }
      return `${themeClass} grid`;
    },
    columnDefs() {
      try {
        let pinnedColumnsCounter = this.options.pinned;
        const columnDefs = [];
        this.columns.forEach(column => {
          let currentWidth = null;
          let currentPinned = null;

          let sameDbNameCounter = 0;
          columnDefs.forEach(subColumn => {
            if (subColumn.field === column.field.dbName) sameDbNameCounter += 1;
          });

          let columnModelName = column.field.dbName;
          if (sameDbNameCounter > 0) {
            columnModelName = `${columnModelName}_${sameDbNameCounter}`;
          }
          if (
            this.options.widths
            && Object.prototype.hasOwnProperty.call(
              this.options.widths,
              columnModelName
            )
          ) {
            currentWidth = this.options.widths[columnModelName];
          }
          if (pinnedColumnsCounter * 1 > 0) {
            currentPinned = 'left';
            pinnedColumnsCounter -= 1;
          }

          columnDefs.push({
            headerName: column.field.name,
            field: column.field.dbName,
            width: currentWidth,
            pinned: currentPinned
          });
        });
        return columnDefs;
      } catch (error) {
        this.$log.error(`Error in AxGrid, columnDefs => ${error}`);
        return null;
      }
    }
  },
  watch: {
    update_time(newValue, oldValue) {
      if (oldValue && this.gridObj) {
        this.gridObj.gridOptions.api.destroy();
        this.loadOptions(this.form, this.grid);
      }
    },
    quickSearch(newValue) {
      this.gridObj.gridOptions.api.setQuickFilter(newValue);
    }
  },
  mounted() {
    this.loadOptions(this.form, this.grid);
  },
  methods: {
    testAction() {
      console.log(' TEST ACTION ');
    },
    openForm(guid) {
      if (this.options.enableOpenForm) {
        this.selectedGuid = guid;
        this.$modal.show('sub-form');
      }
    },
    loadOptions(formDbName, gridDbName) {
      const GET_GRID_DATA = gql`
        query($formDbName: String!, $gridDbName: String!, $updateTime: String) {
          grid(
            formDbName: $formDbName
            gridDbName: $gridDbName
            updateTime: $updateTime
          ) {
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
            gridDbName,
            updateTime: this.update_time
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
      try {
        const gridOptions = {
          defaultColDef: {
            sortable: this.options.enableSorting,
            resizable: this.options.enableColumnsResize,
            filter: this.options.enableFiltering
          },
          columnDefs: this.columnDefs,
          rowData: this.rowData
        };
        gridOptions.onRowClicked = event => this.openForm(event.data.guid);
        gridOptions.rowHeight = this.options.rowHeight;
        this.gridObj = new Grid(this.$refs.grid, gridOptions);

        if (this.options.filterModel != null) {
          this.gridObj.gridOptions.api.setFilterModel(this.options.filterModel);
        }

        if (this.options.sortModel != null) {
          this.gridObj.gridOptions.api.setSortModel(this.options.sortModel);
        }

        if (this.options.enableFlatMode) {
          this.gridObj.gridOptions.api.setDomLayout('print');
        }

        this.gridObj.gridOptions.onColumnResized = event => {
          const fieldDbName = event.column.colId;
          const fieldWidth = event.column.actualWidth;
          if (event.finished === true) {
            const eventData = {
              name: 'column-width',
              column: fieldDbName,
              width: fieldWidth
            };
            this.$emit('modify', eventData);
          }
        };

        this.gridObj.gridOptions.onFilterModified = () => {
          const filterModel = this.gridObj.gridOptions.api.getFilterModel();
          const eventData = {
            name: 'filter-change',
            data: filterModel
          };
          if (this.gridInitialized) this.$emit('modify', eventData);
        };

        this.gridObj.gridOptions.onSortChanged = () => {
          const sortModel = this.gridObj.gridOptions.api.getSortModel();
          const eventData = {
            name: 'sort-change',
            data: sortModel
          };
          if (this.gridInitialized) this.$emit('modify', eventData);
        };
        setTimeout(() => {
          this.gridInitialized = true;
        }, 50);
      } catch (e) {
        this.$log.error(`ERROR initiating AG grid => ${e}`);
      }
    }
  }
};
</script>

<style scoped>
.grid {
  width: 100%;
  height: 100%;
}
.grid-actions {
  width: 100%;
  height: calc(100% - 64px);
}
.grid-search {
  width: 100%;
  height: calc(100% - 64px);
}
.grid-search-actions {
  width: 100%;
  height: calc(100% - 128px);
}

.sheet {
  width: 100%;
  height: 100%;
}
.quick-search {
  width: 300px;
  margin-left: auto;
  margin-right: 25px;
}
.ax-grid-app {
  height: 100%;
}
.actions {
  margin: 0px 25px 0px 25px;
  height: 64px;
}
</style>
