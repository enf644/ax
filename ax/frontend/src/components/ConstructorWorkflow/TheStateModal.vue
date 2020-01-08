<template>
  <div class='card'>
    <h1>{{$t("workflow.state.state-settings-header")}}</h1>
    <v-btn :ripple='false' @click='closeModal' class='close' color='black' icon text>
      <i class='fas fa-times close-ico'></i>
    </v-btn>
    <br />
    <v-form @submit.prevent='updateState' ref='form' v-model='valid'>
      <v-text-field
        :hint='$t("workflow.state.state-name-hint")'
        :label='$t("workflow.state.state-name")'
        :rules='nameRules'
        @input='resetNameValid'
        data-cy='state-name'
        ref='nameField'
        required
        v-model='name'
      />
      <br />

      <h2>{{$t("workflow.role.permissions-header")}}:</h2>

      <div class='tbl-div'>
        <table class='perm-table'>
          <thead>
            <th>&nbsp;</th>
            <th :key='role.guid' v-for='role in axRoles'>
              <span class='nobr'>
                {{ role.name }}
                <v-btn
                  @click='deleteRoleFromState(role)'
                  class='breadcrumbs-action'
                  color='black'
                  data-cy='delete-role'
                  icon
                  text
                >
                  <i class='fas fa-times breadcrumbs-action-i'></i>
                </v-btn>
              </span>
            </th>
          </thead>
          <tbody>
            <tr :key='"f_" + field.guid' v-for='field in axFields'>
              <th>
                <b v-if='field.isTab'>{{ field.name }}</b>
                <span v-else>&nbsp;&nbsp;&nbsp; {{ field.name }}</span>
              </th>
              <td :key='fieldRole.guid' v-for='fieldRole in axRoles'>
                <ThePermSwitch
                  :fieldGuid='field.guid'
                  :parent='field.parent'
                  :roleGuid='fieldRole.guid'
                  :stateGuid='guid'
                />
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <br />
      <br />

      <div class='actions'>
        <v-btn @click='updateState' data-cy='update-state-btn' small>
          <i class='fas fa-pencil-alt'></i>
          &nbsp; {{$t("workflow.state.update-state-btn")}}
        </v-btn>

        <v-btn @click='deleteState' color='error' data-cy='delete-state-btn' small text>
          <i class='fas fa-trash-alt'></i>
          &nbsp; {{$t("workflow.state.delete-state-btn")}}
        </v-btn>
      </div>
    </v-form>
  </div>
</template>

<script>
import ThePermSwitch from '@/components/ConstructorWorkflow/ThePermSwitch.vue';

export default {
  name: 'TheStateModal',
  props: {
    guid: null
  },
  components: { ThePermSwitch },
  data() {
    return {
      name: '',
      currentGuid: null,
      valid: false,
      nameRules: [
        v => !!v || this.$t('workflow.state.state-name-required'),
        v => v.length <= 255 || this.$t('common.lenght-error', { num: 255 }),
        v =>
          (v && this.nameIsAvalible) ||
          this.$t('workflow.state.name-not-avalible')
      ]
    };
  },
  computed: {
    nameIsAvalible() {
      let isAvalible = true;
      this.$store.state.workflow.states.forEach(state => {
        if (state.guid !== this.guid && state.name === this.name) {
          isAvalible = false;
        }
      });
      return isAvalible;
    },
    currentState() {
      return this.$store.state.workflow.states.find(
        element => element.guid === this.guid
      );
    },
    axRoles() {
      if (this.currentState && this.currentState.roles) {
        const roles = this.currentState.roles.edges.map(edge => edge.node);
        return roles;
      }
      return null;
    },
    axFields() {
      return this.$store.getters['form/fieldsTabSorted'];
    }
  },
  watch: {},
  mounted() {
    this.$refs.nameField.focus();
    this.name = this.currentState.name;
  },
  methods: {
    resetNameValid() {
      if (this.nameIsAvalible === false) {
        this.$refs.form.validate();
      }
    },
    async deleteRoleFromState(role) {
      const res = await this.$dialog.confirm({
        text: this.$t('workflow.role.delete-role-from-state-confirm', {
          role: role.name,
          state: this.name
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
          .dispatch('workflow/deleteRoleFromState', {
            stateGuid: this.guid,
            roleGuid: role.guid
          })
          .then(() => {
            const msg = this.$t('workflow.role.role-removed-from-state-toast');
            this.$dialog.message.success(
              `<i class="fas fa-times"></i> &nbsp ${msg}`
            );
          });
      }
    },
    updateState() {
      if (this.$refs.form.validate()) {
        const data = {
          guid: this.guid,
          name: this.name
        };
        this.$store.dispatch('workflow/updateState', data).then(() => {
          const msg = this.$t('workflow.state.update-state-toast');
          this.$dialog.message.success(
            `<i class="fas fa-pencil-alt"></i> &nbsp ${msg}`
          );
          this.currentGuid = this.guid;
          this.$emit('updateState');
        });
      }
    },
    async deleteState(e) {
      e.preventDefault();
      const res = await this.$dialog.confirm({
        text: this.$t('workflow.state.state-delete-confirm', {
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
          .dispatch('workflow/deleteState', {
            guid: this.guid
          })
          .then(() => {
            const msg = this.$t('workflow.state.delete-state-toast');
            this.$dialog.message.success(
              `<i class="fas fa-trash-alt"></i> &nbsp ${msg}`
            );
            this.currentGuid = this.guid;
            this.$emit('updateState');
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
table {
  width: 100%;
}
td:first-child,
th:first-child {
  position: sticky;
  left: 0;
  z-index: 1;
}
thead tr th {
  position: sticky;
  top: 0;
}

tr:nth-child(even) {
  background-color: #f5f5f5;
}

tr:nth-child(odd) {
  background-color: white;
}

td,
th {
  padding: 0px 30px 0px 0px;
  text-align: left;
  white-space: nowrap;
  background: inherit;
  font-weight: normal;
}

.del {
  cursor: pointer;
  color: #c0c0c0;
}

.tbl-div {
  overflow: auto;
  width: 100%;
}
.breadcrumbs-action {
  margin: 0;
  width: 25px;
  height: 25px;
}

.breadcrumbs-action-i {
  color: #c0c0c0;
}
.nobr {
  white-space: nowrap;
}
</style>
