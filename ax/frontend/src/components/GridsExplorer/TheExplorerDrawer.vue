<template>
  <div>
    <h3>{{$t("home.ax-forms")}}:</h3>
    <div data-cy='forms-tree' ref='tree'></div>
  </div>
</template>

<script>
/* eslint-disable no-unused-vars */

import $ from 'jquery';
import 'jstree/dist/jstree.js';
import 'jstree/dist/themes/default/style.css';

export default {
  name: 'TheExplorerDrawer',
  components: {},
  data() {
    return {
      // currentFolderGuid: null
    };
  },
  computed: {
    forms() {
      return this.$store.state.home.forms;
    }
  },
  watch: {
    forms(newValue) {
      if (newValue) {
        this.initJstree(this.$store.getters['home/explorerTreeData']);
      }
    }
  },
  created() {},
  mounted() {
    window.jQuery = $;
    window.$ = $;
    setTimeout(() => {
      this.initJstree(this.$store.getters['home/explorerTreeData']);
    }, 100);
  },
  methods: {
    gotoGrid(e, data) {
      this.$router.push({
        path: `/admin/explorer/${data.node.data.form}/${data.node.data.grid}`
      });
    },
    initJstree(jsTreeData) {
      $(this.$refs.tree)
        .on('activate_node.jstree', (e, data) => this.gotoGrid(e, data))
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
    }
  }
};
</script>

<style scoped>
</style>
