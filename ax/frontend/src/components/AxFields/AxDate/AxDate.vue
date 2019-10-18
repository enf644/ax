<template>
  <v-menu
    :close-on-content-click='false'
    :nudge-right='40'
    min-width='290px'
    offset-y
    transition='scale-transition'
    v-model='menu2'
  >
    <template v-slot:activator='{ on }'>
      <v-col>
        <v-row>
          <v-text-field
            :disabled='isReadonly'
            :error-messages='errors'
            :hint='options.hint'
            :label='name'
            @change='setDate()'
            v-mask='currentMask'
            v-model='visibleDate'
          ></v-text-field>
          <v-btn class='open-icon' icon v-on='on'>
            <i class='far fa-calendar-alt'></i>
          </v-btn>
        </v-row>
      </v-col>
    </template>
    <v-date-picker :disabled='isReadonly' @input='menu2 = false' v-model='pickerDate'></v-date-picker>
  </v-menu>
</template>

<script>
import i18n from '../../../locale.js';

export default {
  name: 'AxDate',
  props: {
    name: null,
    dbName: null,
    tag: null,
    options: null,
    value: null,
    isRequired: null,
    isReadonly: null
  },
  data: () => ({
    visibleDate: null,
    pickerDate: null,
    currentValue: null,
    errors: [],
    menu2: false,
    currentMask: '####-##-##'
  }),
  computed: {},
  watch: {
    currentValue(newValue) {
      this.$emit('update:value', newValue);
    },
    pickerDate(newValue) {
      // console.log(newValue);
      this.currentValue = this.strToTimestamp(newValue);
      this.visibleDate = newValue;
    },
    value(newValue) {
      if (newValue != this.currentValue) {
        this.currentValue = newValue;
        this.visibleDate = this.timestampToStr(newValue);
        this.pickerDate = this.timestampToStr(newValue);
      }
    },
    options(newValue) {
      this.loadFirstValue();
    }
  },
  created() {
    this.loadFirstValue();
  },
  methods: {
    loadFirstValue() {
      if (this.options && this.options.defaultNow && !this.value) {
        this.currentValue = Math.round(new Date().getTime() / 1000);
        this.visibleDate = this.timestampToStr(this.currentValue);
        this.pickerDate = this.timestampToStr(this.currentValue);
      } else {
        this.currentValue = this.value;
        this.visibleDate = this.timestampToStr(this.value);
        this.pickerDate = this.timestampToStr(this.value);
      }
    },
    setDate() {
      console.log(this.visibleDate);
      this.currentValue = this.strToTimestamp(this.visibleDate);
      this.pickerDate = this.visibleDate;
    },
    strToTimestamp(dateStr) {
      if (dateStr) return Math.round(new Date(dateStr).getTime() / 1000);
      return null;
    },
    timestampToStr(timestamp) {
      if (timestamp) {
        let date = new Date(timestamp * 1000),
          month = '' + (date.getMonth() + 1),
          day = '' + date.getDate(),
          year = date.getFullYear();

        if (month.length < 2) month = '0' + month;
        if (day.length < 2) day = '0' + day;

        return [year, month, day].join('-');
      }
      return null;
    },
    isValid() {
      if (this.requiredIsValid()) return true;
      return false;
    },
    requiredIsValid() {
      if (this.isRequired) {
        if (!this.currentValue || this.currentValue.length === 0) {
          let msg = i18n.t('common.field-required');
          if (this.options.required_text) msg = this.options.required_text;
          this.errors.push(msg);
          return false;
        }
        this.errors = [];
        return true;
      }
      return true;
    }
  }
};
</script>

<style scoped>
.open-icon {
  margin-top: 20px;
}
</style>
