<template>
  <div>
    <h3>{{$t("form.columns-header")}}:</h3>
    <div data-cy='fields-tree' ref='tree'></div>

    <br>
    <v-divider></v-divider>
    <br>

    <v-badge class='drawer-toggle' color='blue-grey' overlap>
      <template v-slot:badge>
        <span class='drawer-toggle-errors'>{{serverFilterRulesCount}}</span>
      </template>
      <v-btn @click='openServerFilterModal' small>
        <i class='fas fa-filter'></i>
        &nbsp;
        {{$t("grids.serer-filter-btn")}}
      </v-btn>
    </v-badge>

    <modal adaptive height='auto' name='server-filter' scrollable width='1000px'>
      <TheServerFilter @close='closeServerFilterModal'/>
    </modal>

    <br>
    <br>

    <v-switch
      :label='this.$t("grids.options-quick-search")'
      @change='saveOptions'
      class='options-switcher'
      cy-data='options-quick-search'
      v-model='changedOptions.enableQuickSearch'
    ></v-switch>

    <v-switch
      :label='this.$t("grids.options-flat-mode")'
      @change='saveOptions'
      class='options-switcher'
      cy-data='options-flat-mode'
      v-model='changedOptions.enableFlatMode'
    ></v-switch>

    <v-switch
      :label='this.$t("grids.options-columns-resize")'
      @change='saveOptions'
      class='options-switcher'
      cy-data='options-columns-resize'
      v-model='changedOptions.enableColumnsResize'
    ></v-switch>

    <v-switch
      :label='this.$t("grids.options-filtering")'
      @change='saveOptions'
      class='options-switcher'
      cy-data='options-filtering'
      v-model='changedOptions.enableFiltering'
    ></v-switch>

    <v-switch
      :label='this.$t("grids.options-soring")'
      @change='saveOptions'
      class='options-switcher'
      cy-data='options-soring'
      v-model='changedOptions.enableSorting'
    ></v-switch>

    <v-switch
      :label='this.$t("grids.options-open-form")'
      @change='saveOptions'
      class='options-switcher'
      cy-data='options-open-form'
      v-model='changedOptions.enableOpenForm'
    ></v-switch>

    <v-switch
      :label='this.$t("grids.options-actions")'
      @change='saveOptions'
      class='options-switcher'
      cy-data='options-actions'
      v-model='changedOptions.enableActions'
    ></v-switch>

    <v-subheader class='pl-0'>{{$t("grids.options-row-height")}}</v-subheader>
    <v-slider
      @change='saveOptions'
      class='options-switcher'
      max='250'
      min='35'
      thumb-label
      v-model='changedOptions.rowHeight'
    ></v-slider>

    <v-subheader class='pl-0'>{{$t("grids.options-pinned")}}</v-subheader>
    <v-slider
      @change='saveOptions'
      class='options-switcher'
      max='10'
      thumb-label
      v-model='changedOptions.pinned'
    ></v-slider>
  </div>
</template>

<script>
import $ from 'jquery';
import 'jstree/dist/jstree.js';
import 'jstree/dist/themes/default/style.css';
import TheServerFilter from '@/components/ConstructorGrids/TheServerFilter.vue';

export default {
  name: 'admin-grids-drawer-second',
  data: () => ({
    treeInitialized: false,
    changedOptions: {},
    optionsLoaded: false
  }),
  components: {
    TheServerFilter
  },
  computed: {
    columns() {
      return this.$store.state.grids.columns;
    },
    updated() {
      return this.$store.state.grids.updateTime;
    },
    options() {
      return this.$store.state.grids.options;
    },
    serverFilterRulesCount() {
      return this.$store.getters['grids/serverFilterRulesCount'];
    },
    updateTime() {
      return this.$store.state.grids.updateTime;
    }
  },
  watch: {
    columns() {
      if (this.treeInitialized) {
        const tree = $(this.$refs.tree).jstree(true);
        tree.settings.core.data = this.$store.getters['grids/columnTreeData'];
        tree.refresh(true, false);
        // setTimeout(() => {
        //   $(this.$refs.tree).jstree('open_all');
        // }, 100);
      } else {
        this.initColumnTree(this.$store.getters['grids/columnTreeData']);
      }
    },
    updateTime() {
      if (this.updateTime && this.$store.state.grids.loadingDone) {
        this.changedOptions = Object.assign({}, this.options);
        this.optionsLoaded = true;
      }
    }
  },
  mounted() {
    window.jQuery = $;
    window.$ = $;

    if (!this.treeInitialized) {
      this.initColumnTree(this.$store.getters['grids/columnTreeData']);
    }

    // this.options = this.$store.state.grids.options;
  },
  methods: {
    openServerFilterModal() {
      this.$modal.show('server-filter');
    },
    closeServerFilterModal() {
      this.$modal.hide('server-filter');
    },
    saveOptions() {
      if (this.$store.state.grids.loadingDone) {
        this.$store.commit('grids/combineOptions', this.changedOptions);
        this.$store.dispatch('grids/updateGrid', {}).then(() => {
          const msg = this.$t('grids.grid-updated');
          this.$store.commit('grids/setUpdateTime', Date.now());
          this.$dialog.message.success(
            `<i class="fas fa-columns"></i> &nbsp ${msg}`
          );
        });
      }
    },
    createColumn(e, data) {
      this.$nextTick(() => {
        const mustBePosition = data.position;
        $(this.$refs.tree)
          .jstree()
          .delete_node(data.node);

        const positionList = this.getPositionList(mustBePosition);

        // console.log(positionList);
        // console.log(mustBePosition);

        this.$store
          .dispatch('grids/createColumn', {
            fieldGuid: data.original.id,
            columnType: data.parent,
            positions: positionList,
            position: mustBePosition
          })
          .then(() => {
            this.openGroup(data.parent);
            const msg = this.$t('grids.add-column-toast');
            this.$dialog.message.success(
              `<i class="fas fa-columns"></i> &nbsp ${msg}`
            );
          });
      });
    },
    changeColumnPositions(e, data) {
      const positions = this.getPositionList();
      this.$store
        .dispatch('grids/changeColumnsPositions', { positions })
        .then(() => {
          this.openGroup(data.parent);
          const msg = this.$t('grids.change-positions-toast');
          this.$dialog.message.success(
            `<i class="fas fa-sort"></i> &nbsp ${msg}`
          );
        });
    },
    deleteColumn(guid) {
      this.$store.dispatch('grids/deleteColumn', { guid }).then(() => {
        const msg = this.$t('grids.column-deleted-toast');
        this.$dialog.message.success(
          `<i class="fas fa-trash-alt"></i> &nbsp ${msg}`
        );
      });
    },
    openGroup(guid) {
      const guidId = `#${guid}`;
      setTimeout(() => {
        $(this.$refs.tree).jstree('open_node', $(guidId), false, true);
      }, 300);
    },
    openAllNodes() {
      setTimeout(() => {
        $(this.$refs.tree).jstree('open_all');
      }, 30);
    },
    initColumnTree(jsTreeData) {
      $(this.$refs.tree)
        .on('move_node.jstree', (e, data) => this.changeColumnPositions(e, data))
        .on('copy_node.jstree', (e, data) => this.createColumn(e, data))
        .on('ready.jstree', () => this.openAllNodes())
        .on('refresh.jstree', () => this.openAllNodes())
        .jstree({
          core: {
            data: jsTreeData,
            check_callback(operation, node, nodeParent, nodePosition, more) {
              if (operation === 'move_node') {
                if (nodeParent.parent == null) {
                  return false;
                }
              }

              if (operation === 'copy_node') {
                if (nodeParent.parent == null) {
                  return false;
                }

                if (more.ref != null) {
                  if (more.ref.parent === '#') return true;
                  if (more.core || more.pos === 'i') return false;
                  return true;
                }
              }
              return true;
            }
          },
          plugins: ['types', 'dnd', 'sort'],
          types: {
            default: {
              icon: false,
              valid_children: []
            },
            group: {
              icon: false,
              valid_children: ['default'],
              a_attr: { class: 'tree-group' }
            },
            agg: {
              icon: false,
              valid_children: [],
              a_attr: { class: 'tree-group' }
            }
          },
          sort(a, b) {
            if (this.get_node(a).data && this.get_node(b).data) {
              return this.get_node(a).data.position
                > this.get_node(b).data.position
                ? 1
                : -1;
            }
            return 1;
          }
        });

      $(this.$refs.tree).on('keydown.jstree', '.jstree-anchor', e => {
        if (e.which === 46) {
          const columnGuid = e.currentTarget.id.replace('_anchor', '');
          this.deleteColumn(columnGuid);
        }
      });

      this.treeInitialized = true;
    },
    getPositionList(mustBePosition) {
      const positionList = [];
      const tree = $(this.$refs.tree).jstree(true);
      const jsonNodes = tree.get_json('#', { flat: true });
      const realNodes = jsonNodes.filter(node => node.type === 'default');
      $.each(realNodes, (i, node) => {
        const parentNode = tree.get_node(node.parent);
        let newPosition = $.inArray(node.id, parentNode.children);
        if (mustBePosition != null && mustBePosition * 1 <= newPosition) {
          newPosition += 1;
        }
        const nodeInfo = {
          guid: node.id,
          position: newPosition,
          parent: node.parent
        };
        positionList.push(nodeInfo);
      });
      return positionList;
    }
  }
};
</script>

<style scoped>
.options-switcher {
  margin: 0px;
  height: 30px;
}
.options-switcher .v-label {
  font-size: 14px !important;
}
</style>
