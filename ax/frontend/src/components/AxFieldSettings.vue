<template>
  <div class='card'>
    <v-form @submit.prevent='updateSettings' ref='form' v-model='valid'>
      <h1>{{header}}</h1>
      <v-btn :ripple='false' @click='closeModal' class='close' color='black' icon text>
        <i class='fas fa-times close-ico'></i>
      </v-btn>
      <br />

      <v-container>
        <v-row>
          <v-col class='mr-3'>
            <v-switch
              :label='locale("form.is-required")'
              data-cy='is-required-input'
              v-if='showRequired'
              v-model='isRequired'
              v-show='isNotVirtual'
            ></v-switch>
          </v-col>
          <v-col class='ml-3'>
            <v-switch
              :disabled='isWholeRowIsDisabled'
              :label='locale("form.is-whole-row")'
              data-cy='whole-row'
              v-if='showWholeRow'
              v-model='isWholeRow'
            ></v-switch>
          </v-col>
        </v-row>
        <v-row>
          <v-col class='mr-3'>
            <v-text-field
              :label='locale("form.required-text-label")'
              data-cy='required'
              v-if='showRequiredText'
              v-model='reuiredText'
              v-show='isNotVirtual'
            ></v-text-field>
          </v-col>
          <v-col class='ml-3'>
            <v-text-field
              :label='locale("form.hint-setting-label")'
              data-cy='hint'
              v-if='showHint'
              v-model='hint'
              v-show='isNotVirtual'
            ></v-text-field>
          </v-col>
        </v-row>
      </v-container>

      <slot></slot>
      <v-btn
        :ripple='false'
        @click.prevent='updateSettings'
        data-cy='save-settings-btn'
        small
        type='submit'
      >
        <i class='fas fa-save'></i>
        &nbsp; {{locale("form.field-settings-submit")}}
      </v-btn>
    </v-form>
  </div>
</template>

<script>
import i18n from '../locale.js';
import store from '../store';

export default {
  name: 'AxFieldSettings',
  props: {
    guid: null, // this is AxField guid
    options: null, // this is passed from field settings component
    privateOptions: null, // this is passed from field settings component
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
      field: null,
      valid: true
    };
  },
  computed: {
    addedOptions() {
      const options = { ...this.options };
      options.required_text = this.reuiredText;
      options.hint = this.hint;
      return options;
    },
    isNotVirtual() {
      if (this.field && this.field.fieldType.isVirtual) return false;
      if (this.field && this.field.fieldType.isReadonly) return false;
      return true;
    }
  },
  watch: {},
  mounted() {
    this.field = store.state.form.fields.find(
      field => field.guid === this.guid
    );
    this.isRequired = this.field.isRequired;
    this.isWholeRow = this.field.isWholeRow;
    this.reuiredText = this.options.required_text;
    this.hint = this.options.hint;

    if (this.field.fieldType.isAlwaysWholeRow) {
      this.isWholeRowIsDisabled = true;
    }

    this.header = i18n.t('form.field-settings-title', {
      name: this.field.name
    });
  },
  methods: {
    locale(key) {
      return i18n.t(key);
    },
    updateSettings() {
      if (this.$refs.form.validate()) {
        const payload = {};
        payload.guid = this.field.guid;
        payload.name = this.field.name;
        payload.dbName = this.field.dbName;
        payload.isRequired = this.isRequired;
        payload.isWholeRow = this.isWholeRow;
        payload.optionsJson = JSON.stringify(this.addedOptions);
        payload.privateOptionsJson = JSON.stringify(this.privateOptions);
        store.dispatch('form/updateField', payload);
        this.$emit('closed');
      }
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
