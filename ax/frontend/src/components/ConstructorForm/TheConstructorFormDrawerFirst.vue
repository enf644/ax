<template>
  <div>
    <h3>{{$t("form.types-header")}}:</h3>
    <div data-cy='types-tree' ref='tree'></div>
  </div>
</template>

<script>
import $ from 'jquery';
import 'jstree/dist/jstree.js';
import 'jstree/dist/themes/default/style.css';

export default {
  components: {},
  data: () => ({
    dialog: false,
    treeInitialized: false
  }),
  computed: {
    fieldTypes() {
      return this.$store.state.form.fieldTypes;
    }
  },
  watch: {
    fieldTypes() {
      if (this.treeInitialized) {
        const tree = $(this.$refs.tree).jstree(true);
        tree.settings.core.data = this.$store.getters['form/typesTreeData'];
        tree.refresh();
      } else {
        this.initTypesTree(this.$store.getters['form/typesTreeData']);
      }
    }
  },
  mounted() {
    window.jQuery = $;
    window.$ = $;
    if (!this.treeInitialized) {
      const data = this.$store.getters['form/typesTreeData'];
      this.initTypesTree(data);
    }
  },
  methods: {
    initTypesTree(jsTreeData) {
      $(this.$refs.tree)
        .on('ready.jstree', () => this.openFirstNode())
        .on('refresh.jstree', () => this.openFirstNode())
        .jstree({
          core: {
            data: jsTreeData,
            // eslint-disable-next-line camelcase, no-unused-vars
            check_callback(operation, node, node_parent, node_position, more) {
              return false;
            }
          },
          plugins: ['types', 'dnd', 'sort'],
          types: {
            default: {
              icon: false,
              valid_children: ['default']
            },
            group: {
              icon: false,
              draggable: false
            }
          },
          sort(a, b) {
            const positionA = this.get_node(a).data
              ? this.get_node(a).data.position
              : null;
            const positionB = this.get_node(b).data
              ? this.get_node(b).data.position
              : null;
            return positionA > positionB ? 1 : -1;
          },
          dnd: {
            always_copy: true
          }
        });
      this.treeInitialized = true;
    },
    openFirstNode() {
      setTimeout(() => {
        $(this.$refs.tree).jstree('select_node', 'ul > li:first');
        const selectNode = $(this.$refs.tree).jstree('get_selected');
        $(this.$refs.tree).jstree('open_node', selectNode, false, true);
      }, 30);
    }
  }
};
</script>

<style scoped>
</style>
