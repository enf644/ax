<template>
  <div>
    <h3>{{$t("home.ax-forms")}}:</h3>
    <div data-cy='forms-tree' ref='tree'></div>
    <br>
    <v-btn @click='openFormModal' data-cy='create-form-btn' small>
      <i class='fas fa-plus'></i>
      &nbsp; {{$t("home.create-form-btn")}}
    </v-btn>

    <!--  transition='animated flipInX faster' -->
    <modal adaptive height='auto' name='new-form' scrollable>
      <TheNewForm @created='closeFormModal'/>
    </modal>

    <v-btn @click='openFolderModal()' data-cy='create-folder-btn' small>
      <i class='far fa-folder'></i>
      &nbsp; {{$t("home.create-folder-btn")}}
    </v-btn>

    <modal adaptive height='auto' name='new-folder'>
      <TheNewFolder :guid='currentFolderGuid' @created='closeFolderModal'/>
    </modal>

    <br>
    <br>

    <h3>{{$t("home.settings")}}:</h3>
    <br>
    <v-btn small to='/admin/users'>
      <i class='far fa-user'></i>
      &nbsp; {{$t("home.users-btn")}}
    </v-btn>

    <v-btn small to='/admin/marketplace'>
      <i class='fas fa-store'></i>
      &nbsp; {{$t("home.marketplace-btn")}}
    </v-btn>

    <v-btn small to='/admin/pages'>
      <i class='fas fa-desktop'></i>
      &nbsp; {{$t("home.pages-designer-btn")}}
    </v-btn>
  </div>
</template>

<script>
/* eslint-disable no-unused-vars */

import $ from 'jquery';
import 'jstree/dist/jstree.js';
import 'jstree/dist/themes/default/style.css';
import TheNewForm from '@/components/AdminHome/TheNewForm.vue';
import TheNewFolder from '@/components/AdminHome/TheNewFolder.vue';

export default {
  name: 'home-drawer',
  components: {
    TheNewForm,
    TheNewFolder
  },
  data() {
    return {
      currentFolderGuid: null
    };
  },
  computed: {
    forms() {
      return this.$store.state.home.forms;
    }
  },
  watch: {
    forms() {
      if (this.$store.state.home.positionChangedFlag) {
        // If state change is started by changing node order -> then no need for refresh
        this.$store.commit('home/setPositionChangedFlag', false);
      } else {
        const tree = $(this.$refs.tree).jstree(true);
        tree.settings.core.data = this.$store.getters['home/jsTreeData'];
        tree.refresh();
      }
    }
  },
  created() {
    if (!this.$store.state.home.isFormsLoaded) {
      this.$store.dispatch('home/getAllForms');
    }
  },
  mounted() {
    window.jQuery = $;
    window.$ = $;
    this.initJstree(this.$store.getters['home/jsTreeData']);
  },
  methods: {
    openFormModal() {
      this.$modal.show('new-form');
    },
    closeFormModal() {
      this.$modal.hide('new-form');
    },
    openFolderModal(guid = null) {
      this.currentFolderGuid = guid;
      this.$modal.show('new-folder');
    },
    closeFolderModal() {
      this.$modal.hide('new-folder');
    },
    getPositionList() {
      const orderList = [];
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
        orderList.push(nodeInfo);

        const nodeObject = tree.get_node(node.id);
        nodeObject.data.position = newPosition;
      });
      return orderList;
    },
    initJstree(jsTreeData) {
      $(this.$refs.tree)
        .on('move_node.jstree', (e, data) => {
          const positionData = this.getPositionList();
          this.$store.dispatch('home/changeFormsPositions', {
            positions: positionData
          });
        })
        .on('activate_node.jstree', (e, data) => {
          if (data.node.type === 'folder') {
            this.openFolderModal(data.node.id);
          } else {
            this.$router.push({
              path: `/admin/${data.node.data.dbName}/form`
            });
          }
        })
        .jstree({
          core: {
            data: jsTreeData,
            // eslint-disable-next-line camelcase
            check_callback(operation, node, node_parent, node_position, more) {
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
            return this.get_node(a).data.position
              > this.get_node(b).data.position
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
