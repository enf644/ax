<template>
  <div class='card'>
    <h1>{{header}}</h1>
    <v-btn :ripple='false' @click='closeModal' class='close' color='black' flat icon>
      <i class='fas fa-times close-ico'></i>
    </v-btn>
    <br>
    <v-layout align-left row wrap>
      <v-flex xs5>
        <v-switch :label='isRequiredLocale' v-model='isRequired'></v-switch>
      </v-flex>
      <v-flex offset-xs2 xs5>
        <v-switch :disabled='isWholeRowIsDisabled' :label='isWholeRowLocale' v-model='isWholeRow'></v-switch>
      </v-flex>
    </v-layout>
    <slot></slot>
    <v-btn :ripple='false' @click='updateSettings' data-cy='save-settings-btn' small>
      <i class='fas fa-save'></i>
      &nbsp; {{submit}}
    </v-btn>
  </div>
</template>

<script>
import i18n from '../locale.js';
import store from '../store';

export default {
  name: 'AxFieldSettings',
  props: {
    guid: null,
    options: null
  },
  data() {
    return {
      isRequired: false,
      isRequiredLocale: null,
      isWholeRow: false,
      isWholeRowIsDisabled: false,
      isWholeRowLocale: null,
      header: null,
      submit: null,
      field: null
    };
  },
  computed: {},
  watch: {},
  mounted() {
    this.field = store.state.form.fields.find(
      field => field.guid === this.guid
    );
    this.isRequired = this.field.isRequired;
    this.isWholeRow = this.field.isWholeRow;

    if (this.field.fieldType.isAlwaysWholeRow) {
      this.isWholeRowIsDisabled = true;
    }

    this.header = i18n.tc('form.field-settings-title');
    this.submit = i18n.tc('form.field-settings-submit');
    this.isWholeRowLocale = i18n.tc('form.is-whole-row');
    this.isRequiredLocale = i18n.tc('form.is-required');
  },
  methods: {
    updateSettings() {
      const payload = {};
      payload.guid = this.field.guid;
      payload.name = this.field.name;
      payload.dbName = this.field.dbName;
      payload.isRequired = this.isRequired;
      payload.isWholeRow = this.isWholeRow;
      payload.optionsJson = JSON.stringify(this.options);
      store.dispatch('form/updateField', payload);
      this.$emit('closed');
    },
    closeModal() {
      this.$emit('closed');
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
</style>
