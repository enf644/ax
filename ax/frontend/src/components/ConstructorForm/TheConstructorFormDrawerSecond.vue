<template>
  <div>
    <h3>{{$t("form.fields-header")}}:</h3>
    <div data-cy='fields-tree' ref='tree'></div>

    <br>
    <v-btn @click='createTab' data-cy='add-tab-btn' small>
      <i class='far fa-folder'></i>
      &nbsp; {{$t("form.add-tab")}}
    </v-btn>
  </div>
</template>

<script>
import Vue from 'vue';
import $ from 'jquery';
import 'jstree/dist/jstree.js';
import 'jstree/dist/themes/default/style.css';
import ConstructorField from '@/components/ConstructorForm/ConstructorField.vue';
import ConstructorTab from '@/components/ConstructorForm/ConstructorTab.vue';

export default {
  name: 'admin-form-drawer-second',
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
        tree.settings.core.data = this.$store.getters['form/fieldTreeData'];
        tree.refresh(true, false);
      } else {
        this.initFieldTree(this.$store.getters['form/fieldTreeData']);
      }
    }
  },
  created() {
    Vue.customElement('constructor-field', ConstructorField);
    Vue.customElement('constructor-tab', ConstructorTab);
  },
  mounted() {
    window.jQuery = $;
    window.$ = $;

    if (!this.treeInitialized) {
      this.initFieldTree(this.$store.getters['form/fieldTreeData']);
    }
  },
  methods: {
    createTab() {
      const args = {
        formGuid: this.$store.state.form.guid,
        name: this.$t('form.new-tab-dummy')
      };
      this.$store.dispatch('form/createTab', args).then(() => {
        const msg = this.$t('form.add-tab-toast');
        this.$dialog.message.success(
          `<i class="fas fa-folder"></i> &nbsp ${msg}`
        );
      });
    },
    createField(e, data) {
      const mustBePosition = data.position;
      const tag = data.original.id;
      $(this.$refs.tree)
        .jstree()
        .delete_node(data.node);
      const positionList = this.getPositionList(mustBePosition);
      const locale = `types.${tag}`;
      const defaultName = this.$t(locale);
      this.$store
        .dispatch('form/createField', {
          tag,
          name: defaultName,
          positions: positionList,
          position: mustBePosition,
          parent: data.parent
        })
        .then(() => {
          const msg = this.$t('form.add-field-toast');
          this.$dialog.message.success(
            `<i class="fas fa-${data.original.icon}"></i> &nbsp ${msg}`
          );
        });
    },
    changeFieldsPositions() {
      const positions = this.getPositionList();
      this.$store
        .dispatch('form/changeFieldsPositions', { positions })
        .then(() => {
          const msg = this.$t('common.position-changed');
          this.$dialog.message.success(
            `<i class="fas fa-sort-numeric-up"></i> &nbsp ${msg}`
          );
        });
    },
    initFieldTree(jsTreeData) {
      $(this.$refs.tree)
        .on('move_node.jstree', (e, data) => this.changeFieldsPositions(e, data))
        .on('copy_node.jstree', (e, data) => this.createField(e, data))
        .on('ready.jstree', () => {})
        .jstree({
          core: {
            data: jsTreeData,
            // "animation" : 100,
            check_callback(operation, node, nodeParent) {
              if (operation === 'move_node') {
                if (node.type !== 'tab') {
                  if (nodeParent.parent !== '#') return false;
                }
              }

              if (operation === 'copy_node') {
                if (nodeParent.parent == null) {
                  return false;
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
            tab: {
              icon: false,
              valid_children: ['default'],
              li_attr: { class: 'jstree-field' }
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
          const fieldGuid = e.currentTarget.id.replace('_anchor', '');
          console.log(`DELETE FIELD -> ${fieldGuid}`);
        }
      });

      this.treeInitialized = true;
    },
    getPositionList(mustBePosition) {
      const positionList = [];
      const tree = $(this.$refs.tree).jstree(true);
      const jsonNodes = tree.get_json('#', { flat: true });
      $.each(jsonNodes, (i, node) => {
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

        // const nodeObject = tree.get_node(node.id);
        // nodeObject.data.position = newPosition;
      });
      return positionList;
    }
  }
};
</script>

<style scoped>
</style>
