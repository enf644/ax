<template>
  <span class='wrap'>
    <i :class='iconClass'></i>
    <input
      @change='applyNameChange'
      @click='focusName'
      class='name-input'
      ref='nameInput'
      type='text'
      v-model='currentName'
    >
    <div id='db_div'>
      <i
        @click='openSettings'
        aria-hidden='true'
        class='fas fa-cog but hvr-pop'
        title='Open settings'
      ></i>
      <input
        @change='applyDbChange'
        @click='focusDbName'
        @keyup='preventNameError'
        class='db-input'
        ref='dbInput'
        type='text'
        v-model='currentDbName'
      >
    </div>
  </span>
</template>

<script>
// import AxFieldSettings from '@/components/AxFieldSettings.vue';
import i18n from '../../locale.js';
import store from '../../store';

export default {
  name: 'construcor-field',
  // components: { AxFieldSettings },
  props: {
    guid: null,
    name: null,
    db_name: null,
    tag: null,
    icon: null,
    options_json: null
  },
  data: () => ({
    currentName: null,
    currentDbName: null,
    component: null
  }),
  computed: {
    iconClass() {
      return `fas fa-${this.icon}`;
    },
    loader() {
      if (!this.tag) {
        return null;
      }
      return () => import(`@/components/AxFields/${this.tag}/${this.tag}Settings.vue`);
    }
  },
  watch: {
    currentDbName(newValue, oldValue) {
      // const isCorrectDbName = /^[a-zA-Z\d][\w]{0,127}$/.test(newValue);
      const isCorrectDbName = /^((\d)|([A-Z0-9][a-z0-9]+))*([A-Z])?$/.test(
        newValue
      );
      if (!isCorrectDbName) this.currentDbName = oldValue;
    }
  },
  created() {
    this.currentName = this.name;
    this.currentDbName = this.db_name;
  },
  mounted() {
    if (store.state.form.createdFieldGuid === this.guid) this.focusName();
    this.loader()
      .then(() => {
        this.component = () => this.loader();
      })
      .catch(() => {
        this.component = () => import('@/components/AxFieldSettings.vue');
      });
  },
  methods: {
    focusName() {
      setTimeout(() => {
        this.$refs.nameInput.focus();
        this.$refs.nameInput.select();
      }, 10);
    },
    focusDbName() {
      setTimeout(() => {
        this.$refs.dbInput.focus();
        this.$refs.dbInput.select();
      }, 10);
    },
    async applyNameChange() {
      store.commit('form/setIsNameChangeOperation', true);
      store
        .dispatch('form/updateField', {
          guid: this.guid,
          name: this.currentName
        })
        .then(() => {
          this.$refs.nameInput.blur();
          const msg = i18n.tc('form.update-field-toast');
          this.$dialog.message.success(
            `<i class="fas fa-check"></i> &nbsp ${msg}`
          );
        });
    },
    async applyDbChange() {
      store.commit('form/setIsNameChangeOperation', true);
      store
        .dispatch('form/updateField', {
          guid: this.guid,
          dbName: this.currentDbName
        })
        .then(() => {
          this.$refs.dbInput.blur();
          const msg = i18n.tc('form.update-field-toast');
          this.$dialog.message.success(
            `<i class="fas fa-check"></i> &nbsp ${msg}`
          );
        });
    },
    preventNameError() {},
    openSettings() {
      store.commit('form/setOpenSettingsFlag', this.guid);
    },
    closeSettings() {
      this.$modal.hide(`field-settings-${this.guid}`);
    }
  }
};
</script>

<style scoped>
#db_div {
  padding-left: 0px;
  position: absolute;
  top: 13px;
  white-space: nowrap;
  margin-left: 18px;
}
.name-input {
  margin-left: 5px;
  background: transparent;
  width: 150px;
  border: 0px;
  padding: 0px;
  font-weight: 300;
}
.name-input:focus {
  outline: none;
}
.db-input {
  margin-left: 5px;
  color: #cfcfcf;
  position: relative;
  background: transparent;
  width: 125px;
  border: 0px;
  padding: 0px;
  font-weight: 300;
}
.db-input:focus {
  color: black;
  outline: none;
}
.wrap {
  position: relative;
}
.but {
  color: #cfcfcf;
  cursor: pointer;
}
.but:hover {
  color: black !important;
}
.error {
  color: red !important;
  text-decoration: underline;
}
</style>
