<template>
  <div class='card'>
    <h1>{{$t("workflow.action.action-settings-header")}}</h1>
    <v-btn :ripple='false' @click='closeThisModal' class='close' color='black' icon text>
      <i class='fas fa-times close-ico'></i>
    </v-btn>
    <br />
    <v-form @submit.prevent='updateAction' ref='form' v-model='valid'>
      <v-container>
        <v-row>
          <v-col>
            <v-text-field
              :label='$t("workflow.action.action-name")'
              :rules='nameRules'
              data-cy='action-name'
              ref='nameField'
              required
              v-model='name'
            />
          </v-col>
          <v-col>
            <h3>{{$t("workflow.action.settings-roles-list")}}:</h3>
            <v-chip :key='role.guid' @click:close='removeRole(role)' close v-for='role in axRoles'>
              <v-avatar :style='{ background: role.color }' left>
                <i :class='getRoleIconClass(role)'></i>
              </v-avatar>
              {{ role.name }}
            </v-chip>
            <div v-if='noAxRoles'>
              <i class='fas fa-user-slash'></i>
              &nbsp; {{$t("workflow.action.no-roles-added")}}
            </div>
          </v-col>
        </v-row>

        <v-switch :label='$t("workflow.action.close-modal-name")' v-model='closeModal'></v-switch>

        <v-row>
          <v-col>
            <v-switch
              :label='$t("workflow.action.run-python-code")'
              @change='codeIsToggled'
              v-model='codeIsShown'
            ></v-switch>
          </v-col>
          <v-col>
            <v-text-field
              :hint='$t("workflow.action.action-db-hint")'
              :label='$t("workflow.action.action-db-name")'
              :rules='dbNameRules'
              data-cy='action-db-name'
              v-if='codeIsShown'
              v-model='dbName'
            />
          </v-col>
        </v-row>

        <v-row v-if='codeIsShown'>
          <v-col class='code-header-left'>{{$t("workflow.action.code-header")}}</v-col>
          <v-col class='code-header-right'>{{$t("workflow.action.code-hint")}}</v-col>
        </v-row>

        <div id='monacoDock' v-if='codeIsShown'>
          <div :class='monacoWrapperClass' id='monacoWrapper'>
            <monaco-editor
              :options='monacoOptions'
              @editorDidMount='initMonaco'
              class='editor'
              data-cy='code-editor'
              language='python'
              ref='editor'
              theme='vs-dark'
              v-model='code'
            ></monaco-editor>
          </div>
        </div>

        <v-row>
          <v-col>
            <v-switch
              :label='$t("workflow.action.confirmation-required")'
              @change='confirmIsToggled'
              v-model='confirmIsShown'
            ></v-switch>
          </v-col>
          <v-col>
            <v-textarea
              :hint='$t("workflow.action.confirm-hint")'
              :label='$t("workflow.action.confirm-name")'
              auto-grow
              v-if='confirmIsShown'
              v-model='confirmText'
            ></v-textarea>
          </v-col>
        </v-row>

        <v-row>
          <v-col>
            <v-switch
              :label='$t("workflow.action.action-is-job")'
              @change='jobIsToggled'
              v-model='jobIsShown'
            ></v-switch>
          </v-col>
          <v-col>
            <v-select
              :items='jobPresets'
              :label='$t("workflow.action.job-preset-list")'
              @change='presetChanged'
              v-if='jobIsShown'
              v-model='currentJobPreset'
            ></v-select>
          </v-col>
        </v-row>

        <v-row v-if='jobIsShown'>
          <v-col>
            <v-text-field
              :label='$t("workflow.action.job-year")'
              :rules='rules.cronRule'
              hint='YYYY'
              v-model='jobYear'
            ></v-text-field>
          </v-col>
          <v-col>
            <v-text-field
              :label='$t("workflow.action.job-month")'
              :rules='rules.cronRule'
              hint='1-12'
              v-model='jobMonth'
            ></v-text-field>
          </v-col>
          <v-col>
            <v-text-field
              :label='$t("workflow.action.job-day")'
              :rules='rules.cronRule'
              hint='1-31'
              v-model='jobDay'
            ></v-text-field>
          </v-col>
          <v-col>
            <v-text-field
              :label='$t("workflow.action.job-week-day")'
              :rules='rules.cronRule'
              hint='0-6'
              v-model='jobWeekDay'
            ></v-text-field>
          </v-col>
          <v-col>
            <v-text-field
              :label='$t("workflow.action.job-hour")'
              :rules='rules.cronRule'
              hint='0-23'
              v-model='jobHour'
            ></v-text-field>
          </v-col>
          <v-col>
            <v-text-field
              :label='$t("workflow.action.job-min")'
              :rules='rules.cronRule'
              hint='0-59'
              v-model='jobMin'
            ></v-text-field>
          </v-col>
        </v-row>

        <v-row v-if='jobIsShown'>
          <v-col>
            <v-btn :disabled='jobIsRunning' text>
              <i class='fas fa-play'></i>
              &nbsp;{{$t("workflow.action.job-play")}}
            </v-btn>
            <v-btn :disabled='jobIsRunning == false' class='ml-8' text>
              <i class='fas fa-stop'></i>
              &nbsp;
              {{$t("workflow.action.job-stop")}}
            </v-btn>
          </v-col>
          <v-col>
            <b class='status play'>{{$t("workflow.action.job-running")}}</b>
            <b class='status'>{{$t("workflow.action.job-stopped")}}</b>
          </v-col>
        </v-row>

        <br />
        <div class='actions'>
          <v-btn @click='updateAction' data-cy='update-action-btn' small>
            <i class='fas fa-pencil-alt'></i>
            &nbsp; {{$t("workflow.action.settings-update-btn")}}
          </v-btn>

          <v-btn @click='openIconPicker' data-cy='icon-btn' small text>
            <i :class='iconClass' key='formIcon'></i>
            &nbsp; {{$t("workflow.action.icon-btn")}}
          </v-btn>

          <v-btn @click='deleteAction' color='error' data-cy='delete-action-btn' small text>
            <i class='fas fa-trash-alt'></i>
            &nbsp; {{$t("workflow.action.settings-delete-btn")}}
          </v-btn>
        </div>

        <modal adaptive height='auto' name='action-icon' scrollable width='800px'>
          <TheIconPicker :icon='icon' @choosed='ChangeIconAndCloseModal' />
        </modal>
      </v-container>
    </v-form>
  </div>
</template>

<script>
import TheIconPicker from '@/components/AdminHome/TheIconPicker.vue';
import MonacoEditor from 'vue-monaco';
import * as monaco from 'monaco-editor';

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
      monacoOptions: null,
      confirmText: null,
      closeModal: null,
      icon: null,
      valid: false,
      currentGuid: null,
      nameRules: [
        v => !!v || this.$t('workflow.action.action-name-required'),
        v => v.length <= 255 || this.$t('common.lenght-error', { num: 255 })
      ],
      dbName: '',
      dbNameRules: [
        v => v.length <= 127 || this.$t('common.lenght-error', { num: 127 }),
        v =>
          /^([a-z0-9]+)*([A-Z][a-z0-9]*)*$/.test(v) ||
          this.$t('workflow.action.db-name-error')
      ],
      fullScreenMode: false,
      codeIsShown: false,
      confirmIsShown: false,
      jobIsShown: false,
      jobYear: null,
      jobMonth: null,
      jobDay: null,
      jobWeekDay: null,
      jobHour: null,
      jobMin: null,
      rules: {
        cronRule: [
          v => !v || /^[0-9\*,-/]+$/.test(v) || this.$t('common.error')
        ]
      },
      jobPresets: [
        { text: this.$t('workflow.action.job-preset-once'), value: 'once' },
        { text: this.$t('workflow.action.job-preset-5min'), value: '5min' },
        { text: this.$t('workflow.action.job-preset-30min'), value: '30min' },
        { text: this.$t('workflow.action.job-preset-2h'), value: '2h' },
        { text: this.$t('workflow.action.job-preset-range'), value: 'range' },
        { text: this.$t('workflow.action.job-preset-1d'), value: '1d' },
        {
          text: this.$t('workflow.action.job-preset-1w-range'),
          value: '1w-range'
        },
        { text: this.$t('workflow.action.job-preset-1w'), value: '1w' },
        { text: this.$t('workflow.action.job-preset-1m'), value: '1m' },
        { text: this.$t('workflow.action.job-preset-1q'), value: '1q' }
      ],
      currentJobPreset: null,
      jobIsRunning: false
    };
  },
  computed: {
    monacoWrapperClass() {
      if (this.fullScreenMode) return 'monacoWrapperFullScreen';
      return 'monacoWrapper';
    },
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
    noAxRoles() {
      if (this.axRoles && this.axRoles.length > 0) return false;
      return true;
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
    // https://microsoft.github.io/monaco-editor/api/interfaces/monaco.editor.ieditorconstructionoptions.html
    this.monacoOptions = {
      automaticLayout: true,
      rulers: [80]
    };

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
    initMonaco(editor) {
      editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KEY_S, () => {
        this.updateAction(false);
      });
      editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => {
        if (!this.fullScreenMode) {
          this.fullScreenMode = true;
          document.body.appendChild(document.getElementById('monacoWrapper'));
          setTimeout(() => {
            editor.layout();
          }, 100);
        } else {
          this.fullScreenMode = false;
          const dock = document.getElementById('monacoDock');
          dock.appendChild(document.getElementById('monacoWrapper'));
          setTimeout(() => {
            editor.layout();
          }, 100);
        }
      });
    },
    getData(actions) {
      const actionData = actions.find(element => element.guid === this.guid);
      if (actionData) {
        this.name = actionData.name;
        this.dbName = actionData.dbName;
        this.code = actionData.code;
        this.confirmText = actionData.confirmText;
        this.closeModal = actionData.closeModal;
        this.icon = actionData.icon;

        if (this.confirmText) this.confirmIsShown = true;

        if (!this.code) this.code = '';
        else this.codeIsShown = true;

        if (!this.dbName) this.dbName = '';
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
    updateAction(doClose = true) {
      if (this.$refs.form.validate()) {
        const data = {
          guid: this.guid,
          name: this.name,
          dbName: this.dbName,
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
          this.$emit('updateAction', doClose);
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
    },
    codeIsToggled() {
      if (this.code && this.codeIsShown == false) {
        this.$dialog.message.error(
          this.$t('workflow.action.delete-code-first')
        );
        setTimeout(() => {
          this.codeIsShown = true;
        }, 5);
      }
    },
    confirmIsToggled() {
      if (this.confirmText && this.confirmIsShown == false) {
        this.$dialog.message.error(
          this.$t('workflow.action.delete-confirm-first')
        );
        setTimeout(() => {
          this.confirmIsShown = true;
        }, 5);
      }
    },
    jobIsToggled() {
      if (this.jobIsRunning && this.jobIsShown == false) {
        this.$dialog.message.error(this.$t('workflow.action.stop-job-first'));
        setTimeout(() => {
          this.jobIsShown = true;
        }, 5);
      }
    },
    setJobValues(year, month, day, weekDay, hour, min) {
      this.jobYear = year;
      this.jobMonth = month;
      this.jobDay = day;
      this.jobWeekDay = weekDay;
      this.jobHour = hour;
      this.jobMin = min;
    },
    presetChanged() {
      // year, month, day, weekDay, hour, min
      if (this.currentJobPreset == 'once')
        this.setJobValues('2040', '1', '25', '*', '15', '20');
      if (this.currentJobPreset == '5min')
        this.setJobValues('*', '*', '*', '*', '*', '*/5');
      if (this.currentJobPreset == '30min')
        this.setJobValues('*', '*', '*', '*', '*', '*/30');
      if (this.currentJobPreset == '2h')
        this.setJobValues('*', '*', '*', '*', '*/2', '0');
      if (this.currentJobPreset == 'range')
        this.setJobValues('*', '*', '*', '*', '9-17', '0');
      if (this.currentJobPreset == '1d')
        this.setJobValues('*', '*', '*', '*', '8', '0');
      if (this.currentJobPreset == '1w-range')
        this.setJobValues('*', '*', '*', '0-4', '0', '0');
      if (this.currentJobPreset == '1w')
        this.setJobValues('*', '*', '*', '2', '0', '0');
      if (this.currentJobPreset == '1m')
        this.setJobValues('*', '*', '1', '*', '0', '0');
      if (this.currentJobPreset == '1q')
        this.setJobValues('*', '*/3', '1', '*', '0', '0');
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
  height: 100%;
}

.monacoWrapper {
  width: 100%;
  height: 600px;
}

.monacoWrapperFullScreen {
  position: absolute;
  width: 100%;
  height: 100%;
  max-width: 100%;
  max-height: 100%;
  top: 0px;
  left: 0px;
  z-index: 200;
  overflow: hidden;
}
.pro-promo {
  font-weight: bolder;
}

.code-header-left {
  font-weight: bold;
}
.code-header-right {
  color: #888888;
  text-align: right;
  font-size: 12px;
}

.status {
  font-size: 24px;
}

.play {
  color: #4caf50;
}
</style>
