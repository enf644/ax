import apolloClient from '../../apollo';
import gql from 'graphql-tag';
import logger from '../../logger';
import i18n from '../../locale.js';


const FieldFragment = gql`
  fragment FieldFragment on Field {
    guid,
    name,
    dbName,
    position,
    fieldType {
      tag,
      icon,
      valueType,
    isInlineEditable,
      isBackendAvailable,
      isUpdatedAlways,
      isAlwaysWholeRow,
      isVirtual,
      isReadonly
    },
    isTab,
    isRequired,
    isWholeRow,
    optionsJson,
    privateOptionsJson,
    parent
  }
`;


const GET_FORM_DATA = gql`
  query ($dbName: String!, $updateTime: String) {
    axForm (dbName: $dbName, updateTime: $updateTime) {
      guid,
      name,
      dbName,
      parent,
      icon,
      fields {
        edges {
          node {    
            ...FieldFragment
          }
        }
      }, 
      grids {
        edges {
          node {
            guid,
            name,
            dbName,
            position,
            isDefaultView
          }
        }
      },
      roles {
        edges {
          node {
            guid,  
            name,
            icon,
            isAdmin
          }
        }
      },          
      states {
        edges {
          node {
            guid,
            name,
            roles{
              edges {
                node {
                  guid,
                  name
                }
              }
            },
            isStart,
            isDeleted,
            isAll,
            x,
            y          
          }
        }
      },
      actions {
        edges {
          node {
            guid,
            name,
            dbName,
            roles{
              edges {
                node {
                  guid,
                  name
                }
              }
            },
            fromStateGuid,
            toStateGuid,
            icon,
            radius
          }
        }
      },
      permissions {
        edges {
          node {
            guid,
            roleGuid,
            fieldGuid,
            stateGuid,
            edit,
            read
          }
        }
      }
    }
  }
  ${FieldFragment}
`;


const CREATE_TAB = gql`
  mutation ($formGuid: String!, $name: String!) {
    createTab(formGuid: $formGuid, name: $name) {
      field {
        ...FieldFragment
      },
      ok    
    }
  }
  ${FieldFragment}
`;


const UPDATE_TAB = gql`
  mutation ($guid: String!, $name: String!) {
    updateTab(guid: $guid, name: $name) {
      field {
        ...FieldFragment
      },
      ok    
    }
  }
  ${FieldFragment}
`;

const DELETE_TAB = gql`
  mutation ($guid: String!) {
    deleteTab(guid: $guid) {
      deleted,
      ok    
    }
  }
`;

const CREATE_FIELD = gql`
  mutation ($formGuid: String!, $name: String!, $tag: String!, $positions: [PositionInput], $position: Int!, $parent: String! ) {
    createField(formGuid: $formGuid, name: $name, tag: $tag, positions: $positions, position: $position, parent: $parent) {
      field {
        ...FieldFragment
      },
      permissions {
        guid,
        formGuid,
        roleGuid,
        stateGuid,
        fieldGuid,
        read,
        edit        
      },
      ok    
    }
  }
  ${FieldFragment}
`;

const UPDATE_FIELD = gql`
  mutation ($guid: String!, $name: String, $dbName: String, $isRequired: Boolean, $isWholeRow: Boolean, $optionsJson: JSONString, $privateOptionsJson: JSONString ) {
    updateField(guid: $guid, name: $name, dbName: $dbName, isRequired: $isRequired, isWholeRow: $isWholeRow, optionsJson: $optionsJson, privateOptionsJson: $privateOptionsJson) {
      field {
        ...FieldFragment
      },
      ok    
    }
  }
  ${FieldFragment}
`;


const DELETE_FIELD = gql`
  mutation ($guid: String!) {
    deleteField(guid: $guid) {
      deleted,
      ok    
    }
  }
`;


const CHANGE_FIELDS_POSITIONS = gql`
  mutation ($formGuid: String!, $positions: [PositionInput]) {
      changeFieldsPositions(formGuid: $formGuid, positions: $positions) {
        fields {
          ...FieldFragment
        }
      }
  }
  ${FieldFragment}
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
    } else {
      state.guid = null;
      state.name = null;
      state.dbName = null;
      state.parent = null;
      state.icon = null;
      state.fields = [];
      state.grids = [];
    }
  },
  addField(state, field) {
    state.fields.push(field);
  },
  updateField(state, newField) {
    state.fields = [
      ...state.fields.filter(element => element.guid !== newField.guid),
      newField
    ];
  },
  deleteField(state, deleted) {
    state.fields = [...state.fields.filter(element => element.guid !== deleted)];
  },
  setFieldsLoadedGuid(state, guid) {
    state.fieldsLoadedGuid = guid;
  },
  setIsNameChangeOperation(state, flag) {
    state.isNameChangeOperation = flag;
  },
  setOpenSettingsFlag(state, guid) {
    state.openSettingsFlag = guid;
  },
  setCreatedFieldGuid(state, guid) {
    state.createdFieldGuid = guid;
  },
  setGrids(state, grids) {
    state.grids = grids;
  },
  addGrid(state, grid) {
    state.grids.push(grid);
  },
  updateGrid(state, grid) {
    const resultGrids = [
      ...state.grids.filter(element => element.guid !== grid.guid),
      grid
    ];

    if (grid.isDefaultView) {
      for (let i = 0; i < resultGrids.length; i += 1) {
        if (resultGrids[i].guid !== grid.guid) {
          resultGrids[i].isDefaultView = false;
        }
      }
    }
    state.grids = resultGrids;
  },
  deleteGrid(state, deleted) {
    state.grids = [...state.grids.filter(element => element.guid !== deleted)];
  },
  setUpdateTime(state, updateTime) {
    state.updateTime = updateTime;
  }
};

const getters = {
  fieldsTabSorted(state) {
    const retFields = [];
    retFields.push({
      guid: null,
      name: 'All fields',
      isTab: true
    });
    const tabs = state.fields.filter(field => field.isTab).sort(field => field.position);
    tabs.forEach(tab => {
      retFields.push(tab);
      const fields = state.fields
        .filter(field => field.parent === tab.guid)
        .sort(field => field.position);
      fields.forEach(tabField => {
        retFields.push(tabField);
      });
    });
    return retFields;
  },
  typesTreeData(state) {
    const typesTreeData = [];

    for (let i = 0; i < state.fieldTypes.length; i += 1) {
      const fieldType = state.fieldTypes[i];
      const parent = fieldType.parent || '#';

      if (fieldType.isGroup) {
        const locale = `types.${fieldType.tag}`;
        const name = i18n.tc(locale);
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
        const locale = `types.${fieldType.tag}.name`;
        const name = i18n.tc(locale);
        const node = {
          id: fieldType.tag,
          parent,
          text: `<i class="fas fa-${fieldType.icon}"></i> ${name}`,
          type: 'default',
          data: {
            position: fieldType.position,
            icon: fieldType.icon
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
          text: `<constructor-field guid='${field.guid}' name='${field.name}' db_name='${field.dbName}' tag='${field.fieldType.tag}' icon='${field.fieldType.icon}' options_json='${field.optionsJson}'></constructor-field>`,
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
        dbName: payload.dbName,
        updateTime: Date.now()
      }
    })
      .then(data => {
        if (data.data.axForm) {
          context.commit('setFormData', data.data.axForm);
          context.commit('workflow/setWorkflowData', data.data.axForm, { root: true });
        } else {
          logger.error(`Cant find form => ${payload.dbName}`);
          const url = '/admin/home';
          context.commit('home/setRedirectNeededUrl', url, { root: true });
        }
      })
      .catch(error => {
        logger.error(`Error in getFormData apollo client => ${error}`);
      });
  },

  // getFields(context, payload) {
  //   apolloClient.query({
  //     query: GET_FIELDS,
  //     variables: {
  //       formGuid: payload.formGuid
  //     }
  //   })
  //     .then(data => {
  //       context.commit('setFields', data.data.allFields);
  //       context.commit('setFieldsLoadedGuid', payload.formGuid);
  //     })
  //     .catch(error => {
  //       logger.error(`Error in getFields apollo client => ${error}`);
  //     });
  // },

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
        context.commit('setCreatedFieldGuid', newField.guid);
      })
      .catch(error => {
        logger.error(`Error in createTab apollo client => ${error}`);
      });
  },

  updateTab(context, payload) {
    apolloClient.mutate({
      mutation: UPDATE_TAB,
      variables: {
        guid: payload.guid,
        name: payload.name
      }
    })
      .then(data => {
        const newField = data.data.updateTab.field;
        context.commit('updateField', newField);
      })
      .catch(error => {
        logger.error(`Error in updateTab apollo client => ${error}`);
      });
  },


  deleteTab(context, payload) {
    apolloClient.mutate({
      mutation: DELETE_TAB,
      variables: {
        guid: payload.guid
      }
    })
      .then(data => {
        const deletedGuid = data.data.deleteTab.deleted;
        context.commit('deleteField', deletedGuid);
      })
      .catch(error => {
        logger.error(`Error in deleteTab apollo client => ${error}`);
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
        context.commit('setCreatedFieldGuid', newField.guid);

        const newPermissions = data.data.createField.permissions;
        context.commit('workflow/setFieldPermissions', newPermissions, { root: true });
      })
      .catch(error => {
        logger.error(`Error in createField apollo client => ${error}`);
      });
  },


  updateField(context, payload) {
    let { privateOptionsJson } = payload;
    if (privateOptionsJson == null || privateOptionsJson === 'null') privateOptionsJson = '{}';

    apolloClient.mutate({
      mutation: UPDATE_FIELD,
      variables: {
        guid: payload.guid,
        name: payload.name,
        dbName: payload.dbName,
        isRequired: payload.isRequired,
        isWholeRow: payload.isWholeRow,
        optionsJson: payload.optionsJson,
        privateOptionsJson
      }
    })
      .then(data => {
        const newField = data.data.updateField.field;
        context.commit('updateField', newField);
      })
      .catch(error => {
        logger.error(`Error in updateField apollo client => ${error}`);
      });
  },


  deleteField(context, payload) {
    apolloClient.mutate({
      mutation: DELETE_FIELD,
      variables: {
        guid: payload.guid
      }
    })
      .then(data => {
        const deletedGuid = data.data.deleteField.deleted;
        context.commit('deleteField', deletedGuid);
        context.commit('grids/deleteField', deletedGuid, { root: true });
      })
      .catch(error => {
        logger.error(`Error in deleteField apollo client => ${error}`);
      });
  },

  changeFieldsPositions(context, payload) {
    apolloClient.mutate({
      mutation: CHANGE_FIELDS_POSITIONS,
      variables: {
        formGuid: context.state.guid,
        positions: payload.positions
      }
    })
      .then(data => {
        context.commit('setFields', data.data.changeFieldsPositions.fields);
      })
      .catch(error => {
        logger.error(`Error in changeFieldsPositions apollo client => ${error}`);
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
  fieldTypes: [],
  isNameChangeOperation: false,
  openSettingsFlag: null,
  createdFieldGuid: null,
  updateTime: null
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
