<template>
  <div class='card'>
    <h1>{{$t("grids.settings-header")}}</h1>
    <v-btn :ripple='false' @click='closeModal' class='close' color='black' flat icon>
      <i class='fas fa-times close-ico'></i>
    </v-btn>
    <br>
    <v-form @submit.prevent='updateGrid' ref='form' v-model='valid'>
      <v-text-field
        :label='$t("grids.grid-name")'
        data-cy='grid-name'
        ref='nameField'
        required
        v-model='name'
      />
    </v-form>
    <br>

    <h1>ACTION MODAL = {{guid}}</h1>

    <div class='actions'>
      <v-btn @click='updateGrid' data-cy='update-grids-btn' small>
        <i class='fas fa-pencil-alt'></i>
        &nbsp; {{$t("grids.settings-update-btn")}}
      </v-btn>

      <v-btn @click='deleteGrid' color='error' data-cy='delete-grid-btn' flat small>
        <i class='fas fa-trash-alt'></i>
        &nbsp; {{$t("grids.settings-delete-btn")}}
      </v-btn>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TheActionModal',
  props: {
    guid: null
  },
  data() {
    return {
      name: '',
      valid: false
    };
  },
  computed: {},
  watch: {},
  mounted() {
    this.$refs.nameField.focus();
    this.name = this.$store.state.grids.name;
  },
  methods: {
    checkDbName() {
      this.$store.state.form.grids.forEach(grid => {
        if (grid.dbName === this.dbName && grid.guid !== this.guid) {
          this.dbNameIsAvalible = false;
        }
      });
    },
    updateGrid() {
      if (this.$refs.form.validate()) {
        const data = {
          guid: this.guid,
          name: this.name,
          dbName: this.dbName,
          isDefaultView: this.isDefaultView
        };
        this.$store.dispatch('grids/updateGrid', data).then(() => {
          const msg = this.$t('grids.grid-updated-toast');
          this.$dialog.message.success(
            `<i class="fas fa-pencil-alt"></i> &nbsp ${msg}`
          );
          this.closeModal();
        });
      }
    },
    async deleteGrid(e) {
      e.preventDefault();
      const res = await this.$dialog.confirm({
        text: this.$t('grids.grid-delete-confirm', { name: this.name }),
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
          .dispatch('grids/deleteGrid', {
            defaultGridDbName: this.defaultGridDbName
          })
          .then(() => {
            const msg = this.$t('grids.grid-deleted-toast');
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
