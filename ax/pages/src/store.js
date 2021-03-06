import Vue from 'vue';
import Vuex from 'vuex';
import gql from 'graphql-tag';
import apolloClient from '@/apollo';
// import i18n from '@/locale.js';
import store from '@/store';
import { getAxHostProtocol } from '@/misc';

Vue.use(Vuex);

const getDefaultState = () => ({
  pages: [],
  treeStore: [],
  indexPageGuid: null,
  currentPage: null,
  accessToken: null,
  refreshToken: null,
  drawerEnabled: true,
  toggleDrawer: false,
  currentUser: null,
  passwordMustChange: false
});

// const checkSelected = (guid, state) => {
//   if (guid === state.currentPage.guid) return true;
//   return false;
// };

const getChildren = (guid, state) => {
  let children = [];
  state.pages.forEach(page => {
    if (page.parent === guid) {
      const newNode = {
        text: page.name,
        data: {
          guid: page.guid,
          position: page.position
        },
        state: {
          // expanded: checkSelected(guid, state),
          // selected: checkSelected(guid, state)
        },
        children: getChildren(page.guid, state)
      };
      children.push(newNode);
    }
  });
  children = children.sort((a, b) => a.data.position - b.data.position);
  return children;
};


const mutations = {
  resetState(state) {
    Object.assign(state, getDefaultState());
  },
  setTokens(state, payload) {
    state.accessToken = payload.access;
    state.refreshToken = payload.refresh;
  },
  setCurrentPage(state, fullPage) {
    state.currentPage = fullPage;
  },
  setPages(state, pages) {
    state.pages = pages;
    pages.forEach(page => {
      if (page.parent === null) state.indexPageGuid = page.guid;
    });
  },
  updateTreeStore(state, newTree) {
    state.treeStore = newTree;
  },
  setToggleDrawer(state, visible) {
    state.toggleDrawer = visible;
  },
  setDrawerEnabled(state, enabled) {
    state.drawerEnabled = enabled;
  },
  setCurrentUser(state, user) {
    state.currentUser = user;
  },
  setPasswordMustChange(state, mustChange) {
    state.passwordMustChange = mustChange;
  }
};

const getters = {
  tree(state) {
    return state.treeStore;
  }
};

const actions = {
  logOut() {
    const host = getAxHostProtocol();
    // console.log('store -> logout');
    setTimeout(() => {
      window.location.href = `${host}/api/signout`;
    }, 3000);
  },
  loadAllPages(context, payload) {
    const ALL_PAGES = gql`
      query($updateTime: String, $guid: String) {
        allPages(updateTime: $updateTime) {
          guid
          name
          dbName
          parent
          position
        },
        pageData(updateTime: $updateTime, guid: $guid) {
          guid
          name
          dbName
          html
        },
        currentAxUser (updateTime: $updateTime) {
          guid
          email
          shortName
          passwordMustChange
          name
          isActiveAdmin
        },        
      }
    `;
    apolloClient
      .query({
        query: ALL_PAGES,
        variables: {
          guid: payload.guid,
          updateTime: Date.now()
        }
      })
      .then(data => {
        const pages = data.data.allPages;
        store.commit('setPages', pages);
        store.commit('setCurrentPage', data.data.pageData);
        store.commit('setCurrentUser', data.data.currentAxUser);
        store.commit('setPasswordMustChange', data.data.currentAxUser.passwordMustChange);

        const rootPage = pages.find(page => page.parent === null);
        const rootNode = {
          text: rootPage.name,
          data: { guid: rootPage.guid },
          state: {
            expanded: true
          },
          children: getChildren(rootPage.guid, context.state)
        };
        console.log([rootNode]);
        store.commit('updateTreeStore', [rootNode]);
      })
      .catch(error => {
        console.log(`Error in loadAllPages gql => ${error}`);
      });
  },
  loadPageData(context, payload) {
    const PAGE_DATA = gql`
      query($updateTime: String, $guid: String) {
        pageData(updateTime: $updateTime, guid: $guid) {
          guid
          name
          dbName
          html
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
        store.commit('setCurrentPage', fullPage);
      })
      .catch(error => {
        console.log(`Error in loadPageData gql => ${error}`);
      });
    return true;
  }
};

const state = getDefaultState();

export default new Vuex.Store({
  state,
  getters,
  mutations,
  actions
});
