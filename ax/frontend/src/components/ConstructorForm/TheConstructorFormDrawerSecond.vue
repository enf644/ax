<template>
  <div>
    <h3>{{$t("form.fields-header")}}:</h3>
    <div data-cy='fields-tree' ref='tree'></div>

    <br>
    <v-btn @click='createTab' data-cy='add-tab-btn' small>
      <i class='far fa-folder'></i>
      &nbsp; {{$t("form.add-tab")}}
    </v-btn>

    <modal adaptive height='auto' name='field-settings' scrollable width='600px'>
      <v-card>
        <component
          :guid='settingsGuid'
          :is='component'
          :options='settingsOptions'
          :privateOptions='privateOptions'
          @closed='closeSettings()'
          v-if='component'
        />
      </v-card>
    </modal>
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
    treeInitialized: false,
    component: null,
    settingsGuid: null,
    settingsOptions: null,
    privateOptions: null
  }),
  computed: {
    fields() {
      return this.$store.state.form.fields;
    },
    settingsFieldGuid() {
      return this.$store.state.form.openSettingsFlag;
    }
  },
  watch: {
    fields(newValue, oldValue) {
      if (oldValue.length === 0) {
        this.openFirstNode();
      }

      if (this.treeInitialized) {
        if (!this.$store.state.form.isNameChangeOperation) {
          const tree = $(this.$refs.tree).jstree(true);
          tree.settings.core.data = this.$store.getters['form/fieldTreeData'];
          tree.refresh(true, false);
        } else {
          this.$store.commit('form/setIsNameChangeOperation', false);
        }
      } else {
        this.initFieldTree(this.$store.getters['form/fieldTreeData']);
      }
    },
    settingsFieldGuid(newValue) {
      if (newValue) this.openSettings(newValue);
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
    settingLoader(tag) {
      return () => import(`@/components/AxFields/${tag}/${tag}Settings.vue`);
    },
    openSettings(fieldGuid) {
      const field = this.$store.state.form.fields.find(
        f => f.guid === fieldGuid
      );
      this.settingsGuid = field.guid;

      let options = null;
      let privateOptions = null;
      try {
        options = JSON.parse(field.optionsJson);
        privateOptions = JSON.parse(field.privateOptionsJson);
      } catch {
        this.$log.error(`Unable to parse options json for ${field.dbName}`);
      }

      this.settingsOptions = options;
      this.privateOptions = privateOptions;
      const ftag = field.fieldType.tag;

      import(`@/components/AxFields/${ftag}/${ftag}Settings.vue`)
        .then(() => {
          this.component = () => import(`@/components/AxFields/${ftag}/${ftag}Settings.vue`);
        })
        .catch(() => {
          this.component = () => import('@/components/AxFieldSettings.vue');
        });

      this.$modal.show('field-settings');
      this.$store.commit('form/setOpenSettingsFlag', null);
    },
    closeSettings() {
      this.component = null;
      this.settingsOptions = null;
      this.settingsGuid = null;
      this.$store.commit('form/setOpenSettingsFlag', null);
      this.$modal.hide('field-settings');
    },
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
    openTab(guid) {
      const guidId = `#${guid}`;
      setTimeout(() => {
        $(this.$refs.tree).jstree('open_node', $(guidId), false, true);
      }, 300);
    },
    createField(e, data) {
      this.$nextTick(() => {
        const mustBePosition = data.position;
        const tag = data.original.id;
        $(this.$refs.tree)
          .jstree()
          .delete_node(data.node);
        const positionList = this.getPositionList(mustBePosition);
        const locale = `types.${tag}.name`;
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
            this.openTab(data.parent);
            const msg = this.$t('form.add-field-toast');
            this.$dialog.message.success(
              `<i class="fas fa-${data.original.data.icon}"></i> &nbsp ${msg}`
            );
          });
      });
    },
    async deleteTab(field) {
      const tabFields = this.$store.state.form.fields.filter(
        f => f.parent === field.guid
      );
      if (tabFields && tabFields.length > 0) {
        const msg = this.$t('form.error-tab-have-children', {
          num: tabFields.length
        });
        this.$dialog.error({
          text: msg,
          actions: {
            false: this.$t('common.error-close')
          }
        });
      } else {
        const res = await this.$dialog.confirm({
          text: this.$t('form.delete-tab-confirm', { name: field.name }),
          actions: {
            false: this.$t('common.confirm-no'),
            true: {
              text: this.$t('common.confirm-yes'),
              color: 'red'
            }
          }
        });
        if (res) {
          this.$store
            .dispatch('form/deleteTab', { guid: field.guid })
            .then(() => {
              const msg = this.$t('form.delete-tab-toast');
              this.$dialog.message.success(
                `<i class="far fa-trash-alt"></i> &nbsp ${msg}`
              );
            });
        }
      }
    },
    async deleteField(guid) {
      const field = this.$store.state.form.fields.find(f => f.guid === guid);
      if (field.isTab) return this.deleteTab(field);

      const res = await this.$dialog.confirm({
        text: this.$t('form.delete-field-confirm', { name: field.name }),
        actions: {
          false: this.$t('common.confirm-no'),
          true: {
            text: this.$t('common.confirm-yes'),
            color: 'red'
          }
        }
      });
      if (res) {
        this.$store
          .dispatch('form/deleteField', { guid: field.guid })
          .then(() => {
            const msg = this.$t('form.delete-field-toast');
            this.$dialog.message.success(
              `<i class="far fa-trash-alt"></i> &nbsp ${msg}`
            );
          });
      }
      return true;
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
    openFirstNode() {
      setTimeout(() => {
        $(this.$refs.tree).jstree('select_node', 'ul > li:first');
        const selectNode = $(this.$refs.tree).jstree('get_selected');
        $(this.$refs.tree).jstree('open_node', selectNode, false, true);
      }, 300);
    },
    initFieldTree(jsTreeData) {
      $(this.$refs.tree)
        .on('move_node.jstree', (e, data) => this.changeFieldsPositions(e, data))
        .on('copy_node.jstree', (e, data) => this.createField(e, data))
        .on('ready.jstree', () => this.openFirstNode())
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
          const fieldGuid = e.currentTarget.id.replace('_anchor', '');
          this.deleteField(fieldGuid);
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
</style>
