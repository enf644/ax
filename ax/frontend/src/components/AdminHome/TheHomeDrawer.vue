<template>
  <div>
    <div class='no-forms' v-show='noForms'>
      <i class='fas fa-cat'></i>
      &nbsp;
      {{$t("home.no-forms")}}
    </div>
    <div v-show='noForms == false'>
      <h3>{{$t("home.ax-forms")}}:</h3>
      <div data-cy='forms-tree' ref='tree'></div>
    </div>
    <br />
    <v-btn @click='openFormModal' class='home-btn' data-cy='create-form-btn' small>
      <i class='fas fa-plus'></i>
      &nbsp; {{$t("home.create-form-btn")}}
    </v-btn>
    <v-btn @click='openFolderModal()' class='ml-2 home-btn' data-cy='create-folder-btn' small>
      <i class='far fa-folder'></i>
    </v-btn>

    <!--  transition='animated flipInX faster' -->
    <modal adaptive class='mb-3' height='auto' name='new-form' scrollable>
      <TheNewForm @created='closeFormModal' />
    </modal>

    <modal adaptive height='auto' name='new-folder'>
      <TheNewFolder
        :guid='currentFolderGuid'
        @created='closeFolderModal'
        @openAppModal='openAppModal'
      />
    </modal>

    <modal adaptive height='auto' name='create-app'>
      <TheNewAppModal :folderGuid='currentFolderGuid' @close='closeAppModal' />
    </modal>

    <br />
    <br />
    <h3 class='manage-label'>{{$t("home.settings")}}:</h3>
    <v-btn class='mb-3 home-btn' data-cy='manage-users-btn' small to='/admin/users'>
      <i class='far fa-user'></i>
      &nbsp; {{$t("home.users-btn")}}
    </v-btn>
    <br />
    <v-btn class='mb-3 home-btn' data-cy='marketplace-btn' small to='/admin/marketplace'>
      <i class='fas fa-store'></i>
      &nbsp; {{$t("home.marketplace-btn")}}
    </v-btn>
    <br />
    <v-btn class='mb-3 home-btn' data-cy='pages-designer-btn' small to='/admin/pages'>
      <i class='fas fa-desktop'></i>
      &nbsp; {{$t("home.pages-designer-btn")}}
    </v-btn>
    <br />
    <v-btn class='mb-3 home-btn' data-cy='data-explorer-btn' small to='/admin/explorer'>
      <i class='fas fa-database'></i>
      &nbsp; {{$t("home.explorer-btn")}}
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
import TheNewAppModal from '@/components/Marketplace/TheNewAppModal.vue';

export default {
  name: 'home-drawer',
  components: {
    TheNewForm,
    TheNewFolder,
    TheNewAppModal
  },
  data() {
    return {
      currentFolderGuid: null
    };
  },
  computed: {
    forms() {
      return this.$store.state.home.forms;
    },
    noForms() {
      if (!this.forms || this.forms.length === 0) return true;
      return false;
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
  created() {},
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
      const positionList = [];
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
        positionList.push(nodeInfo);

        const nodeObject = tree.get_node(node.id);
        nodeObject.data.position = newPosition;
      });
      return positionList;
    },
    changePositions(e, data) {
      const positionData = this.getPositionList();
      this.$store
        .dispatch('home/changeFormsPositions', {
          positions: positionData
        })
        .then(arg => {
          const msg = this.$t('common.position-changed');
          this.$dialog.message.success(
            `<i class="fas fa-sort-numeric-up"></i> &nbsp ${msg}`
          );
        });
    },
    gotoForm(e, data) {
      if (!data || !data.node) return false;

      if (data.node.type === 'folder') {
        this.openFolderModal(data.node.id);
      } else {
        this.$router.push({
          path: `/admin/${data.node.data.dbName}/form`
        });
      }
    },
    initJstree(jsTreeData) {
      $(this.$refs.tree)
        .on('move_node.jstree', (e, data) => this.changePositions(e, data))
        .on('activate_node.jstree', (e, data) => this.gotoForm(e, data))
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
    },
    openAppModal(folderGuid) {
      this.currentFolderGuid = folderGuid;
      this.$modal.hide('new-folder');
      this.$modal.show('create-app');
    },
    closeAppModal() {
      this.$modal.hide('create-app');
    }
  }
};
</script>

<style scoped>
.home-btn {
  /* width: 150px; */
}
.manage-label {
  margin-bottom: 15px;
}
</style>
