<template>
  <div>
    <span class='label'>{{name}}</span>
    <v-checkbox
      :disabled='isReadonly'
      :error-messages='errorFlag'
      :key='item.value'
      :label='item.text'
      :value='item.value'
      @change='isValid'
      v-for='item in items'
      v-model='currentValue'
    ></v-checkbox>

    <hr :class='errorClass' />
    <transition enter-active-class='animated shake' leave-active-class='animated fadeOut'>
      <span class='required-error' v-show='errorString'>{{errorString}}</span>
    </transition>
    <span class='hint' v-show='this.options.hint'>{{this.options.hint}} &nbsp;</span>
  </div>
</template>

<script>
export default {
  name: 'AxCheckboxList',
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
    currentValue: null,
    errors: []
  }),
  computed: {
    items() {
      if (this.options.items) return JSON.parse(this.options.items);

      const defaultItems = [
        { text: 'One', value: 'one_value' },
        { text: 'Two', value: 'two_value' },
        { text: 'Three', value: 'three_value' }
      ];
      return defaultItems;
    },
    errorFlag() {
      if (this.errors.length > 0) return [''];
      return [];
    },
    errorString() {
      if (this.errors.length > 0) return this.errors.join('. ');
      return false;
    },
    errorClass() {
      if (this.errors.length > 0) return 'hr-error';
      return null;
    }
  },
  watch: {
    currentValue(newValue) {
      this.$emit('update:value', newValue);
    }
  },
  created() {
    this.currentValue = this.value;
    if (!this.currentValue) this.currentValue = [];
  },
  methods: {
    isValid() {
      if (this.requiredIsValid()) return true;
      return false;
    },
    requiredIsValid() {
      this.errors = [];
      if (this.isRequired) {
        if (!this.currentValue || this.currentValue.length == 0) {
          this.errors.push(this.options.required_text);
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
.label {
  font-size: 13px;
  color: #000;
  opacity: 0.54;
}
.required-error {
  margin-top: '5px' !important;
  color: #b71c1c;
  font-size: 12px;
  margin-right: 15px;
}
.hr-error {
  border-color: #b71c1c;
}
.hint {
  color: rgba(0, 0, 0, 0.54);
  font-size: 12px;
  margin-top: '5px' !important;
}
</style>
