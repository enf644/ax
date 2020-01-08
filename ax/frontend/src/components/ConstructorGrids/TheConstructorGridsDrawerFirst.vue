<template>
  <div>
    <h3>{{$t("form.avalible-fields-header")}}:</h3>
    <div data-cy='grid-fields-tree' ref='tree'></div>
  </div>
</template>

<script>
import $ from 'jquery';
import 'jstree/dist/jstree.js';
import 'jstree/dist/themes/default/style.css';

export default {
  name: 'admin-grids-drawer-first',
  data: () => ({
    treeInitialized: false
  }),
  computed: {
    fields() {
      return this.$store.state.form.fields;
    }
  },
  watch: {
    fields() {
      if (this.treeInitialized) {
        const tree = $(this.$refs.tree).jstree(true);
        tree.settings.core.data = this.$store.getters[
          'form/avalibleFieldTreeData'
        ];
        tree.refresh();
        // setTimeout(() => {
        //   $(this.$refs.tree).jstree('open_all');
        // }, 100);
      } else {
        this.initFieldTree(this.$store.getters['form/avalibleFieldTreeData']);
      }
    }
  },
  mounted() {
    window.jQuery = $;
    window.$ = $;
    if (!this.treeInitialized) {
      this.initFieldTree(this.$store.getters['form/avalibleFieldTreeData']);
    }
  },
  methods: {
    openAllNodes() {
      setTimeout(() => {
        $(this.$refs.tree).jstree('open_all');
      }, 30);
    },
    initFieldTree(jsTreeData) {
      $(this.$refs.tree)
        .on('ready.jstree', () => this.openAllNodes())
        .on('model.jstree', () => this.openAllNodes())
        .jstree({
          core: {
            data: jsTreeData,
            check_callback() {
              return false;
            }
          },
          plugins: ['types', 'dnd', 'sort'],
          types: {
            default: {
              icon: false,
              valid_children: []
            },
            tab: {
              icon: false,
              valid_children: ['default'],
              li_attr: { class: 'jstree-field' }
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
          }
        });

      this.treeInitialized = true;
    }
  }
};
</script>

<style scoped>
</style>
