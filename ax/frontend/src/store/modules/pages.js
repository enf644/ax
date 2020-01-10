import gql from 'graphql-tag';
import apolloClient from '@/apollo';
import i18n from '@/locale.js';
import store from '@/store';

const getDefaultState = () => {
  return {
    pages: [],
    indexPageGuid: null,
    currentPage: null,
    modalMustOpen: false
  }
}

const mutations = {
  resetState(state) {
    Object.assign(state, getDefaultState())
  },
  setPages(state, pages) {
    state.pages = pages;

    pages.forEach(page => {
      if (page.parent === null) state.indexPageGuid = page.guid
    });
  },
  addPage(state, page) {
    state.pages.push(page)
  },
  setCurrentPage(state, fullPage) {
    state.currentPage = fullPage;
  },
  updatePageInList(state, updatedPage) {
    let page = Object.assign({}, updatedPage);
    page.code = null;

    state.pages = [
      ...state.pages.filter(element => element.guid !== page.guid),
      page
    ];
  },
  deletePageFromList(state, guid) {
    state.pages = [...state.pages.filter(element => element.guid !== guid)];
  },
  setModalMustOpen(state, newVal) {
    state.modalMustOpen = newVal;
  }
};

const getters = {
  jsTreeData(state) {
    const jsTreeData = [];

    for (let i = 0; i < state.pages.length; i += 1) {
      state.pages.forEach(page => {
        const parent = page.parent || '#';
        const node = {
          id: page.guid,
          parent,
          text: `<tree-page name="${page.name}" db_name="${page.dbName}" guid="${page.guid}" />`,
          type: 'default',
          data: {
            position: page.position,
            dbName: page.dbName
          }
        };
        jsTreeData.push(node);
      });
      return jsTreeData;
    }
  }
};

const actions = {
  loadPageData(context, payload) {
    const PAGE_DATA = gql`
      query($updateTime: String, $guid: String) {
        pageData(updateTime: $updateTime, guid: $guid) {
          guid
          name
          dbName
          code
          html
          parent
        }
      }
    `;

    apolloClient
      .query({
        query: PAGE_DATA,
        variables: {
          guid: payload.guid,
          updateTime: Date.now()
        }
      })
      .then(data => {
        const fullPage = data.data.pageData;
        store.commit('pages/setCurrentPage', fullPage);
      })
      .catch(error => {
        const msg = `Error in loadPageData gql => ${error}`;
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
