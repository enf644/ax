<template>
  <div>
    <h3>{{$t("workflow.role.roles-header")}}:</h3>
    <div :key='role.guid' @click='openRoleModal(role)' draggable='true' v-for='role in roles'>
      <div :style='{ background: getColor(role)}' class='role-box'>
        <i :class='getIconClass(role)'></i>
        &nbsp; {{ role.name }}
      </div>
    </div>

    <modal adaptive height='auto' name='update-role' scrollable>
      <TheRoleModal :guid='this.selectedRoleGuid' @close='closeModal'/>
    </modal>

    <br>

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
    materialColors: [
      '#8BC34A',
      '#FFEB3B',
      '#FFC107',
      '#2196F3',
      '#FF9800',
      '#00BCD4',
      '#CDDC39',
      '#E91E63',
      '#FF5722',
      '#009688',
      '#4CAF50',
      '#9E9E9E',
      '#F44336',
      '#3F51B5',
      '#FF9800'
    ]
  }),
  computed: {
    roles() {
      return this.$store.state.workflow.roles;
    }
  },
  methods: {
    getIconClass(role) {
      let roleIcon = 'user-tie';
      if (role.icon) roleIcon = role.icon;
      return `fas fa-${roleIcon}`;
    },
    getColor(role) {
      let index = this.roles.indexOf(role);
      while (index > this.materialColors.length) {
        index -= this.materialColors.length;
      }
      return this.materialColors[index];
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
