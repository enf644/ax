<template>
  <div class='card'>
    <h1>{{$t("grids.settings-header")}}</h1>
    <v-btn :ripple='false' @click='closeModal' class='close' color='black' icon text>
      <i class='fas fa-times close-ico'></i>
    </v-btn>
    <br />
    <v-form @submit.prevent='updateGrid' ref='form' v-model='valid'>
      <v-text-field
        :label='$t("grids.grid-name")'
        :rules='nameRules'
        data-cy='grid-name'
        ref='nameField'
        required
        v-model='name'
      />
      <v-text-field
        :hint='$t("grids.grid-db-name-hint")'
        :label='$t("grids.grid-db-name")'
        :rules='dbNameRules'
        @input='checkDbName'
        data-cy='grid-db-name'
        required
        v-model='dbName'
      ></v-text-field>

      <v-switch
        :label='this.$t("grids.is-default-view")'
        cy-data='is-default-view'
        v-model='isDefaultView'
        v-show='!isDefaultViewSaved'
      ></v-switch>

      <div v-show='isDefaultViewSaved'>
        <i class='far fa-star'></i>
        &nbsp;
        {{$t("grids.grid-is-default-view")}}
      </div>
      <br />

      <div class='actions'>
        <v-btn @click.prevent='updateGrid' data-cy='update-grids-btn' small type='submit'>
          <i class='fas fa-pencil-alt'></i>
          &nbsp; {{$t("grids.settings-update-btn")}}
        </v-btn>

        <v-btn
          @click='deleteGrid'
          color='error'
          data-cy='delete-grid-btn'
          small
          text
          v-show='isNotDefaultView'
        >
          <i class='fas fa-trash-alt'></i>
          &nbsp; {{$t("grids.settings-delete-btn")}}
        </v-btn>
      </div>
    </v-form>
  </div>
</template>

<script>
export default {
  name: 'TheGridSettings',
  data() {
    return {
      guid: null,
      name: '',
      dbName: '',
      isDefaultView: null,
      isDefaultViewSaved: null,
      valid: false,
      dbNameIsAvalible: true,
      nameRules: [
        v => !!v || this.$t('grids.name-required'),
        v => v.length <= 255 || this.$t('common.lenght-error', { num: 255 })
      ],
      dbNameRules: [
        v => !!v || this.$t('grids.db-name-required'),
        v => v.length <= 127 || this.$t('common.lenght-error', { num: 127 }),
        v => (v && this.dbNameIsAvalible)
          || this.$t('home.new-form.db-name-not-avalible'),
        v => /^((\d)|([A-Z0-9][a-z0-9]+))*([A-Z])?$/.test(v)
          || this.$t('home.new-form.db-name-valid-letters')
      ]
    };
  },
  computed: {
    isNotDefaultView() {
      return !this.isDefaultView;
    },
    defaultGridDbName() {
      const defaultGrid = this.$store.state.form.grids.find(
        grid => grid.isDefaultView === true
      );
      return defaultGrid ? defaultGrid.dbName : null;
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
    }
  },
  mounted() {
    this.$refs.nameField.focus();
    this.guid = this.$store.state.grids.guid;
    this.name = this.$store.state.grids.name;
    this.isDefaultView = this.$store.state.grids.isDefaultView;
    this.isDefaultViewSaved = this.$store.state.grids.isDefaultView;
    this.dbName = this.$store.state.grids.dbName;
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
      this.$emit('updated');
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
