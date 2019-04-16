<template>
  <div class='card'>
    <h1>{{header}}</h1>
    <v-btn :ripple='false' @click='closeModal' class='close' color='black' flat icon>
      <i class='fas fa-times close-ico'></i>
    </v-btn>
    <br>
    <v-layout align-left row wrap>
      <v-flex xs5>
        <v-switch
          :label='locale("form.is-required")'
          cy-data='is-required-input'
          v-if='showRequired'
          v-model='isRequired'
        ></v-switch>
      </v-flex>
      <v-flex offset-xs2 xs5>
        <v-switch
          :disabled='isWholeRowIsDisabled'
          :label='locale("form.is-whole-row")'
          cy-data='whole-row'
          v-if='showWholeRow'
          v-model='isWholeRow'
        ></v-switch>
      </v-flex>
      <v-flex xs12>
        <v-text-field
          :label='locale("form.required-text-label")'
          cy-data='required'
          v-if='showRequiredText'
          v-model='reuiredText'
        ></v-text-field>
      </v-flex>
      <v-flex xs12>
        <v-text-field
          :label='locale("form.hint-setting-label")'
          cy-data='hint'
          v-if='showHint'
          v-model='hint'
        ></v-text-field>
      </v-flex>
    </v-layout>
    <slot></slot>
    <v-btn :ripple='false' @click='updateSettings' data-cy='save-settings-btn' small>
      <i class='fas fa-save'></i>
      &nbsp; {{locale("form.field-settings-submit")}}
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
    options: null,
    showHint: {
      type: Boolean,
      default: true
    },
    showRequired: {
      type: Boolean,
      default: true
    },
    showRequiredText: {
      type: Boolean,
      default: true
    },
    showWholeRow: {
      type: Boolean,
      default: true
    }
  },
  data() {
    return {
      isRequired: false,
      isRequiredLocale: null,
      isWholeRow: false,
      isWholeRowIsDisabled: false,
      isWholeRowLocale: null,
      requiredTextLabel: null,
      reuiredText: null,
      hint: null,
      header: null,
      submit: null,
      field: null
    };
  },
  computed: {
    addedOptions() {
      const options = { ...this.options };
      options.required_text = this.reuiredText;
      options.hint = this.hint;
      return options;
    }
  },
  watch: {},
  mounted() {
    this.field = store.state.form.fields.find(
      field => field.guid === this.guid
    );
    this.isRequired = this.field.isRequired;
    this.isWholeRow = this.field.isWholeRow;
    this.ReuiredText = this.options.required_text;
    this.hint = this.options.hint;

    if (this.field.fieldType.isAlwaysWholeRow) {
      this.isWholeRowIsDisabled = true;
    }

    this.header = i18n.t('form.field-settings-title', {
      name: this.field.name
    });
    // this.submit = i18n.tc('form.field-settings-submit');
    // this.isWholeRowLocale = i18n.tc('form.is-whole-row');
    // this.isRequiredLocale = i18n.tc('form.is-required');
    // this.requiredTextLabel = i18n.t('form.required-text-label');
  },
  methods: {
    locale(key) {
      return i18n.t(key);
    },
    updateSettings() {
      const payload = {};
      payload.guid = this.field.guid;
      payload.name = this.field.name;
      payload.dbName = this.field.dbName;
      payload.isRequired = this.isRequired;
      payload.isWholeRow = this.isWholeRow;
      payload.optionsJson = JSON.stringify(this.addedOptions);
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
