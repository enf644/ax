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
    columns() {
      return this.$store.state.grids.columns;
    },
    updated() {
      return this.$store.state.grids.updateTime;
    }
  },
  watch: {
    columns() {
      if (this.treeInitialized) {
        const tree = $(this.$refs.tree).jstree(true);
        tree.settings.core.data = this.$store.getters['grids/columnTreeData'];
        tree.refresh(true, false);
      } else {
        this.initColumnTree(this.$store.getters['grids/columnTreeData']);
      }
    },
    updated(newValue, oldValue) {
      // if (!oldValue) {
      //   setTimeout(() => {
      //     $(this.$refs.tree).jstree('open_all');
      //   }, 100);
      // }
    }
  },
  mounted() {
    window.jQuery = $;
    window.$ = $;

    if (!this.treeInitialized) {
      this.initColumnTree(this.$store.getters['grids/columnTreeData']);
    }
  },
  methods: {
    createColumn(e, data) {
      const mustBePosition = data.position;
      $(this.$refs.tree)
        .jstree()
        .delete_node(data.node);
      const positionList = this.getPositionList(mustBePosition);

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
    initColumnTree(jsTreeData) {
      $(this.$refs.tree)
        .on('move_node.jstree', (e, data) => this.changeColumnPositions(e, data))
        .on('copy_node.jstree', (e, data) => this.createColumn(e, data))
        .on('ready.jstree', () => {
          setTimeout(() => {
            $(this.$refs.tree).jstree('open_all');
          }, 100);
        })
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
            // console.log(this.get_node(a).text + " > " + this.get_node(b).text);
            return this.get_node(a).data.position
              > this.get_node(b).data.position
              ? 1
              : -1;
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
        if (mustBePosition && mustBePosition * 1 <= newPosition) {
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
</style>
