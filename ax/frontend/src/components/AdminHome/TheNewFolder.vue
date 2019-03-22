<template>
  <div class='new-form-card'>
    <h1>{{formTitle}}</h1>
    <v-btn @click='closeModal' class='close' color='black' flat icon>
      <font-awesome-icon class='close-ico' icon='times'/>
    </v-btn>
    <br>
    <v-form ref='form' v-model='valid'>
      <v-text-field :rules='nameRules' label='Form name' ref='nameField' required v-model='name'/>
    </v-form>
    <br>
    <v-btn @click='doSomething' small>
      <font-awesome-icon icon='folder'/>
      &nbsp; {{buttonLabel}}
    </v-btn>
  </div>
</template>

<script>
export default {
  name: 'the-new-folder',
  props: {
    guid: {
      type: String,
      default: null
    }
  },
  data() {
    return {
      valid: false,
      name: '',
      nameRules: [
        v => !!v || 'Name is required',
        v => v.length <= 255 || 'Must be less than 255 characters'
      ],
      buttonLabel: 'Create folder',
      formTitle: 'Creating new folder'
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
    if (this.guid) {
      const folder = this.$store.state.home.forms.find(
        x => x.guid === this.guid
      );
      if (folder) this.name = folder.name;
      else this.$log.error('Could not find folder in store');
      this.buttonLabel = 'Update folder';
      this.formTitle = 'Updating folder';
    }
    this.$refs.nameField.focus();
  },
  methods: {
    doSomething() {
      if (this.guid) this.updateFolder();
      else this.createNewFolder();
    },
    createNewFolder() {
      if (this.$refs.form.validate()) {
        this.$store.dispatch('home/createFolder', {
          name: this.name
        });
      }
    },
    updateFolder() {
      if (this.$refs.form.validate()) {
        this.$store.dispatch('home/updateFolder', {
          guid: this.guid,
          name: this.name
        });
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
