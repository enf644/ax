<template>
  <div class='ax-grid-app' id='ax-grid' ref='gridWrapper'>
    <v-btn
      :class='{"reload-btn": !isToxModal,  "reload-btn-tom": isToxModal}'
      @click='reloadGrid'
      class='reload-btn'
      icon
      text
    >
      <i class='fas fa-redo-alt'></i>
    </v-btn>

    <v-alert :value='this.gqlException' type='error'>
      {{locale("grids.error-in-query")}} {{this.form}} {{this.grid}}
      <br />
      <br />
      {{errorText}}
    </v-alert>

    <v-alert :value='this.gridNotFound' type='error'>{{locale("grids.error-grid-not-found")}}</v-alert>

    <v-sheet
      :class='sheetClass'
      :elevation='elevation'
      light
      ref='sheet'
      v-show='this.gqlException == false'
    >
      <div class='header'>
        <div @click='openGridBlank()' class='grid-title' v-show='titleEnabled'>
          <i :class='`fas fa-${this.formIcon}`'></i>
          &nbsp; {{gridTitle}}
          <span class='hint' v-show='hint'>{{hint}} &nbsp;</span>
        </div>
        <div class='quick-search' v-show='quickSearchEnabled'>
          <v-text-field
            data-cy='quicksearch'
            label='Quick search'
            ref='quickSearch'
            v-model='quickSearch'
          ></v-text-field>
        </div>
      </div>

      <div :class='gridClass' ref='grid'></div>

      <div class='actions'>
        <div v-show='actionsEnabled'>
          <v-btn
            :key='action.guid'
            @click='doAction(action)'
            class='action-btn'
            small
            v-for='action in this.actions'
          >
            <i :class='getActionIconClass(action)'></i>
            &nbsp;
            {{ action.name }}
          </v-btn>
        </div>
        <div v-if='this.isTomMode'>
          <v-btn @click='emitSelectedItems' small>
            <i class='fas fa-check-double'></i>
            &nbsp; {{locale("grids.select-relation")}}
          </v-btn>
        </div>
        <div v-if='this.addRelationEnabled'>
          <v-btn @click='emitSelectDialog' small>
            <i class='fas fa-check-double'></i>
            &nbsp; {{addRelationButtonLabel}}
          </v-btn>
        </div>
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
import { getAxHost, getAxProtocol } from '@/misc';

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
    tom_children_mode: null,
    preselect: null,
    title: null,
    guids: null,
    arguments: null,
    width: null,
    height: null,
    tom_disabled: {
      type: Boolean,
      default: false
    },
    enable_add_relation: {
      type: Boolean,
      default: true
    },
    tom_add_btn_label: null,
    constructor_mode: {
      type: Boolean,
      default: false
    },
    hint: null
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
      actions: null,
      gqlException: false,
      gridNotFound: false,
      reloadIsActive: false,
      errorText: null
    };
  },
  asyncComputed: {
    rawArguments() {
      if (!this.arguments) return null;
      if (typeof this.arguments === 'string') return this.arguments;
      if (typeof this.arguments === 'object') {
        return JSON.stringify(this.arguments);
      }
      return null;
    },
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
            this.options.widths &&
            Object.prototype.hasOwnProperty.call(
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
            renderer = params =>
              `<${kebabName} options_json='${column.field.optionsJson}'>${params.value}</${kebabName}>`;
          } else {
            renderer = params => params.value;
          }

          // column.field.fieldType.tag
          // params.value

          let fieldDbName = column.field.dbName;
          if (column.field.fieldType.isVirtual) {
            fieldDbName = column.field.fieldType.virtualSource;
          }

          columnDefs.push({
            headerName: column.field.name,
            field: fieldDbName,
            width: currentWidth,
            pinned: currentPinned,
            cellRenderer: renderer,
            checkboxSelection: firstRun
          });

          firstRun = false;
        });
        if (this.tom_inline_mode !== undefined && this.tom_disabled != true) {
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
    // agGridStyle() {
    //   let retStyle = '';
    //   if (this.width) retStyle += `width: ${this.width}`;
    //   if (this.height) retStyle += ` height: ${this.height}`;
    //   return retStyle;
    // },
    elevation() {
      if (this.options && this.options.elevation) return this.options.elevation;
      return 0;
    },
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
    addRelationEnabled() {
      if (
        this.isTomInlineMode &&
        (this.enable_add_relation == true ||
          this.enable_add_relation == undefined)
      )
        return true;
      return false;
    },
    addRelationButtonLabel() {
      if (this.tom_add_btn_label) return this.tom_add_btn_label;
      return this.locale('grids.open-select-dialog');
    },
    actionsEnabled() {
      if (!this.options) return false;
      if (this.to1_mode !== undefined) return false;
      if (this.tom_mode !== undefined) return false;
      if (this.tom_children_mode !== undefined) return false;
      if (this.tom_disabled == true) return false;
      // if (this.tom_inline_mode !== undefined) return false;
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
          (this.options.enableQuickSearch || this.options.enableTitle) &&
          (this.options.enableActions || this.isTomInlineMode)
        ) {
          return `${themeClass} grid-search-actions`;
        }
        if (
          (this.options.enableQuickSearch || this.options.enableTitle) &&
          !(this.options.enableActions || this.isTomInlineMode)
        ) {
          return `${themeClass} grid-search`;
        }
        if (
          !(this.options.enableQuickSearch || this.options.enableTitle) &&
          (this.options.enableActions || this.isTomInlineMode)
        ) {
          return `${themeClass} grid-actions`;
        }
      }
      return `${themeClass} grid`;
    },
    isToxModal() {
      if (this.tom_mode !== undefined || this.to1_mode !== undefined) {
        return true;
      }
      return false;
    },
    isTomMode() {
      return this.tom_mode !== undefined;
    },
    isTomInlineMode() {
      return this.tom_inline_mode !== undefined && this.tom_disabled == false;
    },
    gridTitle() {
      if (this.title) return this.title;
      return this.name;
    },
    guidsString() {
      if (
        this.tom_inline_mode === undefined &&
        this.tom_children_mode === undefined
      )
        return null;
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
    update_time() {
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
      if (this.reloadIsActive == false) {
        this.reloadIsActive = true;
        if (
          this.gridObj &&
          this.gridObj.gridOptions &&
          this.gridObj.gridOptions.api
        ) {
          if (this.gridInitialized) {
            this.gridObj.gridOptions.api.destroy();
            this.gridInitialized = false;
          }
        }
        this.loadOptions(this.form, this.grid);
      }
    },
    locale(key) {
      return i18n.t(key);
    },
    updateAndClose(guid) {
      this.updateGrid(guid);
      this.closeModal();
    },
    updateGrid(guid) {
      if (
        this.tom_inline_mode !== undefined ||
        this.tom_children_mode !== undefined
      ) {
        this.$emit('added', guid);
      } else if (!this.options.enableSubscription) {
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
      const GET_GRID_DATA = gql`
        query(
          $formDbName: String!
          $gridDbName: String!
          $currentState: String
          $updateTime: String
        ) {
          axGrid(
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
                      isVirtual
                      virtualSource
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
          axForm(dbName: $formDbName, updateTime: $updateTime) {
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
          const gridData = data.data.axGrid;
          if (gridData == null) {
            this.gridNotFound = true;
          } else {
            this.guid = gridData.guid;
            this.name = gridData.name;
            this.dbName = gridData.dbName;
            this.formGuid = gridData.formGuid;
            this.formName = data.data.axForm.name;
            this.formIcon = data.data.axForm.icon;
            this.isDefaultView = gridData.isDefaultView;
            this.options = JSON.parse(gridData.optionsJson);
            this.columns = gridData.columns
              ? gridData.columns.edges.map(edge => edge.node)
              : null;
            this.actions = data.data.actionsAvalible;

            if (this.options.enableSubscription) this.subscribeToActions();
            this.loadData();
          }
        })
        .catch(error => {
          logger.error(
            `Error in AxGrid => loadOptions apollo client => ${error}`
          );
        });
    },
    loadData() {
      this.errorText = null;
      // If tom_inline_mode we use quicksearch with impossible query.
      // So only guids rows  will be returned
      let impossibleGuid = null;
      if (this.isTomInlineMode || this.tom_children_mode !== undefined) {
        impossibleGuid = 'de24a16e-3b4d-4abf-guid-imposible000';
      }

      const GRID_DATA = placeholder => gql`
        query ($updateTime: String, $quicksearch: String, $guids: String, $arguments: String) {
          ${this.viewDbName} (
            updateTime: $updateTime, 
            quicksearch: $quicksearch, 
            guids: $guids,
            arguments: $arguments
          ) {
            ${placeholder}
          }
        }
      `;
      let placeholder = 'guid';
      this.columns.forEach(column => {
        let fieldDbName = column.field.dbName;
        if (column.field.fieldType.isVirtual) {
          fieldDbName = column.field.fieldType.virtualSource;
        }
        placeholder += `, ${fieldDbName}`;
      });
      const dataQuery = GRID_DATA(placeholder);

      // if quicksearch or guids is not null - the grids python code will not be executed!
      // if quicksearch - then it is tom_inline.
      // if guids - then it is Ax1omTable
      const vars = {
        updateTime: Date.now(),
        quicksearch: impossibleGuid,
        guids: this.guidsString,
        arguments: this.rawArguments
      };
      apolloClient
        .query({
          query: dataQuery,
          variables: vars
        })
        .then(data => {
          this.gqlException = false;
          const rowsWithEmptyRows = data.data[this.viewDbName];

          this.rowData = null;
          // If all fields but guid is null - hide row
          if (rowsWithEmptyRows && rowsWithEmptyRows.length > 0) {
            this.rowData = rowsWithEmptyRows.filter(row => {
              let rowIsEmpty = true;
              Object.keys(row).forEach(key => {
                if (key != 'guid' && key != '__typename' && row[key] != null)
                  rowIsEmpty = false;
              });
              if (!rowIsEmpty) return row;
            });
          }

          if (!this.gridInitialized) {
            if (
              this.gridObj &&
              this.gridObj.gridOptions &&
              this.gridObj.gridOptions.api
            ) {
              this.gridObj.gridOptions.api.destroy();
              this.gridInitialized = false;
            }
            this.initAgGrid();
          } else {
            const filterModel = this.gridObj.gridOptions.api.getFilterModel();
            this.gridObj.gridOptions.api.setRowData(this.rowData);
            this.gridObj.gridOptions.api.setFilterModel(filterModel);

            if (this.rowData == null) {
              this.gridObj.gridOptions.api.showNoRowsOverlay();
            }
          }
          // this.gridObj.gridOptions.api.setRowData(this.rowData);
          this.reloadIsActive = false;
        })
        .catch(error => {
          this.reloadIsActive = false;
          this.gqlException = true;
          this.errorText = error;
          logger.error(`Error in AxGrid => loadData apollo client => ${error}`);
        });
    },
    initAgGrid() {
      try {
        if (this.width) this.$refs.gridWrapper.style.width = this.width;
        if (this.height) this.$refs.gridWrapper.style.height = this.height;

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

        if (this.constructor_mode) {
          this.gridObj.gridOptions.onColumnResized = event => {
            if (this.gridInitialized) {
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
            }
          };
        }

        this.gridObj.gridOptions.api.getSortModel();
        this.gridObj.gridOptions.api.getFilterModel();

        if (this.rowData == null) {
          this.gridObj.gridOptions.api.showNoRowsOverlay();
        }

        setTimeout(() => {
          this.gridInitialized = true;
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
    },
    openGridBlank() {
      const url = `${getAxProtocol()}://${getAxHost()}/grid/${this.form}/${
        this.grid
      }`;
      Object.assign(document.createElement('a'), {
        target: '_blank',
        href: url
      }).click();
    },
    getFilterModel() {
      return this.gridObj.gridOptions.api.getFilterModel();
    },
    getSortModel() {
      return this.gridObj.gridOptions.api.getSortModel();
    }
  }
};
</script>

<style scoped>
.reload-btn {
  position: absolute;
  right: 10px;
  top: 10px;
  z-index: 100;
}

.reload-btn-tom {
  position: absolute;
  right: 50px;
  top: 10px;
  z-index: 100;
}

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
  /* height: 64px; */
  min-height: 49px;
  display: flex;
  flex-direction: row;
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
  cursor: pointer;
}
.quick-search {
  width: 300px;
  margin-left: auto;
  margin-right: 25px;
}
.action-btn {
  margin-right: 10px;
}
.hint {
  color: rgba(0, 0, 0, 0.54);
  font-size: 12px;
  margin-top: '5px' !important;
  margin-left: 15px;
}
</style>
