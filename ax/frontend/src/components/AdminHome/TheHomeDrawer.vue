<template>
  <div>
    <h3>Ax Forms:</h3>
    <div ref='tree'></div>
    <br>
    <v-btn @click='openFormModal' small>
      <font-awesome-icon icon='plus'/>&nbsp; Create form
    </v-btn>

    <v-btn @click='openFolderModal' small>
      <font-awesome-icon icon='folder'/>&nbsp; Create folder
    </v-btn>

    <!--  transition='animated flipInX faster' -->
    <modal adaptive height='auto' name='new-form'>
      <TheNewForm @created='closeFormModal'/>
    </modal>

    <modal adaptive height='auto' name='new-folder'>
      <TheNewFolder :guid='currentFolderGuid' @created='closeFolderModal'/>
    </modal>

    <br>
    <br>

    <h3>Settings:</h3>
    <br>
    <v-btn small to='/admin/users'>
      <font-awesome-icon icon='user'/>&nbsp; Users
    </v-btn>

    <v-btn small to='/admin/marketplace'>
      <font-awesome-icon icon='store'/>&nbsp; Marketplace
    </v-btn>

    <v-btn small to='/admin/deck'>
      <font-awesome-icon icon='money-check-alt'/>&nbsp; Deck designer
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
