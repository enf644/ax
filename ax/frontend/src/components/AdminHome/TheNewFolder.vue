<template>
  <div class='new-form-card'>
    <h1>Creating new folder</h1>
    <v-btn @click='closeModal' class='close' color='black' flat icon>
      <font-awesome-icon class='close-ico' icon='times'/>
    </v-btn>
    <br>
    <v-form ref='form' v-model='valid'>
      <v-text-field :rules='nameRules' label='Form name' ref='nameField' required v-model='name'/>
    </v-form>
    <br>
    <v-btn @click='createNewFolder' small>
      <font-awesome-icon icon='folder'/>&nbsp; Create folder
    </v-btn>
  </div>
</template>

<script>
export default {
  name: 'the-new-folder',
  data() {
    return {
      valid: false,
      name: '',
      nameRules: [
        v => !!v || 'Name is required',
        v => v.length <= 255 || 'Must be less than 255 characters'
      ]
    };
  },
  computed: {
    modalMustClose() {
      return this.$store.state.home.modalMustClose;
    }
  },
  watch: {
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
    createNewFolder() {
      if (this.$refs.form.validate()) {
        this.$store.dispatch('home/createFolder', {
          name: this.name
        });
      } else {
        this.$log.info('NOT VALID');
      }
    },
    closeModal() {
      this.$emit('created');
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
