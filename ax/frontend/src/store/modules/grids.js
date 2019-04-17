import apolloClient from '../../apollo';
import gql from 'graphql-tag';
import logger from '../../logger';
// import i18n from '../../locale.js';


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
      optionsJson,
      isDefaultView,
      columns {
        edges {
          node {    
            ...ColumnFragment
          }
        }
      }     
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


const mutations = {
  setGridData(state, data) {
    if (data) {
      state.guid = data.guid;
      state.name = data.name;
      state.dbName = data.dbName;
      state.formGuid = data.formGuid;
      state.options = JSON.parse(data.optionsJson);
      state.isDefaultView = data.isDefaultView;
      state.columns = data.columns ? data.columns.edges.map(edge => edge.node) : null;
    } else {
      state.guid = null;
      state.name = null;
      state.dbName = null;
      state.formGuid = null;
      state.options = null;
      state.isDefaultView = null;
      state.columns = [];
    }
  },
  setColumns(state, columns) {
    state.columns = columns;
  },
  addColumn(state, column) {
    state.columns.push(column);
  },
  updateField(state, newColumn) {
    state.fields = [
      ...state.columns.filter(element => element.guid !== newColumn.guid),
      newColumn
    ];
  },
  deleteColumn(state, deleted) {
    state.columns = [...state.columns.filter(element => element.guid !== deleted)];
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
        gridDbName: payload.gridDbName
      }
    })
      .then(data => {
        console.log(data.data.grid);
        context.commit('setGridData', data.data.grid);
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
      })
      .catch(error => {
        logger.error(`Error in createColumn apollo client => ${error}`);
      });
  }
};

const state = {
  guid: null,
  formGuid: null,
  formDbName: null,
  name: null,
  dbName: null,
  options: null,
  isDefaultView: null,
  columns: []
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
