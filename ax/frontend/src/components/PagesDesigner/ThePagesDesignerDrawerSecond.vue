<template>
  <div class='monaco-wrapper'>
    <monaco-editor
      :options='monacoOptions'
      @editorDidMount='initMonaco'
      automaticLayout='true'
      class='editor'
      cy-data='code-editor'
      language='html'
      ref='editor'
      theme='vs-dark'
      v-model='currentCode'
    ></monaco-editor>
    <resize-observer @notify='handleResize' />
  </div>
</template>

<script>
import apolloClient from '@/apollo';
import gql from 'graphql-tag';
import MonacoEditor from 'vue-monaco';
import * as monaco from 'monaco-editor';

export default {
  name: 'ThePagesDesignerDrawerSecond',
  components: { MonacoEditor },
  data: () => ({
    currentCode: '',
    pageGuid: null,
    monacoOptions: null
  }),
  computed: {
    code() {
      if (this.$store.state.pages.currentPage) {
        if (this.$store.state.pages.currentPage.code) {
          return this.$store.state.pages.currentPage.code;
        }
        return '';
      }
      return 'loading...';
    }
  },
  watch: {
    code(newValue) {
      if (newValue != this.currentCode) this.currentCode = newValue;
    }
  },
  mounted() {},
  methods: {
    initMonaco(editor) {
      editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KEY_S, () => {
        this.updatePage();
      });
    },
    handleResize() {
      const editor = this.$refs.editor.getEditor();
      editor.layout();
    },
    updatePage() {
      const UPDATE_PAGE = gql`
        mutation($guid: String!, $code: String) {
          updatePage(guid: $guid, code: $code) {
            page {
              guid
              name
              dbName
              code
              parent
            }
            ok
          }
        }
      `;

      apolloClient
        .mutate({
          mutation: UPDATE_PAGE,
          variables: {
            guid: this.$store.state.pages.currentPage.guid,
            code: this.currentCode
          }
        })
        .then(data => {
          const page = data.data.updatePage.page;
          this.$store.commit('pages/setCurrentPage', page);

          const msg = this.$t('pages.page-updated-toast');
          this.$dialog.message.success(
            `<i class="fas fa-pencil-alt"></i> &nbsp ${msg}`
          );
        })
        .catch(error => {
          this.$log.error(`Error in updatePage gql => ${error}`);
          this.$dialog.message.error(`${error}`);
        });
    }
  }
};
</script>

<style scoped>
.monaco-wrapper {
  width: 100%;
  height: 100%;
  resize: both;
}
.editor {
  width: 100%;
  height: 100%;
  resize: both;
  overflow: auto;
}
</style>
