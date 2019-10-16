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
import gql from 'graphql-tag';
import apolloClient from '@/apollo';

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
            check_callback(operation, node, nodeParent, nodePosition, more) {
              if (operation === 'move_node') {
                if (more.ref && more.ref.parent === '#') return false;
                return true;
              }
              return false;
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
    changePositions(e, data) {
      const positionData = this.getPositionList();
      const CHANGE_PAGES_POSITIONS = gql`
        mutation($positions: [PositionInput]) {
          changePagesPositions(positions: $positions) {
            pages {
              guid
              name
              dbName
              parent
              position
            }
          }
        }
      `;

      apolloClient
        .mutate({
          mutation: CHANGE_PAGES_POSITIONS,
          variables: {
            positions: positionData
          }
        })
        .then(data => {
          this.$store.commit(
            'pages/setPages',
            data.data.changePagesPositions.pages,
            { root: true }
          );
        })
        .catch(error => {
          console.log(`Error in changePositions apollo client => ${error}`);
        });
    },
    getPositionList() {
      const positionList = [];
      const tree = $(this.$refs.tree).jstree(true);
      const jsonNodes = tree.get_json('#', { flat: true });
      $.each(jsonNodes, (i, node) => {
        const parentNode = tree.get_node(node.parent);
        const newPosition = $.inArray(node.id, parentNode.children);
        const nodeInfo = {
          guid: node.id,
          position: newPosition,
          parent: node.parent
        };
        positionList.push(nodeInfo);

        const nodeObject = tree.get_node(node.id);
        nodeObject.data.position = newPosition;
      });
      return positionList;
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