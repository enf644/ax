<template>
  <div>
    <h3>{{$t("form.columns-header")}}:</h3>
    <div data-cy='fields-tree' ref='tree'></div>
  </div>
</template>

<script>
import $ from 'jquery';
import 'jstree/dist/jstree.js';
import 'jstree/dist/themes/default/style.css';

export default {
  name: 'admin-grids-drawer-second',
  data: () => ({
    treeInitialized: false
  }),
  computed: {
    fields() {
      return this.$store.state.grids.columns;
    }
  },
  watch: {
    fields(newValue, oldValue) {
      if (this.treeInitialized) {
        const tree = $(this.$refs.tree).jstree(true);
        tree.settings.core.data = this.$store.getters['form/fieldTreeData'];
        tree.refresh();
      } else {
        this.initFieldTree(this.$store.getters['form/fieldTreeData']);
      }
    }
  },
  mounted() {
    window.jQuery = $;
    window.$ = $;

    if (!this.treeInitialized) {
      this.initFieldTree(this.$store.getters['form/fieldTreeData']);
    }
  },
  methods: {
    initFieldTree(jsTreeData) {}
  }
};
</script>

<style scoped>
</style>
