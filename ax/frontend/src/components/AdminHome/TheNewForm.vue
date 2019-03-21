<template>
  <div class='new-form-card'>
    <h1>Creating new Ax Form</h1>
    <v-btn @click='closeModal' class='close' color='black' flat icon>
      <font-awesome-icon class='close-ico' icon='times'/>
    </v-btn>
    <br>
    <v-form ref='form' v-model='valid'>
      <v-text-field :rules='nameRules' label='Form name' ref='nameField' required v-model='name'/>
      <v-text-field
        :rules='dbNameRules'
        @input='resetDbNameValid'
        label='Database table name'
        required
        v-model='dbName'
      ></v-text-field>
    </v-form>
    <br>
    <v-btn @click='createNewForm' small>
      <font-awesome-icon icon='plus'/>&nbsp; Create ax form
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
        v => !!v || 'Name is required',
        v => v.length <= 255 || 'Must be less than 255 characters'
      ],
      dbName: '',
      dbNameRules: [
        v => !!v || 'Database name is required',
        v => v.length <= 255 || 'Must be less than 255 characters',
        v => (v && this.dbNameIsAvalible)
          || 'Database name is not avalible. Please choose enother.',
        v => /[a-zA-Z\d][\w]{0,127}$/.test(v)
          || 'Use only latin letters, numbers and _ symbol'
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
        this.closeModal();
      }
    }
  },
  mounted() {
    this.$refs.nameField.focus();
  },
  methods: {
    createNewForm() {
      if (this.$refs.form.validate()) {
        this.$store.dispatch('home/createForm', {
          name: this.name,
          dbName: this.dbName
        });
      } else {
        this.$log.info('NOT VALID');
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
