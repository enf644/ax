<template>
  <div class='card'>
    <h1>{{$t("workflow.role.role-settings-header")}}</h1>
    <v-btn :ripple='false' @click='closeModal' class='close' color='black' flat icon>
      <i class='fas fa-times close-ico'></i>
    </v-btn>
    <br>
    <v-form @submit.prevent='updateRole' ref='form' v-model='valid'>
      <v-text-field
        :label='$t("workflow.role.role-name")'
        :rules='nameRules'
        data-cy='role-name'
        ref='nameField'
        required
        v-model='name'
      />
    </v-form>
    <br>

    <div class='actions'>
      <v-btn @click='updateRole' data-cy='update-role-btn' small>
        <i class='fas fa-pencil-alt'></i>
        &nbsp; {{$t("workflow.role.update-role-btn")}}
      </v-btn>

      <v-btn @click='deleteRole' color='error' data-cy='delete-role-btn' flat small>
        <i class='fas fa-trash-alt'></i>
        &nbsp; {{$t("workflow.role.delete-role-btn")}}
      </v-btn>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TheRoleModal',
  props: {
    guid: null
  },
  data() {
    return {
      name: '',
      valid: false,
      nameRules: [
        v => !!v || this.$t('workflow.role.role-name-required'),
        v => v.length <= 255 || this.$t('common.lenght-error', { num: 255 })
      ]
    };
  },
  computed: {},
  watch: {},
  mounted() {
    this.$refs.nameField.focus();
    this.name = this.$store.state.workflow.roles.find(
      role => role.guid === this.guid
    ).name;
  },
  methods: {
    updateRole() {
      if (this.$refs.form.validate()) {
        const data = {
          guid: this.guid,
          name: this.name,
          icon: null
        };
        this.$store.dispatch('workflow/updateRole', data).then(() => {
          const msg = this.$t('workflow.role.update-role-toast');
          this.$dialog.message.success(
            `<i class="fas fa-pencil-alt"></i> &nbsp ${msg}`
          );
          this.closeModal();
        });
      }
    },
    async deleteRole(e) {
      const res = await this.$dialog.confirm({
        text: this.$t('workflow.role.role-delete-confirm', { name: this.name }),
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
          .dispatch('workflow/deleteRole', {
            guid: this.guid
          })
          .then(() => {
            const msg = this.$t('workflow.role.role-deleted-toast');
            this.$dialog.message.success(
              `<i class="fas fa-trash-alt"></i> &nbsp ${msg}`
            );
            this.closeModal();
          });
      }
    },
    closeModal() {
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
</style>
