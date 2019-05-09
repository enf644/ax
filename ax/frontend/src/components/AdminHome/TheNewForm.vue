<template>
  <div class='new-form-card'>
    <h1>{{modalHeader}}</h1>
    <v-btn :ripple='false' @click='closeModal' class='close' color='black' flat icon>
      <i class='fas fa-times close-ico'></i>
    </v-btn>
    <br>
    <v-form @submit='createNewForm' ref='form' v-model='valid'>
      <v-text-field
        :label='$t("home.new-form.form-name")'
        :rules='nameRules'
        data-cy='new-form-name'
        ref='nameField'
        required
        v-model='name'
      />
      <v-text-field
        :label='$t("home.new-form.form-database-name")'
        :rules='dbNameRules'
        @input='resetDbNameValid'
        data-cy='new-form-db-name'
        required
        v-model='dbName'
      ></v-text-field>
    </v-form>

    <v-layout row>
      <v-flex xs3>
        <v-btn
          @click='openIconPicker'
          data-cy='new-form-icon-btn'
          small
          v-if='this.$route.params.db_name'
        >
          <i :class='[iconClass]' key='formIcon'></i>
          &nbsp; {{$t("home.new-form.change-icon")}}
        </v-btn>
        <modal adaptive height='auto' name='new-form-icon' scrollable width='800px'>
          <TheIconPicker :icon='icon' @choosed='ChangeIconAndCloseModal'/>
        </modal>
      </v-flex>
      <v-flex offset-xs1 xs8>
        <v-text-field
          :hint='$t("home.new-form.tom-label-hint")'
          :label='$t("home.new-form.tom-label")'
          data-cy='new-form-tom'
          required
          v-if='this.$route.params.db_name'
          v-model='tomLabel'
        />
      </v-flex>
    </v-layout>

    <br>
    <div class='chip-preview' v-if='this.$route.params.db_name'>
      <span>{{$t("home.new-form.chip-preview")}}:</span>
      &nbsp;
      <v-chip>
        <v-avatar class='grey darken-2'>
          <i :class='["ax-chip-icon", iconClass]'></i>
        </v-avatar>
        {{tomLabel}}
      </v-chip>
    </div>

    <br>
    <div class='actions'>
      <v-btn @click='createNewForm' data-cy='new-form-btn' small v-if='!this.$route.params.db_name'>
        <i class='fas fa-plus'></i>
        &nbsp; {{$t("home.new-form.create-btn")}}
      </v-btn>
      <v-btn @click='updateForm' data-cy='update-form-btn' small v-if='this.$route.params.db_name'>
        <i class='fas fa-pencil-alt'></i>
        &nbsp; {{$t("home.new-form.update-btn")}}
      </v-btn>
      <v-btn
        @click='deleteForm'
        color='error'
        data-cy='delete-form-btn'
        flat
        small
        v-if='this.$route.params.db_name'
      >
        <i class='fas fa-trash-alt'></i>
        &nbsp; {{$t("home.new-form.delete-btn")}}
      </v-btn>
    </div>
  </div>
</template>

<script>
import TheIconPicker from '@/components/AdminHome/TheIconPicker.vue';

export default {
  name: 'the-new-form',
  props: {
    guid: {
      type: String,
      default: null
    }
  },
  components: { TheIconPicker },
  data() {
    return {
      valid: false,
      name: '',
      nameRules: [
        v => !!v || this.$t('home.new-form.name-required'),
        v => v.length <= 255 || this.$t('common.lenght-error', { num: 255 })
      ],
      dbName: '',
      dbNameRules: [
        v => !!v || this.$t('home.new-form.db-name-required'),
        v => v.length <= 127 || this.$t('common.lenght-error', { num: 127 }),
        v => (v && this.dbNameIsAvalible)
          || this.$t('home.new-form.db-name-not-avalible'),
        v => /^((\d)|([A-Z0-9][a-z0-9]+))*([A-Z])?$/.test(v)
          || this.$t('home.new-form.db-name-valid-letters')
      ],
      tomLabel: null,
      icon: null,
      isDeleteAction: false
      // /^((\d)|([A-Z0-9][a-z0-9]+))*([A-Z])?$/
      // /^[a-zA-Z\d][\w]{0,127}$/
    };
  },
  computed: {
    dbNameIsAvalible() {
      return this.$store.state.home.dbNameIsAvalible;
    },
    modalMustClose() {
      return this.$store.state.home.modalMustClose;
    },
    dbNameChanged() {
      return this.$store.state.home.dbNameChanged;
    },
    iconClass() {
      return `fas fa-${this.icon}`;
    },
    modalHeader() {
      return this.guid == null
        ? this.$t('home.new-form.header')
        : this.$t('home.new-form.update-header');
    },
    okToast() {
      let toastMessage = null;
      let toastIcon = null;

      if (this.guid) {
        toastMessage = this.$t('home.new-form.toast-form-updated');
        toastIcon = 'check';
      } else if (this.isDeleteAction) {
        toastMessage = this.$t('home.new-form.toast-form-deleted');
        toastIcon = 'trash-alt';
      } else {
        toastMessage = this.$t('home.new-form.toast-form-created');
        toastIcon = 'trash-alt';
      }
      return `<i class="fas fa-${toastIcon}"></i> &nbsp ${toastMessage}`;
    }
  },
  watch: {
    dbName(newValue) {
      if (newValue) {
        if (newValue[0] !== newValue[0].toUpperCase()) {
          const firstLetter = newValue.charAt(0).toUpperCase();
          this.dbName = firstLetter + newValue.slice(1);
        }
      }
    },
    dbNameIsAvalible() {
      this.$refs.form.validate();
    },
    modalMustClose() {
      this.$dialog.message.success(this.okToast);
      if (this.isDeleteAction) {
        this.$router.push({ path: '/admin/home' });
        this.isDeleteAction = false;
      }
      this.closeModal();
    },
    dbNameChanged(newValue) {
      if (newValue) {
        this.$router.push({ path: `/admin/${newValue}/form` });
        this.$store.commit('home/setModalMustClose', true);
        this.$store.commit('home/setDbNameChanged', null);
      }
    }
  },
  mounted() {
    this.$refs.nameField.focus();
    if (this.guid) {
      const form = this.$store.state.home.forms.find(x => x.guid === this.guid);
      if (form) {
        this.name = form.name;
        this.dbName = form.dbName;
        this.icon = form.icon;
        this.tomLabel = form.tomLabel;
      } else this.$log.error('Could not Ax form folder in store');
    }
  },
  methods: {
    createNewForm(e) {
      e.preventDefault();
      if (this.$refs.form.validate()) {
        this.$store.dispatch('home/createForm', {
          name: this.name,
          dbName: this.dbName
        });
      }
    },
    updateForm(e) {
      e.preventDefault();
      this.$store.dispatch('home/updateForm', {
        guid: this.guid,
        name: this.name,
        dbName: this.dbName,
        icon: this.icon,
        tomLabel: this.tomLabel
      });
    },
    async deleteForm(e) {
      e.preventDefault();
      const res = await this.$dialog.confirm({
        text: this.$t('home.new-form.delete-confirm', { name: this.name }),
        actions: {
          false: this.$t('common.confirm-no'),
          true: {
            text: this.$t('common.confirm-yes'),
            color: 'red'
          }
        }
      });

      if (res) {
        this.isDeleteAction = true;
        this.$store
          .dispatch('home/deleteForm', {
            guid: this.guid
          })
          .then(() => {
            // this.$store.commit('form/setFormData', null);
            this.$store.dispatch('form/getFormData', {
              dbName: this.dbName,
              guid: this.guid
            });
          });
      }
    },
    resetDbNameValid() {
      if (this.dbNameIsAvalible === false) {
        this.$store.commit('home/setDbNameIsAvalible', true);
        this.$refs.form.validate();
      }
    },
    closeModal() {
      this.$emit('created');
      this.$store.commit('home/setDbNameIsAvalible', true);
      this.$store.commit('home/setModalMustClose', false);
    },
    openIconPicker(e) {
      e.preventDefault();
      this.$modal.show('new-form-icon');
    },
    ChangeIconAndCloseModal(newIcon) {
      if (newIcon) this.icon = newIcon;
      this.$modal.hide('new-form-icon');
    }
  }
};
</script>

<style scoped>
.new-form-card {
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
.chip-preview {
  text-align: left;
}
.actions {
  justify-content: space-between;
  display: flex;
}
.delete-div {
  border: 2px solid #db4437;
  padding: 30px;
  color: #db4437;
}
</style>
