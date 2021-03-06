import apolloClient from '@/apollo';
import gql from 'graphql-tag';
import logger from '@/logger';
import i18n from '@/locale.js';

const getDefaultState = () => {
  return {
    guid: null,
    formGuid: null,
    formDbName: null,
    name: null,
    dbName: null,
    code: null,
    options: {},
    isDefaultView: null,
    columns: [],
    otherGrids: [],
    gotoGridDbName: null,
    updateTime: null,
    deletedFlag: null,
    loadingDone: false,
    doSaveSortFilterModel: false
  }
}

const ColumnFragment = gql`
  fragment ColumnFragment on Column {
    guid,
    position,
    field {
      guid,
      name,
      dbName,
      fieldType {
        tag,
        icon,
        valueType
      }
    },
    columnType,
    aggregationType,
    optionsJson
  }
`;

const GET_GRID_DATA = gql`
  query ($formDbName: String!, $gridDbName: String!, $updateTime: String) {
    axGrid (formDbName: $formDbName, gridDbName: $gridDbName, updateTime: $updateTime) {
      guid,
      name,
      dbName,
      formGuid,
      columns {
        edges {
          node {    
            ...ColumnFragment
          }
        }
      },
      codeNotNone,
      optionsJson,
      isDefaultView,
    }
  }
  ${ColumnFragment}
`;

const CREATE_COLUMN = gql`
  mutation ($gridGuid: String!, $fieldGuid: String!, $columnType: String, $position: Int, $positions: [PositionInput] ) {
    createColumn(gridGuid: $gridGuid, fieldGuid: $fieldGuid, columnType: $columnType, position: $position,  positions: $positions) {
      column {
        ...ColumnFragment
      },
      ok
    }
  }
  ${ColumnFragment}
`;

const DELETE_COLUMN = gql`
  mutation ($guid: String!) {
    deleteColumn(guid: $guid) {
      deleted,
      ok    
    }
  }
`;

const CHANGE_COLUMNS_POSITIONS = gql`
  mutation ($gridGuid: String!, $positions: [PositionInput]) {
      changeColumnsPositions(gridGuid: $gridGuid, positions: $positions) {
        columns {
          ...ColumnFragment
        }
      }
  }
  ${ColumnFragment}
`;

const CREATE_GRID = gql`
  mutation ($formGuid: String!, $name: String!) {
    createGrid(formGuid: $formGuid, name: $name) {
      grid {
        guid,
        name,
        dbName,
        formGuid,
        codeNotNone,
        optionsJson,
        isDefaultView,
        columns {
          edges {
            node {    
              ...ColumnFragment
            }
          }
        }
      },
      ok
    }
  }
  ${ColumnFragment}
`;


const DELETE_GRID = gql`
  mutation ($guid: String!) {
    deleteGrid(guid: $guid) {
      deleted,
      ok    
    }
  }
`;


const UPDATE_GRID = gql`
  mutation ($guid: String!, $name: String!, $dbName: String, $optionsJson: String, $isDefaultView: Boolean) {
    updateGrid(guid: $guid, name: $name, dbName: $dbName, optionsJson: $optionsJson, isDefaultView: $isDefaultView) {
      grid {
        guid,
        name,
        dbName,
        formGuid,
        optionsJson,
        isDefaultView,
        columns {
          edges {
            node {    
              ...ColumnFragment
            }
          }
        }
      },
      ok
    }
  }
  ${ColumnFragment}
`;


const mutations = {
  resetState(state) {
    Object.assign(state, getDefaultState())
  },
  setGridData(state, grid) {
    if (grid) {
      state.guid = grid.guid;
      state.name = grid.name;
      state.dbName = grid.dbName;
      state.formGuid = grid.formGuid;
      state.options = JSON.parse(grid.optionsJson);
      state.code = grid.codeNotNone;
      state.isDefaultView = grid.isDefaultView;
      state.columns = grid.columns ? grid.columns.edges.map(edge => edge.node) : null;
    } else {
      state.guid = null;
      state.name = null;
      state.dbName = null;
      state.formGuid = null;
      state.options = null;
      state.code = null;
      state.isDefaultView = null;
      state.columns = [];
    }
    state.loadingDone = true;
  },
  updateGrid(state, grid) {
    state.name = grid.name;
    state.dbName = grid.dbName;
    state.options = JSON.parse(grid.optionsJson);
    state.isDefaultView = grid.isDefaultView;
    state.columns = grid.columns ? grid.columns.edges.map(edge => edge.node) : null;
  },
  setColumns(state, columns) {
    state.columns = columns;
  },
  addColumn(state, column) {
    state.columns.push(column);
  },
  updateColumn(state, newColumn) {
    state.fields = [
      ...state.columns.filter(element => element.guid !== newColumn.guid),
      newColumn
    ];
  },
  deleteColumn(state, deleted) {
    state.columns = [...state.columns.filter(element => element.guid !== deleted)];
  },
  deleteField(state, deleted) {
    state.columns = [...state.columns.filter(element => element.field.guid !== deleted)];
  },
  setUpdateTime(state, time) {
    state.updateTime = time;
  },
  setCreatedGridDbName(state, dbName) {
    state.createdGridDbName = dbName;
  },
  setDeletedFlag(state, isDeleted) {
    state.deletedFlag = isDeleted;
  },
  setColumnWidths(state, colsData) {
    if (!('widths' in state.options)) state.options.widths = {};
    colsData.forEach(col => {
      state.options.widths[col.colId] = col.width;
    });
  },
  setFilterModel(state, colData) {

    state.options.filterModel = colData;
  },
  setSortModel(state, colData) {
    state.options.sortModel = colData;
  },
  combineOptions(state, optionsPart) {
    Object.keys(optionsPart).forEach(key => {
      state.options[key] = optionsPart[key];
    });
  },
  setFormDbName(state, formDbName) {
    state.formDbName = formDbName;
  },
  setCode(state, code) {
    state.code = code;
  },
  setDoSaveSortFilterModel(state, doSave) {
    state.doSaveSortFilterModel = doSave;
  }
};

const getters = {
  columnTreeData(state) {
    const treeData = [];
    const columnsText = `<i class='fas fa-columns' ></i> &nbsp; ${i18n.t('grids.columns')}`;
    treeData.push({
      id: 'columns', parent: '#', text: columnsText, type: 'group', data: { position: 1 }
    });

    state.columns.forEach(column => {
      const node = {
        id: column.guid,
        parent: 'columns',
        text: `<i class='${column.field.fieldType.icon}'></i>&nbsp;${column.field.name}`,
        type: 'default',
        data: { position: column.position }
      };
      treeData.push(node);
    });
    return treeData;
  }
};

const actions = {
  getGridData(context, payload) {
    apolloClient.query({
      query: GET_GRID_DATA,
      variables: {
        formDbName: payload.formDbName,
        gridDbName: payload.gridDbName,
        updateTime: Date.now()
      }
    })
      .then(data => {
        if (data.data.axGrid) {
          context.commit('setGridData', data.data.axGrid);
          context.commit('setUpdateTime', Date.now());
        } else {
          logger.error(`Cant find grid => ${payload.gridDbName}`);
          const url = `/admin/${payload.formDbName}/form`;
          context.commit('home/setRedirectNeededUrl', url, { root: true });
        }
      })
      .catch(error => {
        const msg = `Error in getGridData apollo client => ${error}`;
        context.commit('home/setShowErrorMsg', msg, { root: true });
      });
  },

  createColumn(context, payload) {
    apolloClient.mutate({
      mutation: CREATE_COLUMN,
      variables: {
        gridGuid: context.state.guid,
        fieldGuid: payload.fieldGuid,
        columnType: payload.columnType,
        position: payload.position,
        positions: payload.positions
      }
    })
      .then(data => {
        const newColumn = data.data.createColumn.column;
        context.commit('addColumn', newColumn);
        context.commit('setUpdateTime', Date.now());
      })
      .catch(error => {
        const msg = `Error in createColumn apollo client => ${error}`;
        context.commit('home/setShowErrorMsg', msg, { root: true });
      });
  },

  deleteColumn(context, payload) {
    apolloClient.mutate({
      mutation: DELETE_COLUMN,
      variables: {
        guid: payload.guid
      }
    })
      .then(data => {
        const deletedGuid = data.data.deleteColumn.deleted;
        context.commit('deleteColumn', deletedGuid);
        context.commit('setUpdateTime', Date.now());
      })
      .catch(error => {
        const msg = `Error in deleteColumn apollo client => ${error}`;
        context.commit('home/setShowErrorMsg', msg, { root: true });
      });
  },

  changeColumnsPositions(context, payload) {
    apolloClient.mutate({
      mutation: CHANGE_COLUMNS_POSITIONS,
      variables: {
        gridGuid: context.state.guid,
        positions: payload.positions
      }
    })
      .then(data => {
        context.commit('setColumns', data.data.changeColumnsPositions.columns);
        context.commit('setUpdateTime', Date.now());
      })
      .catch(error => {
        const msg = `Error in changeColumnsPositions apollo client => ${error}`;
        context.commit('home/setShowErrorMsg', msg, { root: true });
      });
  },


  createGrid(context) {
    apolloClient.mutate({
      mutation: CREATE_GRID,
      variables: {
        formGuid: context.state.formGuid,
        name: i18n.t('grids.default-name')
      }
    })
      .then(data => {
        const newGrid = data.data.createGrid.grid;
        context.commit('setCreatedGridDbName', newGrid.dbName);
        context.commit('form/addGrid', newGrid, { root: true });
        context.commit('home/addGrid', newGrid, { root: true });
        const url = `/admin/${context.state.formDbName}/grids/${newGrid.dbName}`;
        context.commit('home/setRedirectNeededUrl', url, { root: true });
      })
      .catch(error => {
        const msg = `Error in createGrid apollo client => ${error}`;
        context.commit('home/setShowErrorMsg', msg, { root: true });
      });
  },

  updateGrid(context, payload) {
    let currentName = context.state.name;
    let currentDbName = context.state.dbName;
    let currentOptionsJson = JSON.stringify(context.state.options);
    let currentIsDefaultView = context.state.isDefaultView;
    let redirectNeeded = false;

    if ('name' in payload) currentName = payload.name;
    if ('dbName' in payload) {
      currentDbName = payload.dbName;
      redirectNeeded = true;
    }
    if ('optionsJson' in payload) currentOptionsJson = JSON.stringify(payload.optionsJson);
    if ('isDefaultView' in payload) currentIsDefaultView = payload.isDefaultView;

    apolloClient.mutate({
      mutation: UPDATE_GRID,
      variables: {
        guid: context.state.guid,
        name: currentName,
        dbName: currentDbName,
        optionsJson: currentOptionsJson,
        isDefaultView: currentIsDefaultView
      }
    })
      .then(data => {
        const newGrid = data.data.updateGrid.grid;
        const shortGrid = {
          guid: newGrid.guid,
          name: newGrid.name,
          dbName: newGrid.dbName,
          position: newGrid.position,
          isDefaultView: newGrid.isDefaultView,
          formGuid: context.state.formGuid
        };
        context.commit('updateGrid', newGrid);
        context.commit('form/updateGrid', shortGrid, { root: true });
        context.commit('home/updateGrid', shortGrid, { root: true });

        if (payload.updateNeeded) context.commit('setUpdateTime', Date.now());

        if (redirectNeeded) {
          const url = `/admin/${context.state.formDbName}/grids/${currentDbName}`;
          context.commit('home/setRedirectNeededUrl', url, { root: true });
        }
      })
      .catch(error => {
        const msg = `Error in updateGrid apollo client => ${error}`;
        context.commit('home/setShowErrorMsg', msg, { root: true });
      });
  },

  deleteGrid(context, payload) {
    apolloClient.mutate({
      mutation: DELETE_GRID,
      variables: {
        guid: context.state.guid
      }
    })
      .then(data => {
        const isDeleted = data.data.deleteGrid.deleted;
        context.commit('setDeletedFlag', true);
        context.commit('form/deleteGrid', isDeleted, { root: true });
        const url = `/admin/${context.state.formDbName}/grids/${payload.defaultGridDbName}`;
        context.commit('home/setRedirectNeededUrl', url, { root: true });
      })
      .catch(error => {
        const msg = `Error in deleteGrid apollo client => ${error}`;
        context.commit('home/setShowErrorMsg', msg, { root: true });
      });
  }

};

const state = getDefaultState();

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
