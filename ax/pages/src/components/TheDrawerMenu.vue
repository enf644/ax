<template>
  <div @click='goHome()' class='drawer-wrapper'>
    <img class='logo' src='@/assets/small_axe.png' />
    <tree :data='treeData' :options='treeOptions' @node:selected='onNodeSelected'>
      <span class='tree-text' slot-scope='{ node }'>
        <template>
          <a href='#'>{{ node.text }}</a>
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

export default {
  name: 'TheDrawerMenu',
  components: {},
  data: () => ({
    guid: null,
    treeData: [],
    treeOptions: {
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
      access: window.$cookies.get('access_token'),
      refresh: window.$cookies.get('refresh_token')
    });
    setTimeout(() => {
      this.checkAuth(this.$store.state.accessToken);
      const currentGuid = this.$route.params.page;
      this.$store.dispatch('loadPageData', { guid: currentGuid });
    }, 50);
  },
  methods: {
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
  margin: auto;
  margin-bottom: 15px;
  height: 50px;
  margin-top: 10px;
  cursor: pointer;
}
.user-div {
  color: #999;
  margin: auto;
  padding-top: 40px;
  width: fit-content;
}
.user-div a {
  text-decoration: underline;
}
.to-admin {
  color: #7cb342;
}
</style>
