<template>
  <div class='ax-grid-app' id='ax-grid'>
    <v-sheet :class='sheetClass' elevation='5' light ref='sheet'>
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
        <v-btn :key='action.guid' @click='doAction(action)' small v-for='action in this.actions'>
          <i :class='getActionIconClass(action)'></i>
          &nbsp;
          {{ action.name }}
        </v-btn>
      </div>

      <div class='actions' v-if='this.isTomMode'>
        <v-btn @click='emitSelectedItems' small>
          <i class='fas fa-check-double'></i>
          &nbsp; {{locale("grids.select-relation")}}
        </v-btn>
      </div>
      <div class='actions' v-if='this.isTomInlineMode'>
        <v-btn @click='emitSelectDialog' small>
          <i class='fas fa-check-double'></i>
          &nbsp; {{locale("grids.open-select-dialog")}}
        </v-btn>
      </div>
    </v-sheet>
    <modal :name='`sub-form-${this.modalGuid}`' adaptive height='auto' scrollable width='70%'>
      <v-card>
        <v-btn :ripple='false' @click='closeModal' class='close' color='black' icon text>
          <i class='fas fa-times close-ico'></i>
        </v-btn>
        <AxForm
          :action_guid='selectedActionGuid'
          :db_name='form'
          :guid='selectedGuid'
          @close='updateAndClose'
          @updated='updateGrid'
        ></AxForm>
      </v-card>
    </modal>
  </div>
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
import i18n from '@/locale';
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
      default: 'Default'
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
      selectedActionGuid: null,
      quickSearch: null,
      gridInitialized: false,
      modalGuid: null,
      actions: null
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
            // prettier-ignore
            columnPromise = () => import(
              `@/components/AxFields/${camelName}/${camelName}Column.vue`
            ).then(
              m => m.default
            );

            Vue.customElement(kebabName, columnPromise, {
              props: ['options_json']
            });
            renderer = params => `<${kebabName} options_json='${column.field.optionsJson}'>${params.value}</${kebabName}>`;
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
        if (this.tom_inline_mode !== undefined) {
          const tomRenderer = params => {
            const eDiv = document.createElement('div');
            eDiv.innerHTML = "<i class='fas fa-trash-alt tom-remove'></i>";
            const eButton = eDiv.querySelectorAll('.tom-remove')[0];

            eButton.addEventListener('click', () => {
              this.$emit('tomRemove', params.value);
            });
            return eDiv;
          };

          columnDefs.push({
            colId: 'tom_delete',
            headerName: '',
            field: 'guid',
            width: 50,
            cellRenderer: tomRenderer
          });
        }

        return columnDefs;
      } catch (error) {
        logger.error(`Error in AxGrid, columnDefs => ${error}`);
        return null;
      }
    }
  },
  computed: {
    sheetClass() {
      if (this.options && this.options.enableFlatMode) return 'sheet-flat';
      return 'sheet';
    },
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
      if (this.tom_inline_mode !== undefined) return false;
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
    },
    formAndGrid() {
      return this.form + this.grid;
    }
  },
  watch: {
    update_time(newValue, oldValue) {
      this.reloadGrid();
    },
    quickSearch(newValue) {
      this.gridObj.gridOptions.api.setQuickFilter(newValue);
    },
    formAndGrid() {
      this.reloadGrid();
    }
  },
  created() {
    this.modalGuid = uuid4();
  },
  mounted() {
    this.loadOptions(this.form, this.grid);
  },
  methods: {
    reloadGrid() {
      if (this.gridObj.gridOptions && this.gridObj.gridOptions.api) {
        this.gridObj.gridOptions.api.destroy();
      }
      this.gridInitialized = false;
      this.loadOptions(this.form, this.grid);
    },
    locale(key) {
      return i18n.t(key);
    },
    updateAndClose(guid) {
      if (!this.options.enableSubscription) {
        this.loadData();
        setTimeout(() => {
          this.highliteRow(guid);
        }, 100);
      }
      this.closeModal();
    },
    updateGrid(guid) {
      if (!this.options.enableSubscription) {
        this.loadData();
        setTimeout(() => {
          this.highliteRow(guid);
        }, 100);
      }
    },
    subscribeToActions() {
      const ACTION_SUBSCRIPTION_QUERY = gql`
        subscription($formDbName: String!, $rowGuid: String) {
          actionNotify(formDbName: $formDbName, rowGuid: $rowGuid) {
            formGuid
            formDbName
            rowGuid
          }
        }
      `;

      apolloClient
        .subscribe({
          query: ACTION_SUBSCRIPTION_QUERY,
          variables: {
            formDbName: this.form
          }
        })
        .subscribe(
          data => {
            this.loadData();
            setTimeout(() => {
              this.highliteRow(data.data.actionNotify.rowGuid);
            }, 500);
            // logger.info(`Action subscribtion data recieved: ${data}`);
          },
          {
            error(error) {
              logger.error(`ERRROR in GQL subscribeToActions => ${error}`);
            }
          }
        );
    },
    highliteRow(guid) {
      const rowNode = this.gridObj.gridOptions.api.getRowNode(guid);
      if (rowNode) {
        const newData = { ...rowNode.data };
        newData.isHighlited = true;
        rowNode.setData(newData);

        setTimeout(() => {
          const node = this.gridObj.gridOptions.api.getRowNode(guid);
          if (node) {
            const oldData = { ...node.data };
            oldData.isHighlited = false;
            node.setData(oldData);
          }
        }, 400);
      }
    },
    loadOptions(formDbName, gridDbName) {
      // console.log(`get grid data - ${formDbName} , ${gridDbName}`);
      const GET_GRID_DATA = gql`
        query(
          $formDbName: String!
          $gridDbName: String!
          $currentState: String
          $updateTime: String
        ) {
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
                    optionsJson
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
          form(dbName: $formDbName, updateTime: $updateTime) {
            name
            icon
          }
          actionsAvalible(
            formDbName: $formDbName
            currentState: $currentState
            updateTime: $updateTime
          ) {
            guid
            name
            fromStateGuid
            toStateGuid
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
            currentState: null,
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
          this.actions = data.data.actionsAvalible;

          if (this.options.enableSubscription) this.subscribeToActions();
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
        impossibleGuid = 'de24a16e-3b4d-4abf-guid-imposible000';
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
            updateTime: Date.now(),
            quicksearch: impossibleGuid,
            guids: this.guidsString
          }
        })
        .then(data => {
          this.rowData = data.data[this.viewDbName];
          if (!this.gridInitialized) this.initAgGrid();
          else {
            const filterModel = this.gridObj.gridOptions.api.getFilterModel();
            this.gridObj.gridOptions.api.setRowData(this.rowData);
            this.gridObj.gridOptions.api.setFilterModel(filterModel);
          }
          // this.gridObj.gridOptions.api.setRowData(this.rowData);
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
          suppressScrollOnNewData: true,
          rowData: this.rowData,
          rowSelection: 'multiple',
          getRowNodeId: data => data.guid
        };
        // gridOptions.onRowClicked = event => {
        //   this.openForm(event.data.guid);
        // };
        gridOptions.onCellClicked = event => {
          if (event.column.colId !== 'tom_delete') {
            this.openForm(event.data.guid);
          }
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

        this.gridObj.gridOptions.rowClassRules = {
          'ax-highlited-row': params => params.data.isHighlited === true
        };

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
        this.gridInitialized = true;

        setTimeout(() => {
          if (this.isTomMode) {
            this.gridObj.gridOptions.suppressRowClickSelection = true;
            this.doPreselect(this.preselect);
          }
        }, 50);
      } catch (e) {
        logger.error(`ERROR initiating AG grid => ${e}`);
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
    },
    getActionIconClass(action) {
      if (action.icon) return `fas fa-${action.icon}`;
      return 'far fa-arrow-alt-circle-right';
    },
    doAction(action) {
      this.selectedGuid = null;
      this.selectedActionGuid = action.guid;
      this.$modal.show(`sub-form-${this.modalGuid}`);
    },
    openForm(guid) {
      if (this.options.enableOpenForm) {
        this.selectedGuid = guid;
        this.selectedActionGuid = null;
        this.$modal.show(`sub-form-${this.modalGuid}`);
      }
    },
    closeModal() {
      this.selectedGuid = null;
      this.$modal.hide(`sub-form-${this.modalGuid}`);
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
.sheet-flat {
  width: 100%;
}
.ax-grid-app {
  height: 100%;
  position: relative;
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
