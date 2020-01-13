<template>
  <div>
    <h3>{{$t("form.columns-header")}}:</h3>
    <div data-cy='columns-tree' ref='tree'></div>

    <br />
    <v-divider></v-divider>
    <br />

    <v-btn
      @click='saveSortFilterModel()'
      class='save-model-btn'
      data-cy='save-grid-model-btn'
      small
    >
      <i class='fas fa-sort-amount-down-alt'></i>
      &nbsp;
      {{$t("grids.save-filter-order-btn")}}
    </v-btn>

    <v-btn @click='openQueryModal' data-cy='query-modal-btn' small>
      <i class='fas fa-filter'></i>
      &nbsp;
      {{$t("grids.query-modal-btn")}}
    </v-btn>

    <modal adaptive height='auto' name='query-modal' scrollable width='1000px'>
      <TheQueryModal @close='closeQueryModal' />
    </modal>

    <br />
    <br />

    <v-switch
      :label='this.$t("grids.options-quick-search")'
      @change='saveOptions'
      class='options-switcher'
      data-cy='options-quick-search'
      v-model='changedOptions.enableQuickSearch'
    ></v-switch>

    <v-switch
      :label='this.$t("grids.options-title")'
      @change='saveOptions'
      class='options-switcher'
      data-cy='options-enable-title'
      v-model='changedOptions.enableTitle'
    ></v-switch>

    <v-switch
      :label='this.$t("grids.options-flat-mode")'
      @change='saveOptions'
      class='options-switcher'
      data-cy='options-flat-mode'
      v-model='changedOptions.enableFlatMode'
    ></v-switch>

    <v-switch
      :label='this.$t("grids.options-subscription")'
      @change='saveOptions'
      class='options-switcher'
      data-cy='options-subscription'
      v-model='changedOptions.enableSubscription'
    ></v-switch>

    <v-switch
      :label='this.$t("grids.options-columns-resize")'
      @change='saveOptions'
      class='options-switcher'
      data-cy='options-columns-resize'
      v-model='changedOptions.enableColumnsResize'
    ></v-switch>

    <v-switch
      :label='this.$t("grids.options-filtering")'
      @change='saveOptions'
      class='options-switcher'
      data-cy='options-filtering'
      v-model='changedOptions.enableFiltering'
    ></v-switch>

    <v-switch
      :label='this.$t("grids.options-soring")'
      @change='saveOptions'
      class='options-switcher'
      data-cy='options-soring'
      v-model='changedOptions.enableSorting'
    ></v-switch>

    <v-switch
      :label='this.$t("grids.options-open-form")'
      @change='saveOptions'
      class='options-switcher'
      data-cy='options-open-form'
      v-model='changedOptions.enableOpenForm'
    ></v-switch>

    <v-switch
      :label='this.$t("grids.options-actions")'
      @change='saveOptions'
      class='options-switcher'
      data-cy='options-actions'
      v-model='changedOptions.enableActions'
    ></v-switch>

    <v-subheader class='pl-0' data-cy='options-row-height'>{{$t("grids.options-row-height")}}</v-subheader>
    <v-slider
      @change='saveOptions'
      class='options-switcher'
      max='250'
      min='35'
      thumb-label
      v-model='changedOptions.rowHeight'
    ></v-slider>

    <v-subheader class='pl-0' data-cy='options-pinned'>{{$t("grids.options-pinned")}}</v-subheader>
    <v-slider
      @change='saveOptions'
      class='options-switcher'
      max='10'
      thumb-label
      v-model='changedOptions.pinned'
    ></v-slider>
    <br />
    <br />
    <v-btn @click='copyUrl()' class='mb-3' data-cy='copy-url-btn' small text>
      <i class='fas fa-link'></i>
      &nbsp; {{$t("form.copy-url")}}
    </v-btn>

    <br />
    <v-btn @click='copyTag()' class='mb-3' data-cy='copy-tag-btn' small text>
      <i class='fas fa-code'></i>
      &nbsp; {{$t("form.copy-tag")}}
    </v-btn>

    <br />
    <v-btn @click='copyGraphql()' class='mb-3' data-cy='copy-graphql-btn' small text>
      <i class='fas fa-project-diagram'></i>
      &nbsp; {{$t("grids.copy-graphql")}}
    </v-btn>
  </div>
</template>

<script>
import $ from 'jquery';
import copy from 'copy-to-clipboard';
import { getAxHost, getAxProtocol } from '@/misc';
import 'jstree/dist/jstree.js';
import 'jstree/dist/themes/default/style.css';
import TheQueryModal from '@/components/ConstructorGrids/TheQueryModal.vue';

export default {
  name: 'admin-grids-drawer-second',
  data: () => ({
    treeInitialized: false,
    changedOptions: {},
    optionsLoaded: false
  }),
  components: {
    TheQueryModal
  },
  computed: {
    columns() {
      return this.$store.state.grids.columns;
    },
    allFields() {
      return this.$store.state.form.fields;
    },
    updated() {
      return this.$store.state.grids.updateTime;
    },
    options() {
      return this.$store.state.grids.options;
    },
    updateTime() {
      return this.$store.state.grids.updateTime;
    },
    formDbName() {
      return this.$store.state.grids.formDbName;
    },
    gridDbName() {
      return this.$store.state.grids.dbName;
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
    saveSortFilterModel() {
      this.$store.commit('grids/setDoSaveSortFilterModel', true);
    },
    openQueryModal() {
      this.$modal.show('query-modal');
    },
    closeQueryModal() {
      this.$modal.hide('query-modal');
    },
    saveOptions() {
      console.log('save options');
      if (this.$store.state.grids.loadingDone) {
        this.$store.commit('grids/combineOptions', this.changedOptions);
        this.$store
          .dispatch('grids/updateGrid', { updateNeeded: true })
          .then(() => {
            const msg = this.$t('grids.grid-updated');
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
        .on('move_node.jstree', (e, data) =>
          this.changeColumnPositions(e, data)
        )
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
              return this.get_node(a).data.position >
                this.get_node(b).data.position
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
    },
    copyUrl() {
      const url = `${getAxProtocol()}://${getAxHost()}/grid/${
        this.formDbName
      }/${this.gridDbName}`;
      copy(url);
      const msg = `Copied to clipboard - ${url}`;
      this.$store.commit('home/setShowToastMsg', msg);
    },
    copyTag() {
      const tag = `<ax-grid form="${this.formDbName}" grid="${this.gridDbName}" />`;
      const msg_tag = `&lt;ax-grid form="${this.formDbName}" grid="${this.gridDbName}" /&gt;`;
      copy(tag);
      const msg = `Copied to clipboard - ${tag}`;
      this.$store.commit('home/setShowToastMsg', msg_tag);
    },
    copyGraphql() {
      const viewName = this.formDbName + this.gridDbName;
      let qry = '';
      qry += 'query {';
      qry += `\n  ${viewName} {`;
      this.allFields.forEach(field => {
        const tomFieldTags = ['Ax1to1', 'Ax1tom', 'Ax1tomTable'];
        if (!field.isTab && !field.fieldType.isVirtual) {
          if (tomFieldTags.includes(field.fieldType.tag)) {
            qry += `\n    ${field.dbName} {`;
            qry += `\n      guid`;
            qry += `\n    }`;
          } else {
            qry += `\n    ${field.dbName}`;
          }
        }
      });
      qry += '\n  }';
      qry += '\n}';
      copy(qry);
      const msg = `<pre>${qry}</pre>`;
      this.$store.commit('home/setShowToastMsg', msg);
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
.save-model-btn {
  margin-bottom: 10px;
}
</style>
