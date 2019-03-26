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
      <v-flex xs8>
        <v-text-field
          :hint='$t("home.new-form.tom-label-hint")'
          :label='$t("home.new-form.tom-label")'
          data-cy='new-form-tom'
          required
          v-if='this.$route.params.db_name'
          v-model='tomLabel'
        />
      </v-flex>
      <v-flex offset-xs1 xs3>
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
    <v-btn @click='createNewForm' data-cy='new-form-btn' small v-if='!this.$route.params.db_name'>
      <i class='fas fa-plus'></i>
      &nbsp; {{$t("home.new-form.create-btn")}}
    </v-btn>
    <v-btn @click='updateForm' data-cy='new-form-btn' small v-if='this.$route.params.db_name'>
      <i class='fas fa-pencil-alt'></i>
      &nbsp; {{$t("home.new-form.update-btn")}}
    </v-btn>
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
        v => /^[a-zA-Z\d][\w]{0,127}$/.test(v)
          || this.$t('home.new-form.db-name-valid-letters')
      ],
      tomLabel: null,
      icon: null
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
      if (this.guid) return this.$t('home.new-form.toast-form-updated');
      return this.$t('home.new-form.toast-form-created');
    }
  },
  watch: {
    dbNameIsAvalible() {
      this.$refs.form.validate();
    },
    modalMustClose(newValue) {
      if (newValue === true) {
        this.$dialog.message.success(
          `<i class="fas fa-check"></i> &nbsp ${this.okToast}`
        );
        this.closeModal();
      }
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
    resetDbNameValid() {
      this.dbName = this.dbName.toLowerCase();
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
  text-align: center;
}
</style>
