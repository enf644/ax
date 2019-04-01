import apolloClient from '../../apollo';
import gql from 'graphql-tag';
import logger from '../../logger';
import i18n from '../../locale.js';

const GET_FORM_DATA = gql`
  query ($dbName: String!) {
    form (dbName: $dbName) {
      guid,
      name,
      dbName,
      parent,
      icon,
      fields {
        edges {
          node {    
            guid,
            name,
            dbName,
            position,
            valueType,
            fieldType {
              tag,
              icon,
              valueType
            },
            isTab,
            isRequired,
            isWholeRow,
            parent
          }
        }
      }, 
      grids {
        edges {
          node {
            guid,
            name,
            position,
            isDefaultView
          }
        }
      },
      roles {
        edges {
          node {
            guid,  
            name
          }
        }
      },          
      states {
        edges {
          node {
            guid,
            name,
            color,
            roles{
              edges {
                node {
                  guid
                }
              }
            },
            isStart,
            isEnd,
            isAll            
          }
        }
      },
      actions {
        edges {
          node {
            guid,
            name,
            roles{
              edges {
                node {
                  guid
                }
              }
            },
            fromStateGuid,
            toStateGuid
          }
        }
      },

    }
  }
`;


const GET_FIELDS = gql`
    query ($formGuid: String!) {
      allFields (formGuid: $formGuid) {
        guid,
        formGuid,
        name,
        dbName,
        position,
        optionsJson,
        valueType,
        fieldTypeTag,
        isTab,
        isRequired,
        isWholeRow,
        parent
      }
    }
`;

const CREATE_TAB = gql`
  mutation ($formGuid: String!, $name: String!) {
    createTab(formGuid: $formGuid, name: $name) {
      field {
        guid,
        name,
        dbName,
        position,
        valueType,
        fieldType {
          tag,
          icon,
          valueType
        },
        isTab,
        isRequired,
        isWholeRow,
        parent
      },
      ok    
    }
  }
`;


const CREATE_FIELD = gql`
  mutation ($formGuid: String!, $name: String!, $tag: String!, $positions: [PositionInput], $position: Int!, $parent: String! ) {
    createField(formGuid: $formGuid, name: $name, tag: $tag, positions: $positions, position: $position, parent: $parent) {
      field {
        guid,
        name,
        dbName,
        position,
        valueType,
        fieldType {
          tag,
          icon,
          valueType
        },
        isTab,
        isRequired,
        isWholeRow,
        parent
      },
      ok    
    }
  }
`;

const GET_FIELD_TYPES = gql`
    query {
      fieldTypes {
        edges {
          node {
            tag,
            name,
            parent,
            position,
            defaultName,
            defaultDbName,
            valueType,
            comparator,
            icon,
            isGroup,
            isInlineEditable,
            isBackendAvailable,
            isUpdatedAlways,
            isAlwaysWholeRow
          }
        }
      }
    }
`;

const mutations = {
  setFields(state, fields) {
    state.fields = fields;
  },
  setFieldTypes(state, fieldTypes) {
    state.fieldTypes = fieldTypes.edges.map(edge => edge.node);
  },
  setFormData(state, data) {
    if (data) {
      state.guid = data.guid;
      state.name = data.name;
      state.dbName = data.dbName;
      state.parent = data.parent;
      state.icon = data.icon;
      state.fields = data.fields ? data.fields.edges.map(edge => edge.node) : null;
      state.grids = data.grids ? data.grids.edges.map(edge => edge.node) : null;
      state.roles = data.roles ? data.roles.edges.map(edge => edge.node) : null;
      state.states = data.states ? data.states.edges.map(edge => edge.node) : null;
      state.actions = data.actions ? data.actions.edges.map(edge => edge.node) : null;
    }
  },
  addField(state, field) {
    state.fields.push(field);
  },
  setFieldsLoadedGuid(state, guid) {
    state.fieldsLoadedGuid = guid;
  }
};

const getters = {
  typesTreeData(state) {
    const typesTreeData = [];

    for (let i = 0; i < state.fieldTypes.length; i += 1) {
      const fieldType = state.fieldTypes[i];
      const locale = `types.${fieldType.tag}`;
      const name = i18n.tc(locale);
      const parent = fieldType.parent || '#';

      if (fieldType.isGroup) {
        const node = {
          id: fieldType.tag,
          parent,
          text: `<i class="fas fa-${fieldType.icon}"></i> ${name}`,
          type: 'group',
          data: {
            position: fieldType.position
          }
        };
        typesTreeData.push(node);
      } else {
        const node = {
          id: fieldType.tag,
          parent,
          text: `<i class="fas fa-${fieldType.icon}"></i> ${name}`,
          type: 'default',
          data: {
            position: fieldType.position
          }
        };
        typesTreeData.push(node);
      }
    }
    return typesTreeData;
  },
  fieldTreeData(state) {
    const treeData = [];

    for (let i = 0; i < state.fields.length; i += 1) {
      const field = state.fields[i];

      if (field.isTab) {
        const node = {
          id: field.guid,
          parent: '#',
          text: `<constructor-tab guid='${field.guid}' name='${field.name}'></constructor-tab>`,
          type: 'tab',
          data: { position: field.position }
        };
        treeData.push(node);
      } else {
        const node = {
          id: field.guid,
          parent: field.parent,
          text: `<constructor-field guid='${field.guid}' name='${field.name}' db_name='${field.dbName}' tag='${field.fieldType.tag}' icon='${field.fieldType.icon}'></constructor-field>`,
          data: { position: field.position },
          li_attr: { class: 'ax-field-node' }
        };
        treeData.push(node);
      }
    }
    return treeData;
  },
  avalibleFieldTreeData(state) {
    const treeData = [];

    for (let i = 0; i < state.fields.length; i += 1) {
      const field = state.fields[i];
      if (field.isTab) {
        const node = {
          id: field.guid,
          parent: '#',
          text: `<i class="far fa-bookmark"></i>&nbsp;<b id='${field.guid}'>${field.name}</b>`,
          type: 'tab',
          data: {
            guid: field.guid,
            position: field.position
          }
        };
        treeData.push(node);
      } else {
        const node = {
          id: field.guid,
          parent: field.parent,
          text: `<i class='fas fa-${field.fieldType.icon}'></i>&nbsp;<span id='${field.guid}' >${field.name}</span>`,
          data: {
            guid: field.guid,
            position: field.position
          },
          li_attr: { class: 'ax-field-name' }
        };
        treeData.push(node);
      }
    }
    return treeData;
  }
};

const actions = {

  getFormData(context, payload) {
    apolloClient.query({
      query: GET_FORM_DATA,
      variables: {
        dbName: payload.dbName
      }
    })
      .then(data => {
        context.commit('setFormData', data.data.form);
      })
      .catch(error => {
        logger.error(`Error in getFormData apollo client => ${error}`);
      });
  },

  getFields(context, payload) {
    apolloClient.query({
      query: GET_FIELDS,
      variables: {
        formGuid: payload.formGuid
      }
    })
      .then(data => {
        context.commit('setFields', data.data.allFields);
        context.commit('setFieldsLoadedGuid', payload.formGuid);
      })
      .catch(error => {
        logger.error(`Error in getFields apollo client => ${error}`);
      });
  },

  getFieldTypes(context) {
    apolloClient.query({
      query: GET_FIELD_TYPES
    })
      .then(data => {
        context.commit('setFieldTypes', data.data.fieldTypes);
      })
      .catch(error => {
        logger.error(`Error in getFieldTypes apollo client => ${error}`);
      });
  },

  createTab(context, payload) {
    apolloClient.mutate({
      mutation: CREATE_TAB,
      variables: {
        formGuid: payload.formGuid,
        name: payload.name
      }
    })
      .then(data => {
        const newField = data.data.createTab.field;
        context.commit('addField', newField);
      })
      .catch(error => {
        logger.error(`Error in createTab apollo client => ${error}`);
      });
  },

  createField(context, payload) {
    apolloClient.mutate({
      mutation: CREATE_FIELD,
      variables: {
        formGuid: context.state.guid,
        name: payload.name,
        tag: payload.tag,
        positions: payload.positions,
        position: payload.position,
        parent: payload.parent
      }
    })
      .then(data => {
        const newField = data.data.createField.field;
        context.commit('addField', newField);
      })
      .catch(error => {
        logger.error(`Error in createField apollo client => ${error}`);
      });
  }
};

const state = {
  guid: null,
  name: null,
  dbName: null,
  parent: null,
  icon: null,
  fields: [],
  grids: [],
  roles: [],
  states: [],
  actions: [],
  fieldTypes: []
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
