import apolloClient from '../../apollo';
import gql from 'graphql-tag';
import logger from '../../logger';
import i18n from '../../locale.js';


const ColumnFragment = gql`
  fragment ColumnFragment on Column {
    guid,
    position,
    field {
      guid,
      name,
      fieldType {
        tag,
        icon
      }
    },
    columnType,
    aggregationType,
    optionsJson
  }
`;

const GET_GRID_DATA = gql`
  query ($formDbName: String!, $gridDbName: String!) {
    grid (formDbName: $formDbName, gridDbName: $gridDbName) {
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
      optionsJson,
      isDefaultView,
    }
  }
  ${ColumnFragment}
`;

const CREATE_COLUMN = gql`
  mutation ($gridGuid: String!, $fieldGuid: String!, $columnType: String!, $position: Int!, $positions: [PositionInput] ) {
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
  setGridData(state, grid) {
    if (grid) {
      state.guid = grid.guid;
      state.name = grid.name;
      state.dbName = grid.dbName;
      state.formGuid = grid.formGuid;
      state.options = JSON.parse(grid.optionsJson);
      state.isDefaultView = grid.isDefaultView;
      state.columns = grid.columns ? grid.columns.edges.map(edge => edge.node) : null;
    } else {
      state.guid = null;
      state.name = null;
      state.dbName = null;
      state.formGuid = null;
      state.options = null;
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
  setUpdateTime(state, time) {
    state.updateTime = time;
  },
  setCreatedGridDbName(state, dbName) {
    state.createdGridDbName = dbName;
  },
  setDeletedFlag(state, isDeleted) {
    state.deletedFlag = isDeleted;
  },
  setColumnWidth(state, colData) {
    if (!('widths' in state.options)) state.options.widths = {};
    state.options.widths[colData.column] = colData.width;
  },
  setFilterModel(state, colData) {
    state.options.filterModel = colData.data;
  },
  setSortModel(state, colData) {
    state.options.sortModel = colData.data;
  },
  combineOptions(state, optionsPart) {
    Object.keys(optionsPart).forEach(key => {
      state.options[key] = optionsPart[key];
    });
  }

};

const getters = {
  columnTreeData(state) {
    const treeData = [];

    treeData.push({
      id: 'columns', parent: '#', text: "<i class='fas fa-columns' ></i> &nbsp; Columns", type: 'agg', data: { position: 1 }
    });
    treeData.push({
      id: 'all', parent: 'columns', text: "<i class='fas fa-mobile-alt' ></i> &nbsp; All media", type: 'group', data: { position: 1 }
    });
    treeData.push({
      id: 'mid', parent: 'columns', text: "<i class='fas fa-tablet-alt' ></i> &nbsp; Tablet", type: 'group', data: { position: 2 }
    });
    treeData.push({
      id: 'big', parent: 'columns', text: "<i class='fas fa-laptop' ></i> &nbsp; Laptop +", type: 'group', data: { position: 3 }
    });

    state.columns.forEach(column => {
      const node = {
        id: column.guid,
        parent: column.columnType,
        text: `<i class='fas fa-${column.field.fieldType.icon}'></i>&nbsp;${column.field.name}`,
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
        context.commit('setGridData', data.data.grid);
        context.commit('setUpdateTime', Date.now());
      })
      .catch(error => {
        logger.error(`Error in getGridData apollo client => ${error}`);
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
        logger.error(`Error in createColumn apollo client => ${error}`);
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
        logger.error(`Error in deleteColumn apollo client => ${error}`);
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
        logger.error(`Error in changeColumnsPositions apollo client => ${error}`);
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
      })
      .catch(error => {
        logger.error(`Error in createColumn apollo client => ${error}`);
      });
  },

  updateGrid(context, payload) {
    let currentName = context.state.name;
    let currentDbName = context.state.dbName;
    let currentOptionsJson = JSON.stringify(context.state.options);

    if ('name' in payload) currentName = payload.name;
    if ('dbName' in payload) currentDbName = payload.dbName;
    if ('optionsJson' in payload) currentOptionsJson = JSON.stringify(payload.optionsJson);

    apolloClient.mutate({
      mutation: UPDATE_GRID,
      variables: {
        guid: context.state.guid,
        name: currentName,
        dbName: currentDbName,
        optionsJson: currentOptionsJson
      }
    })
      .then(data => {
        const newGrid = data.data.updateGrid.grid;
        const shortGrid = {
          guid: newGrid.guid,
          name: newGrid.name,
          dbName: newGrid.dbName,
          position: newGrid.position,
          isDefaultView: newGrid.isDefaultView
        };
        context.commit('updateGrid', newGrid);
        context.commit('form/updateGrid', shortGrid, { root: true });
      })
      .catch(error => {
        logger.error(`Error in updateGrid apollo client => ${error}`);
      });
  },

  deleteGrid(context) {
    apolloClient.mutate({
      mutation: DELETE_GRID,
      variables: {
        guid: context.state.guid
      }
    })
      .then(data => {
        const isDeleted = data.data.createGrid.deleted;
        context.commit('setDeletedFlag', true);
        context.commit('form/deleteGrid', isDeleted, { root: true });
      })
      .catch(error => {
        logger.error(`Error in deleteGrid apollo client => ${error}`);
      });
  }

};

const state = {
  guid: null,
  formGuid: null,
  formDbName: null,
  name: null,
  dbName: null,
  options: {},
  isDefaultView: null,
  columns: [],
  otherGrids: [],
  gotoGridDbName: null,
  updateTime: null,
  deletedFlag: null,
  loadingDone: false
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
