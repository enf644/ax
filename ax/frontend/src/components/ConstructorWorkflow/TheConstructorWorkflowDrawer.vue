<template>
  <div v-show='formGuid'>
    <h3>{{$t("workflow.role.roles-list-header")}}:</h3>
    <div v-if='this.roles.length == 0'>
      <i class='fas fa-user-slash'></i>
      &nbsp; {{$t("workflow.role.no-roles")}}
    </div>
    <div
      :key='role.guid'
      @click='openRoleModal(role)'
      @dragstart='onDragStart(role, $event)'
      @mouseout='highlightRole(null)'
      @mouseover='highlightRole(role)'
      draggable='true'
      v-for='role in roles'
    >
      <div :style='{ background: role.color }' class='role-box'>
        <i :class='getIconClass(role)'></i>
        &nbsp; {{ role.name }}
      </div>
    </div>

    <modal :height='windowHeight' adaptive name='update-role' width='1000px'>
      <TheRoleModal :guid='this.selectedRoleGuid' @close='closeModal' />
    </modal>

    <br />

    <v-btn @click='createRole' data-cy='create-role-btn' small>
      <i class='fas fa-plus'></i>
      &nbsp; {{$t("workflow.role.create-role-btn")}}
    </v-btn>
  </div>
</template>

<script>
import TheRoleModal from '@/components/ConstructorWorkflow/TheRoleModal.vue';

export default {
  name: 'WorkflowDrawer',
  components: { TheRoleModal },
  data: () => ({
    selectedRoleGuid: null,
    windowHeight: null
  }),
  computed: {
    roles() {
      return this.$store.getters['workflow/rolesWithColor'];
    },
    formGuid() {
      return this.$store.state.workflow.formGuid;
    }
  },
  created() {
    this.windowHeight = window.innerHeight * 1 - 50;
  },
  methods: {
    highlightRole(role) {
      this.$store.commit('workflow/setHighlightedRole', role);
    },
    onDragStart(role, ev) {
      ev.dataTransfer.setData('roleGuid', role.guid);
    },
    getIconClass(role) {
      let roleIcon = 'user-tie';
      if (role.icon) roleIcon = role.icon;
      return `fas fa-${roleIcon}`;
    },
    async createRole() {
      const res = await this.$dialog.prompt({
        text: this.$t('workflow.role.add-role-prompt'),
        actions: {
          true: {
            text: this.$t('common.confirm')
          }
        }
      });
      if (res) {
        const args = {
          name: res
        };
        this.$store.dispatch('workflow/createRole', args).then(() => {
          const msg = this.$t('workflow.role.add-role-toast');
          this.$dialog.message.success(
            `<i class="fas user-tie"></i> &nbsp ${msg}`
          );
        });
      }
    },
    openRoleModal(role) {
      this.selectedRoleGuid = role.guid;
      this.$modal.show('update-role');
    },
    closeModal() {
      this.$modal.hide('update-role');
    }
  }
};
</script>

<style scoped>
.role-box {
  background: #ccc;
  padding: 5px 15px 5px 15px;
  text-align: left;
  border-radius: 5px;
  cursor: pointer;
  margin-top: 10px;
}
</style>
