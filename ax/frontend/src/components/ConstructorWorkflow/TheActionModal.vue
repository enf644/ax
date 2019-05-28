<template>
  <div class='card'>
    <h1>{{$t("workflow.action.action-settings-header")}}</h1>
    <v-btn :ripple='false' @click='closeThisModal' class='close' color='black' flat icon>
      <i class='fas fa-times close-ico'></i>
    </v-btn>
    <br>
    <v-form @submit.prevent='updateAction' ref='form' v-model='valid'>
      <v-text-field
        :label='$t("workflow.action.action-name")'
        data-cy='action-name'
        ref='nameField'
        required
        v-model='name'
      />
      <br>
      <h3>{{$t("workflow.action.settings-roles-list")}}:</h3>
      <v-chip :key='role.guid' @input='removeRole(role)' close v-for='role in axRoles'>
        <v-avatar :style='{ background: role.color }'>
          <i :class='getRoleIconClass(role)'></i>
        </v-avatar>
        {{ role.name }}
      </v-chip>

      <br>

      <modal adaptive height='auto' name='action-icon' scrollable width='800px'>
        <TheIconPicker :icon='icon' @choosed='ChangeIconAndCloseModal'/>
      </modal>

      <br>
      <h3>{{$t("workflow.action.code-header")}}:</h3>
      <monaco-editor
        class='editor'
        cy-data='code-editor'
        language='python'
        ref='editor'
        theme='vs-dark'
        v-model='code'
      ></monaco-editor>

      <br>

      <div class='actions'>
        <v-btn @click='updateAction' data-cy='update-action-btn' small>
          <i class='fas fa-pencil-alt'></i>
          &nbsp; {{$t("workflow.action.settings-update-btn")}}
        </v-btn>

        <v-btn @click='openIconPicker' data-cy='icon-btn' flat small>
          <i :class='iconClass' key='formIcon'></i>
          &nbsp; {{$t("workflow.action.icon-btn")}}
        </v-btn>

        <v-btn @click='deleteAction' color='error' data-cy='delete-action-btn' flat small>
          <i class='fas fa-trash-alt'></i>
          &nbsp; {{$t("workflow.action.settings-delete-btn")}}
        </v-btn>
      </div>
    </v-form>
  </div>
</template>

<script>
import TheIconPicker from '@/components/AdminHome/TheIconPicker.vue';
import MonacoEditor from 'vue-monaco';

export default {
  name: 'TheActionModal',
  props: {
    guid: null
  },
  components: { TheIconPicker, MonacoEditor },
  data() {
    return {
      name: '',
      code: '',
      confirmText: null,
      closeModal: null,
      icon: null,
      valid: false,
      currentGuid: null,
      nameRules: [
        v => !!v || this.$t('workflow.action.action-name-required'),
        v => v.length <= 255 || this.$t('common.lenght-error', { num: 255 })
      ]
    };
  },
  computed: {
    currentAction() {
      return this.$store.state.workflow.actions.find(
        element => element.guid === this.guid
      );
    },
    axRoles() {
      if (this.currentAction && this.currentAction.roles) {
        const roles = this.currentAction.roles.edges.map(edge => edge.node);

        // global roles have colors!
        const retRoles = [];
        const allRoles = this.$store.getters['workflow/rolesWithColor'];

        allRoles.forEach(globalRole => {
          roles.forEach(role => {
            if (role.guid === globalRole.guid) retRoles.push(globalRole);
          });
        });

        return retRoles;
      }
      return null;
    },
    iconClass() {
      if (this.icon) return `fas fa-${this.icon}`;
      return 'far fa-arrow-alt-circle-right';
    },
    axActions() {
      return this.$store.state.workflow.actions;
    }
  },
  watch: {
    axActions(newValue) {
      if (newValue) {
        this.getData(newValue);
      }
    }
  },
  mounted() {
    if (this.guid) {
      this.$refs.nameField.focus();
      this.$store.dispatch('workflow/getActionData', {
        guid: this.guid,
        updateTine: Date.now
      });
      this.getData(this.axActions);
    }
  },
  methods: {
    getData(actions) {
      const actionData = actions.find(element => element.guid === this.guid);
      if (actionData) {
        this.name = actionData.name;
        this.code = actionData.code;
        this.confirmText = actionData.confirmText;
        this.closeModal = actionData.closeModal;
        this.icon = actionData.icon;

        if (!this.code) this.code = '';
      }
    },
    openIconPicker() {
      this.$modal.show('action-icon');
    },
    ChangeIconAndCloseModal(newIcon) {
      if (newIcon) this.icon = newIcon;
      this.$modal.hide('action-icon');
    },
    getRoleIconClass(role) {
      let retIcon = 'user-tie';
      if (role.icon) retIcon = role.icon;

      return `fas fa-${retIcon}`;
    },
    removeRole(role) {
      const args = {
        guid: null,
        actionGuid: this.guid,
        roleGuid: role.guid
      };
      this.$store.dispatch('workflow/deleteRoleFromAction', args).then(() => {
        const msg = this.$t('workflow.role.role-removed-from-action-toast');
        this.$dialog.message.success(
          `<i class="fas fa-trash-alt"></i> &nbsp ${msg}`
        );
      });
    },
    updateAction() {
      if (this.$refs.form.validate()) {
        const data = {
          guid: this.guid,
          name: this.name,
          code: this.code,
          confirmText: this.confirmText,
          closeModal: this.closeModal,
          icon: this.icon
        };
        this.$store.dispatch('workflow/updateAction', data).then(() => {
          const msg = this.$t('workflow.action.update-action-toast');
          this.$dialog.message.success(
            `<i class="fas fa-pencil-alt"></i> &nbsp ${msg}`
          );
          this.currentGuid = this.guid;
          this.$emit('updateAction');
        });
      }
    },
    async deleteAction(e) {
      e.preventDefault();
      const res = await this.$dialog.confirm({
        text: this.$t('workflow.action.action-delete-confirm', {
          name: this.name
        }),
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
          .dispatch('workflow/deleteAction', {
            guid: this.guid
          })
          .then(() => {
            const msg = this.$t('workflow.action.delete-action-toast');
            this.$dialog.message.success(
              `<i class="fas fa-trash-alt"></i> &nbsp ${msg}`
            );
            this.currentGuid = this.guid;
            this.$emit('updateAction');
          });
      }
    },
    closeThisModal() {
      this.$emit('close');
    }
  }
};
</script>

<style scoped>
.card {
  padding: 25px;
}
.close {
  position: absolute;
  right: 10px;
  top: 10px;
}
.close-ico {
  font-size: 20px;
}
.actions {
  justify-content: space-between;
  display: flex;
}
.editor {
  width: 100%;
  height: 600px;
}
</style>
