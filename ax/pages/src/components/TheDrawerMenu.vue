<template>
  <div @click='goHome()' class='drawer-wrapper'>
    <div class='logo-div'>
      <img class='logo' src='@/assets/small_axe.png' />
    </div>
    <tree :data='treeData' :options='treeOptions' @node:selected='onNodeSelected' ref='treeMenuRef'>
      <span class='tree-text' slot-scope='{ node }'>
        <template>
          <a :href='getUrl(node)' @click.prevent='linkClick()' class='tree-a'>{{ node.text }}</a>
        </template>
      </span>
    </tree>
    <div class='user-div content-center'>
      {{currentUserShortName}}
      &nbsp;
      <i class='user-avatar fas fa-user-circle'></i>
      <br />
      <a @click='doLogOut()' class='cursor-pointer'>{{$t("sign-out")}}</a>
      <br />
      <a
        @click='gotoAdmin()'
        class='cursor-pointer to-admin'
        v-if='currentUserIsAdmin'
      >{{$t("goto-admin")}}</a>
    </div>
    <br />
    <br />
    <modal adaptive height='auto' name='change-password' scrollable>
      <ax-change-password :guid='currentUserGuid' :is_new='true' @close='closePasswordModal' />
    </modal>
  </div>
</template>

<script>
// import CatalogItem from '@/components/CatalogItem.vue';
import store from '@/store';
import { getAxHostProtocol } from '@/misc';
import Cookies from 'js-cookie';

export default {
  name: 'TheDrawerMenu',
  components: {},
  data: () => ({
    guid: null,
    treeData: [],
    treeOptions: {
      parentSelect: true,
      checkOnSelect: false,
      store: {
        store,
        getter: () => store.getters.tree,
        dispatcher(tree) {
          store.commit('updateTreeStore', tree);
        }
      }
    }
  }),
  computed: {
    treeDataStore() {
      return this.$store.state.treeData;
    },
    currentUserShortName() {
      if (this.$store.state.currentUser) {
        return this.$store.state.currentUser.shortName;
      }
      return null;
    },
    currentUserGuid() {
      if (this.$store.state.currentUser) {
        return this.$store.state.currentUser.guid;
      }
      return null;
    },
    currentUserIsAdmin() {
      if (this.$store.state.currentUser) {
        return this.$store.state.currentUser.isActiveAdmin;
      }
      return null;
    },
    passwordMustChange() {
      return this.$store.state.passwordMustChange;
    }
  },
  watch: {
    treeDataStore(newValue) {
      if (newValue && newValue.length > 0) {
        this.treeData = newValue;
      }
    },
    passwordMustChange(newValue) {
      if (newValue) {
        this.openPasswordModal();
      }
    }
  },
  mounted() {
    this.$store.commit('setTokens', {
      access: Cookies.get('access_token'),
      refresh: Cookies.get('refresh_token')
    });
    setTimeout(() => {
      this.checkAuth(this.$store.state.accessToken);
      const currentGuid = this.$route.params.page;
      this.$store
        .dispatch('loadPageData', { guid: currentGuid })
        .then(response => {
          setTimeout(() => {
            const theNode = this.$refs.treeMenuRef.find({
              data: { guid: currentGuid }
            });
            if (theNode) {
              theNode[0].select(true);
              this.expandNodeAndParents(theNode[0]);
            }
          }, 400);
        });
    }, 150);
  },
  methods: {
    linkClick() {
      return false;
    },
    getUrl(node) {
      return node.data.guid;
    },
    expandNodeAndParents(node) {
      node.expand(true);
      if (node.parent) this.expandNodeAndParents(node.parent);
    },
    onNodeSelected(node) {
      this.$router.push({
        path: `/${node.data.guid}`
      });
    },
    goHome() {
      this.$router.push({
        path: `/${this.$store.state.indexPageGuid}`
      });
    },
    gotoAdmin() {
      const axUrl = getAxHostProtocol();
      window.location.href = `${axUrl}/admin/home`;
    },
    doLogOut() {
      this.$store.dispatch('logOut');
    },
    checkAuth(accessToken) {
      if (accessToken == null || accessToken === 'null') {
        console.log('Tokens not found -> signout');
        this.doLogOut();
      }
    },
    openPasswordModal() {
      this.$modal.show('change-password');
    },
    closePasswordModal() {
      this.$modal.hide('change-password');
    }
  }
};
</script>

<style scoped>
.logo {
  height: 50px;
  cursor: pointer;
}
.logo-div {
  margin-bottom: 15px;
  text-align: center;
}
.user-div {
  color: rgba(0, 0, 0, 0.87);
  margin: auto;
  padding-top: 40px;
  width: fit-content;
}
.user-div a {
  cursor: pointer;
  text-decoration: underline;
  color: rgba(0, 0, 0, 0.87);
}
.to-admin {
  cursor: pointer;
  color: #7cb342 !important;
}
.tree-a {
  color: rgba(0, 0, 0, 0.87);
  text-decoration: none;
}
</style>
