<template>
  <v-app class='ax-grid-app' id='ax-grid'>
    <v-sheet class='sheet' elevation='5' light ref='sheet'>
      <div class='header'>
        <div class='grid-title' v-show='titleEnabled'>
          <i :class='`fas fa-${this.formIcon}`'></i>
          &nbsp; {{gridTitle}}
        </div>
        <div class='quick-search' v-show='quickSearchEnabled'>
          <v-text-field
            cy-data='quicksearch'
            label='Quick search'
            ref='quickSearch'
            v-model='quickSearch'
          ></v-text-field>
        </div>
      </div>

      <div :class='gridClass' ref='grid'></div>

      <div class='actions' v-show='actionsEnabled'>
        <v-btn @click='testAction' small>
          <i class='fas fa-tractor'></i>
          &nbsp; {{$t("grids.test-action")}}
        </v-btn>
      </div>
      <div class='actions' v-if='this.isTomMode'>
        <v-btn @click='emitSelectedItems' small>
          <i class='fas fa-check-double'></i>
          &nbsp; {{$t("grids.select-relation")}}
        </v-btn>
      </div>
      <div class='actions' v-if='this.isTomInlineMode'>
        <v-btn @click='emitSelectDialog' small>
          <i class='fas fa-check-double'></i>
          &nbsp; {{$t("grids.open-select-dialog")}}
        </v-btn>
      </div>
    </v-sheet>
    <modal :name='`sub-form-${this.modalGuid}`' adaptive height='auto' scrollable width='70%'>
      <v-card>
        <v-btn :ripple='false' @click='closeModal' class='close' color='black' flat icon>
          <i class='fas fa-times close-ico'></i>
        </v-btn>
        <AxForm :db_name='form' :guid='selectedGuid'></AxForm>
      </v-card>
    </modal>
  </v-app>
</template>

<script>
import Vue from 'vue';
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
import uuid4 from 'uuid4';

export default {
  name: 'AxGrid',
  components: { AxForm },
  props: {
    form: null,
    grid: {
      type: String,
      default: 'default'
    },
    update_time: null,
    tom_mode: null,
    to1_mode: null,
    tom_inline_mode: null,
    preselect: null,
    title: null,
    guids: null
  },
  data() {
    return {
      gridObj: null,
      rowData: [],
      name: null,
      dbName: null,
      formGuid: null,
      formDbName: null,
      formIcon: null,
      formName: null,
      isDefaultView: null,
      columns: null,
      options: null,
      selectedGuid: null,
      quickSearch: null,
      gridInitialized: false,
      modalGuid: null
    };
  },
  asyncComputed: {
    columnDefs() {
      try {
        if (!this.options || !this.columns) return null;

        let pinnedColumnsCounter = this.options.pinned;
        const columnDefs = [];
        let firstRun = false;
        if (this.to1_mode !== undefined || this.tom_mode !== undefined) {
          firstRun = true;
        }

        this.columns.forEach(column => {
          let currentWidth = null;
          let currentPinned = null;

          // if table have multiple columns with same field, we need to change name
          let sameDbNameCounter = 0;
          columnDefs.forEach(subColumn => {
            if (subColumn.field === column.field.dbName) sameDbNameCounter += 1;
          });
          let columnModelName = column.field.dbName;
          if (sameDbNameCounter > 0) {
            columnModelName = `${columnModelName}_${sameDbNameCounter}`;
          }

          // set width
          if (
            this.options.widths
            && Object.prototype.hasOwnProperty.call(
              this.options.widths,
              columnModelName
            )
          ) {
            currentWidth = this.options.widths[columnModelName];
          }

          // set pinned
          if (pinnedColumnsCounter * 1 > 0) {
            currentPinned = 'left';
            pinnedColumnsCounter -= 1;
          }

          let columnPromise = null;
          const camelName = column.field.fieldType.tag;
          const kebabName = `${camelName
            .replace(/([a-z])([A-Z])/g, '$1-$2')
            .toLowerCase()}-column`;

          let renderer = null;
          if (column.field.fieldType.isColumnnAvalible) {
            columnPromise = () => import(`@/components/AxFields/${camelName}/${camelName}Column.vue`).then(
                m => m.default
              );

            Vue.customElement(kebabName, columnPromise, {
              props: ['options_json']
            });

            renderer = params => `<${kebabName} 
                options_json='hello'>${params.value}</${kebabName}>`;
          } else {
            renderer = params => params.value;
          }

          // column.field.fieldType.tag
          // params.value

          columnDefs.push({
            headerName: column.field.name,
            field: column.field.dbName,
            width: currentWidth,
            pinned: currentPinned,
            cellRenderer: renderer,
            checkboxSelection: firstRun
          });

          firstRun = false;
        });
        return columnDefs;
      } catch (error) {
        this.$log.error(`Error in AxGrid, columnDefs => ${error}`);
        return null;
      }
    }
  },
  computed: {
    viewDbName() {
      if (this.isDefaultView) return this.form;
      return this.form + this.grid;
    },
    quickSearchEnabled() {
      if (!this.options) return false;
      return this.options.enableQuickSearch;
    },
    actionsEnabled() {
      if (!this.options) return false;
      if (this.to1_mode !== undefined) return false;
      if (this.tom_mode !== undefined) return false;
      return this.options.enableActions;
    },
    titleEnabled() {
      if (!this.options) return false;
      return this.options.enableTitle;
    },
    gridClass() {
      const themeClass = 'ag-theme-material';
      if (this.options) {
        if (
          (this.options.enableQuickSearch || this.options.enableTitle)
          && (this.options.enableActions || this.isTomInlineMode)
        ) {
          return `${themeClass} grid-search-actions`;
        }
        if (
          (this.options.enableQuickSearch || this.options.enableTitle)
          && !(this.options.enableActions || this.isTomInlineMode)
        ) {
          return `${themeClass} grid-search`;
        }
        if (
          !(this.options.enableQuickSearch || this.options.enableTitle)
          && (this.options.enableActions || this.isTomInlineMode)
        ) {
          return `${themeClass} grid-actions`;
        }
      }
      return `${themeClass} grid`;
    },
    isTomMode() {
      return this.tom_mode !== undefined;
    },
    isTomInlineMode() {
      return this.tom_inline_mode !== undefined;
    },
    gridTitle() {
      if (this.title) return this.title;
      return this.name;
    },
    guidsString() {
      if (this.tom_inline_mode === undefined) return null;
      const retObj = {
        items: this.guids
      };
      return JSON.stringify(retObj);
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
  created() {
    this.modalGuid = uuid4();
  },
  mounted() {
    this.loadOptions(this.form, this.grid);
  },
  methods: {
    testAction() {
      this.$log.info(' TEST ACTION ');
    },
    openForm(guid) {
      if (this.options.enableOpenForm) {
        this.selectedGuid = guid;
        this.$modal.show(`sub-form-${this.modalGuid}`);
      }
    },
    closeModal() {
      this.selectedGuid = null;
      this.$modal.hide(`sub-form-${this.modalGuid}`);
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
                      isColumnnAvalible
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
          form(dbName: $formDbName) {
            name
            icon
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
          this.formName = data.data.form.name;
          this.formIcon = data.data.form.icon;
          this.isDefaultView = gridData.isDefaultView;
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
      // If tom_inline_mode we use quicksearch with impossible query.
      // So only guids rows  will be returned
      let impossibleGuid = null;
      if (this.isTomInlineMode) {
        impossibleGuid = 'de24a16e-3b4d-4abf-8d50-0bb30f3e6aab';
      }

      const GRID_DATA = placeholder => gql`
        query ($updateTime: String, $quicksearch: String, $guids: String) {
          ${this.viewDbName} (
            updateTime: $updateTime, 
            quicksearch: $quicksearch, 
            guids: $guids) {
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
          variables: {
            updateTime: this.update_time,
            quicksearch: impossibleGuid,
            guids: this.guidsString
          }
        })
        .then(data => {
          this.rowData = data.data[this.viewDbName];
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
          rowData: this.rowData,
          rowSelection: 'multiple'
        };
        gridOptions.onRowClicked = event => {
          this.openForm(event.data.guid);
        };
        gridOptions.onRowSelected = event => this.rowSelected(event);
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
          if (this.isTomMode) {
            this.gridObj.gridOptions.suppressRowClickSelection = true;
            this.doPreselect(this.preselect);
          }
        }, 50);
      } catch (e) {
        this.$log.error(`ERROR initiating AG grid => ${e}`);
      }
    },
    rowSelected(event) {
      if (this.to1_mode !== undefined) {
        this.$emit('selected', event.node.data.guid);
      }
    },
    emitSelectedItems() {
      const selectedItems = this.gridObj.gridOptions.api.getSelectedRows();
      const selectedGuids = selectedItems.map(item => item.guid);
      this.$emit('selected', selectedGuids);
    },
    emitSelectDialog() {
      this.$emit('openSelectDialog');
    },
    doPreselect(selectedGuids) {
      if (selectedGuids) {
        this.gridObj.gridOptions.api.forEachNode(node => {
          if (selectedGuids.indexOf(node.data.guid) > -1) {
            node.setSelected(true);
          } else node.setSelected(false);
        });
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
.ax-grid-app {
  height: 100%;
}
.actions {
  margin: 15px 25px 0px 25px;
  height: 64px;
}
.close {
  position: absolute;
  right: 10px;
  top: 10px;
  z-index: 100;
}
.close-ico {
  font-size: 20px;
}
.header {
  justify-content: space-between;
  display: flex;
  vertical-align: middle;
  max-height: 52px;
}
.grid-title {
  margin-top: 16px;
  margin-left: 25px;
  font-size: 1.2em;
}
.quick-search {
  width: 300px;
  margin-left: auto;
  margin-right: 25px;
}
</style>
