<template>
  <div v-show='formGuid'>
    <h3>{{$t("workflow.role.roles-list-header")}}:</h3>
    <div v-if='noWorkflowRoles'>
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
      <div :style='{ background: role.color }' class='role-box' v-if='!role.isDynamic'>
        <i :class='getIconClass(role)'></i>
        &nbsp; {{ role.name }}
      </div>
    </div>

    <v-btn @click='createRole' class='add-role-btn' data-cy='create-role-btn' small>
      <i class='fas fa-plus'></i>
      &nbsp; {{$t("workflow.role.create-role-btn")}}
    </v-btn>

    <br />
    <br />
    <h3>{{$t("workflow.role.dynamic-roles-list-header")}}:</h3>
    <div v-if='noDynamicRoles'>
      <i class='fas fa-user-slash'></i>
      &nbsp; {{$t("workflow.role.no-roles")}}
    </div>
    <div
      :key='role.name'
      @click='openRoleModal(role)'
      @dragstart='onDragStart(role, $event)'
      @mouseout='highlightRole(null)'
      @mouseover='highlightRole(role)'
      draggable='true'
      v-for='role in roles'
    >
      <div :style='{ background: role.color }' class='role-box' v-if='role.isDynamic'>
        <i :class='getIconClass(role)'></i>
        &nbsp; {{ role.name }}
      </div>
    </div>

    <v-badge class='add-role-btn' color='error' overlap v-model='showProBadge'>
      <template v-slot:badge>
        <span class='drawer-toggle-errors'>{{showProBadge}}</span>
      </template>
      <v-btn
        :disabled='proEnabled == false'
        @click='createDynamicRole'
        data-cy='create-dynamic-role-btn'
        small
      >
        <i class='fas fa-plus'></i>
        &nbsp; {{$t("workflow.role.create-dynamic-role-btn")}}
      </v-btn>
    </v-badge>

    <modal :height='windowHeight' adaptive name='update-role' width='1000px'>
      <TheRoleModal :guid='this.selectedRoleGuid' @close='closeModal' />
    </modal>
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
    },
    noWorkflowRoles() {
      return this.roles.filter(role => role.isDynamic != true).length == 0;
    },
    noDynamicRoles() {
      return this.roles.filter(role => role.isDynamic == true).length == 0;
    },
    showProBadge() {
      if (this.proEnabled == false) return 'pro';
      return false;
    },
    proEnabled() {
      if (this.$store.state.home.clientGuid) return true;
      return false;
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
      if (role.icon) return `fas fa-${role.icon}`;
      return 'fas fa-user-friends';
    },
    checkRoleNameExists(name) {
      let ret_value = false;
      this.roles.forEach(role => {
        if (role.name == name) ret_value = true;
      });
      return ret_value;
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
        if (!this.checkRoleNameExists(res)) {
          const args = {
            name: res
          };
          this.$store.dispatch('workflow/createRole', args).then(() => {
            const msg = this.$t('workflow.role.add-role-toast');
            this.$dialog.message.success(
              `<i class="fas user-tie"></i> &nbsp ${msg}`
            );
          });
        } else {
          const msg = this.$t('workflow.role.role-name-exists-toast', {
            name: res
          });
          this.$dialog.message.error(`<i class="fas fa-bug"></i> &nbsp ${msg}`);
        }
      }
    },
    async createDynamicRole() {
      const res = await this.$dialog.prompt({
        text: this.$t('workflow.role.add-role-prompt'),
        actions: {
          true: {
            text: this.$t('common.confirm')
          }
        }
      });
      if (res) {
        if (!this.checkRoleNameExists(res)) {
          const args = {
            name: res,
            isDynamic: true
          };
          this.$store.dispatch('workflow/createRole', args).then(() => {
            const msg = this.$t('workflow.role.add-role-toast');
            this.$dialog.message.success(
              `<i class="fas user-tie"></i> &nbsp ${msg}`
            );
          });
        } else {
          const msg = this.$t('workflow.role.role-name-exists-toast', {
            name: res
          });
          this.$dialog.message.error(`<i class="fas fa-bug"></i> &nbsp ${msg}`);
        }
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
.add-role-btn {
  margin-top: 15px;
}
</style>
