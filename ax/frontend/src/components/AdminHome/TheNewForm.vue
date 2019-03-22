<template>
  <div class='new-form-card'>
    <h1>{{$t("home.new-form.header")}}</h1>
    <v-btn @click='closeModal' class='close' color='black' flat icon>
      <i class='fas fa-times close-ico'></i>
    </v-btn>
    <br>
    <v-form @submit='createNewForm' ref='form' v-model='valid'>
      <v-text-field
        :label='$t("home.new-form.form-name")'
        :rules='nameRules'
        ref='nameField'
        required
        v-model='name'
      />
      <v-text-field
        :label='$t("home.new-form.form-database-name")'
        :rules='dbNameRules'
        @input='resetDbNameValid'
        required
        v-model='dbName'
      ></v-text-field>
    </v-form>
    <br>
    <v-btn @click='createNewForm' small>
      <i class='fas fa-plus'></i>
      &nbsp; {{$t("home.new-form.create-btn")}}
    </v-btn>
  </div>
</template>

<script>
export default {
  name: 'the-new-form',
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
      ]
    };
  },
  computed: {
    dbNameIsAvalible() {
      return this.$store.state.home.dbNameIsAvalible;
    },
    modalMustClose() {
      return this.$store.state.home.modalMustClose;
    }
  },
  watch: {
    dbNameIsAvalible() {
      this.$refs.form.validate();
    },
    modalMustClose(newValue) {
      if (newValue === true) {
        this.$dialog.message.success(
          `<i class="fas fa-check"></i> &nbsp ${this.$t(
            'home.new-form.toast-form-created'
          )}`
        );
        this.closeModal();
      }
    }
  },
  mounted() {
    this.$refs.nameField.focus();
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
</style>
