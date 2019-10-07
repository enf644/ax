<template>
  <div>
    <h3>{{$t("pages.drawer-header")}}:</h3>
    <div class='pages-tree' data-cy='pages-tree' ref='tree'></div>

    <modal :height='windowHeight' adaptive name='update-page' width='1000px'>
      <ThePageModal :guid='this.currentGuid' @close='closeModal' />
    </modal>
  </div>
</template>

<script>
import Vue from 'vue';
import $ from 'jquery';
import 'jstree/dist/jstree.js';
import 'jstree/dist/themes/default/style.css';
import TreePage from '@/components/PagesDesigner/TreePage.vue';
import ThePageModal from '@/components/PagesDesigner/ThePageModal.vue';

export default {
  name: 'ThePagesDesignerDrawerFirst',
  components: { TreePage, ThePageModal },
  data: () => ({
    windowHeight: null
  }),
  computed: {
    pages() {
      return this.$store.state.pages.pages;
    },
    modalMustOpen() {
      return this.$store.state.pages.modalMustOpen;
    },
    currentGuid() {
      if (this.$store.state.pages.currentPage) {
        return this.$store.state.pages.currentPage.guid;
      }
      return null;
    },
    indexPageGuid() {
      return this.$store.state.pages.indexPageGuid;
    }
  },
  watch: {
    pages() {
      const tree = $(this.$refs.tree).jstree(true);
      tree.settings.core.data = this.$store.getters['pages/jsTreeData'];
      tree.refresh();
    },
    modalMustOpen(newValue) {
      if (newValue) {
        this.$modal.show('update-page');
        this.$store.commit('pages/setModalMustOpen', false);
      }
    }
  },
  created() {
    Vue.customElement('tree-page', TreePage);
    this.windowHeight = window.innerHeight * 1 - 50;
  },
  mounted() {
    window.jQuery = $;
    window.$ = $;
    this.initJstree(this.$store.getters['pages/jsTreeData']);
    window.dialog = this.$dialog;
    this.$store.dispatch('pages/loadPageData', { guid: null });
  },
  methods: {
    changePosition() {
      console.log('chnage position');
    },
    initJstree(jsTreeData) {
      $(this.$refs.tree)
        .on('move_node.jstree', (e, data) => this.changePositions(e, data))
        .on('refresh.jstree', (e, data) => {
          let root_node = $(this.$refs.tree)
            .jstree(true)
            .get_node(this.indexPageGuid);
          $(this.$refs.tree).jstree('open_node', root_node, false, true);
        })
        .jstree({
          core: {
            data: jsTreeData,
            check_callback() {
              return true;
            }
          },
          plugins: ['types', 'dnd', 'sort'],
          types: {
            default: {
              icon: false,
              valid_children: ['default']
            },
            folder: {
              icon: false,
              valid_children: ['default', 'folder'],
              a_attr: { class: 'tree-folder' }
            }
          },
          sort(a, b) {
            return this.get_node(a).data.position >
              this.get_node(b).data.position
              ? 1
              : -1;
          }
        });
    },
    closeModal() {
      this.$modal.hide('update-page');
    }
  }
};
</script>

<style scoped>
.pages-tree ul {
  padding-left: 0px !important;
}
</style>