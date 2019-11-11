<template>
  <div class='new-form-card'>
    <h1>{{formTitle}}</h1>
    <v-btn :ripple='false' @click='closeModal' class='close' color='black' icon text>
      <i class='fas fa-times close-ico'></i>
    </v-btn>
    <br />
    <v-form @submit='doSomething' ref='form' v-model='valid'>
      <v-text-field
        :label='$t("home.new-folder.folder-name")'
        :rules='nameRules'
        data-cy='new-folder-name'
        ref='nameField'
        required
        v-model='name'
      />
    </v-form>
    <br />
    <div class='actions'>
      <v-btn @click='doSomething' data-cy='new-folder-btn' small>
        <i class='far fa-folder'></i>
        &nbsp; {{buttonLabel}}
      </v-btn>

      <v-btn @click='openCreateAppModal' small text v-if='guid'>
        <i class='fas fa-store'></i>
        &nbsp; {{$t("marketplace.open-create-modal")}}
      </v-btn>

      <v-btn
        @click='deleteFolder'
        color='error'
        data-cy='new-folder-delete-btn'
        small
        text
        v-if='guid'
      >
        <i class='far fa-trash-alt'></i>
        &nbsp; {{$t("home.new-folder.delete-btn")}}
      </v-btn>
    </div>
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
        v => !!v || this.$t('home.new-folder.name-required'),
        v => v.length <= 255 || this.$t('common.lenght-error', { num: 255 })
      ],
      buttonLabel: this.$t('home.new-folder.create-btn'),
      formTitle: this.$t('home.new-folder.create-title'),
      toastMessage: `<i class="fas fa-check"></i> &nbsp ${this.$t(
        'home.new-folder.create-toast'
      )}`,
      isDeleteAction: false
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
        if (this.isDeleteAction) {
          this.isDeleteAction = false;
          this.$dialog.message.success(
            `<i class="fas fa-trash-alt"></i> &nbsp ${this.$t(
              'home.new-folder.delete-toast'
            )}`
          );
        } else this.$dialog.message.success(this.toastMessage);
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

      this.buttonLabel = this.$t('home.new-folder.update-btn');
      this.formTitle = this.$t('home.new-folder.update-title');
      this.toastMessage = `<i class="fas fa-check"></i> &nbsp ${this.$t(
        'home.new-folder.update-toast'
      )}`;
    }
    this.$refs.nameField.focus();
  },
  methods: {
    doSomething(e) {
      e.preventDefault();
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
    async deleteFolder() {
      const res = await this.$dialog.confirm({
        text: this.$t('home.new-folder.delete-confirm'),
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
        this.$store.dispatch('home/deleteFolder', {
          guid: this.guid
        });
      }
    },
    closeModal() {
      this.$emit('created');
      setTimeout(() => {
        this.$store.commit('home/setModalMustClose', false);
      }, 50);
    },
    openCreateAppModal() {
      this.$emit('openAppModal', this.guid);
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
.actions {
  justify-content: space-between;
  display: flex;
}
</style>
