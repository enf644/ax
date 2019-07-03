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
    grid (formDbName: $formDbName, gridDbName: $gridDbName, updateTime: $updateTime) {
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
  },
  setFormDbName(state, formDbName) {
    state.formDbName = formDbName;
  }

};

const getters = {
  serverFilterRulesCount(state) {
    if (state.options.serverFilter
      && state.options.serverFilterRules.rules
      && state.options.serverFilterRules.rules.length > 0) {
      return state.options.serverFilterRules.rules.length;
    }
    return 0;
  },
  columnTreeData(state) {
    const treeData = [];
    const columnsText = `<i class='fas fa-columns' ></i> &nbsp; ${i18n.t('grids.columns')}`;
    treeData.push({
      id: 'columns', parent: '#', text: columnsText, type: 'group', data: { position: 1 }
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
  },

  serverFilterData(state) {
    const filters = [
      {
        id: 'guid',
        label: 'Guid',
        type: 'string'
      },
      {
        id: 'axState',
        label: 'Workflow state',
        type: 'string'
      }
    ];

    state.columns.forEach(column => {
      let theType = 'string';
      let operators = [];
      const theInput = 'text';
      let values = [];
      const valueTypeName = column.field.fieldType.valueType.toUpperCase();

      if (valueTypeName.includes('INT')) {
        theType = 'integer';
        operators = ['equal', 'not_equal', 'in', 'not_in', 'less', 'less_or_equal', 'greater', 'greater_or_equal', 'between', 'not_between', 'is_empty', 'is_not_empty', 'is_null', 'is_not_null'];
      }
      if (valueTypeName.includes('FLOAT')) {
        theType = 'double';
        operators = ['equal', 'not_equal', 'in', 'not_in', 'less', 'less_or_equal', 'greater', 'greater_or_equal', 'between', 'not_between', 'is_empty', 'is_not_empty', 'is_null', 'is_not_null'];
      }
      if (valueTypeName.includes('DOUBLE')) {
        theType = 'double';
        operators = ['equal', 'not_equal', 'in', 'not_in', 'less', 'less_or_equal', 'greater', 'greater_or_equal', 'between', 'not_between', 'is_empty', 'is_not_empty', 'is_null', 'is_not_null'];
      }
      if (valueTypeName.includes('DECIMAL')) {
        theType = 'double';
        operators = ['equal', 'not_equal', 'in', 'not_in', 'less', 'less_or_equal', 'greater', 'greater_or_equal', 'between', 'not_between', 'not_ends_with', 'is_empty', 'is_not_empty', 'is_null', 'is_not_null'];
      }
      if (valueTypeName.includes('DATE')) {
        theType = 'date';
        operators = ['equal', 'not_equal', 'in', 'not_in', 'less', 'less_or_equal', 'greater', 'greater_or_equal', 'between', 'not_between', 'begins_with', 'not_begins_with', 'contains', 'not_contains', 'ends_with', 'not_ends_with', 'is_empty', 'is_not_empty', 'is_null', 'is_not_null'];
      }
      if (valueTypeName.includes('TIME')) {
        theType = 'date';
        operators = ['equal', 'not_equal', 'in', 'not_in', 'less', 'less_or_equal', 'greater', 'greater_or_equal', 'between', 'not_between', 'begins_with', 'not_begins_with', 'contains', 'not_contains', 'ends_with', 'not_ends_with', 'is_empty', 'is_not_empty', 'is_null', 'is_not_null'];
      }
      if (valueTypeName.includes('VARCHAR')) {
        theType = 'string';
        operators = ['equal', 'not_equal', 'in', 'not_in', 'begins_with', 'not_begins_with', 'contains', 'not_contains', 'ends_with', 'not_ends_with', 'is_empty', 'is_not_empty', 'is_null', 'is_not_null'];
      }
      if (valueTypeName.includes('TEXT')) {
        theType = 'string';
        operators = ['equal', 'not_equal', 'in', 'not_in', 'begins_with', 'not_begins_with', 'contains', 'not_contains', 'ends_with', 'not_ends_with', 'is_empty', 'is_not_empty', 'is_null', 'is_not_null'];
      }
      if (valueTypeName.includes('BOOL')) {
        theType = 'boolean';
        operators = ['equal', 'not_equal', 'is_null', 'is_not_null'];
        values = [
          { 1: 'True' },
          { 0: 'False' }
        ];
      }

      const newFilter = {
        id: column.field.dbName,
        label: column.field.name,
        type: theType,
        operators,
        input: theInput,
        values
      };
      filters.push(newFilter);
    });
    return filters;
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
        if (data.data.grid) {
          context.commit('setGridData', data.data.grid);
          context.commit('setUpdateTime', Date.now());
        } else {
          logger.error(`Cant find grid => ${payload.gridDbName}`);
          const url = `/admin/${payload.formDbName}/form`;
          context.commit('home/setRedirectNeededUrl', url, { root: true });
        }
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
        context.commit('home/addGrid', newGrid, { root: true });
        const url = `/admin/${context.state.formDbName}/grids/${newGrid.dbName}`;
        context.commit('home/setRedirectNeededUrl', url, { root: true });
      })
      .catch(error => {
        logger.error(`Error in createGrid apollo client => ${error}`);
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
        logger.error(`Error in updateGrid apollo client => ${error}`);
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
