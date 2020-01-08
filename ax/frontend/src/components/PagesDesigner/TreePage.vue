<template>
  <span class='wrap'>
    <span @click='loadPageData()' class='name-p'>{{name}}</span>
    <v-btn class='small-ico' data-cy='page-options-btn' icon v-if='isCurrentPage'>
      <i @click='openPageSettings()' class='small-ico-i fas fa-cog'></i>
    </v-btn>
    <v-btn class='small-ico' data-cy='create-page-btn' icon v-if='isCurrentPage'>
      <i @click='createPagePrompt()' class='small-ico-i fas fa-plus'></i>
    </v-btn>
  </span>
</template>

<script>
import ThePageModal from '@/components/PagesDesigner/ThePageModal.vue';
import i18n from '@/locale.js';
import store from '@/store';
import gql from 'graphql-tag';
import apolloClient from '@/apollo';

export default {
  name: 'TreePage',
  components: { ThePageModal },
  props: {
    guid: null,
    name: null,
    db_name: null
  },
  data: () => ({}),
  computed: {
    isCurrentPage() {
      if (
        store.state.pages.currentPage &&
        store.state.pages.currentPage.guid === this.guid
      )
        return true;
      return false;
    }
  },
  watch: {},
  created() {
    this.currentName = this.name;
    this.currentDbName = this.db_name;
    this.okDbName = this.db_name;
  },
  mounted() {},
  methods: {
    locale(key) {
      return i18n.t(key);
    },
    openPageSettings() {
      store.commit('pages/setModalMustOpen', true);
    },
    async createPagePrompt() {
      const res = await this.$dialog.prompt({
        text: this.locale('pages.create-page-prompt'),
        actions: {
          true: {
            text: this.locale('common.confirm')
          }
        }
      });
      if (res) this.createPage(res);
    },
    createPage(name) {
      const CREATE_PAGE = gql`
        mutation($name: String!, $parent: String!) {
          createPage(name: $name, parent: $parent) {
            page {
              guid
              name
              dbName
              parent
              position
            }
            ok
          }
        }
      `;

      apolloClient
        .mutate({
          mutation: CREATE_PAGE,
          variables: {
            name,
            parent: this.guid
          }
        })
        .then(data => {
          const msg = this.locale('pages.page-created-toast');
          window.dialog.message.success(
            `<i class="fas fa-plus"></i> &nbsp ${msg}`
          );
          const newPage = data.data.createPage.page;
          store.commit('pages/addPage', newPage);
        })
        .catch(error => {
          console.log(`Error in createPage gql => ${error}`);
          window.dialog.message.error(`${error}`);
        });
    },
    loadPageData() {
      store.dispatch('pages/loadPageData', { guid: this.guid });
    }
  }
};
</script>

<style scoped>
.wrap {
  white-space: nowrap;
}
.small-ico {
  width: 16px;
  height: 16px;
  margin-left: 10px;
}
.small-ico-i {
  color: #999;
}
.name-p {
  cursor: pointer;
}
</style>
