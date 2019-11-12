<template>
  <div>
    <b>{{name}}</b>
    <transition enter-active-class='animated shake' leave-active-class='animated fadeOut'>
      <div class='required-error' v-show='errorString'>{{errorString}}</div>
    </transition>
    <div class='hint' v-show='this.options.hint'>{{this.options.hint}} &nbsp;</div>
    <table cellspacing='0'>
      <tr>
        <td></td>
        <td
          :class='{ highlite: highlighedX==items.x.indexOf(xitem) }'
          :key='xitem'
          class='x-label'
          v-for='xitem in items.x'
        >{{xitem}}</td>
      </tr>
      <tr :key='yitem' v-for='yitem in items.y'>
        <td :class='{ highlite: highlighedY==items.y.indexOf(yitem) }' class='y-label'>{{yitem}}</td>
        <td :key='xitem' class='radio-cell' v-for='xitem in items.x'>
          <v-radio-group v-model='currentValue[items.y.indexOf(yitem)]'>
            <v-radio
              :disabled='isReadonly'
              :value='items.x.indexOf(xitem)'
              @click='setValue(items.y.indexOf(yitem), items.x.indexOf(xitem))'
              @mouseleave='turnOffHightlite()'
              @mouseover='highlite(items.y.indexOf(yitem), items.x.indexOf(xitem))'
            ></v-radio>
          </v-radio-group>
        </td>
      </tr>
    </table>
  </div>
</template>

<script>
export default {
  name: 'AxRadioSurvey',
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
    errors: [],
    highlighedX: null,
    highlighedY: null
  }),
  computed: {
    items() {
      if (this.options.items) return JSON.parse(this.options.items);

      const defaultItems = {
        x: ['one', 'two', 'three'],
        y: ['Bad', 'Normal', 'Good']
      };
      return defaultItems;
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
    currentValue(newValue, oldValue) {
      this.$emit('update:value', newValue);
    }
  },
  created() {
    this.currentValue = this.value;
    if (!this.currentValue) this.currentValue = [];
  },
  methods: {
    setValue(yIndex, xIndex) {
      this.$set(this.currentValue, yIndex, xIndex);
    },
    highlite(yIndex, xIndex) {
      this.highlighedX = xIndex;
      this.highlighedY = yIndex;
    },
    turnOffHightlite() {
      this.highlighedX = null;
      this.highlighedY = null;
    },
    isValid() {
      this.errors = [];
      if (this.requiredIsValid()) return true;
      return false;
    },
    requiredIsValid() {
      if (this.isRequired) {
        console.log(this.currentValue);
        if (
          !this.currentValue ||
          this.currentValue.length == 0 ||
          this.currentValue.includes(null) ||
          this.currentValue.includes('null') ||
          this.items.y.length > Object.values(this.currentValue).length
        ) {
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
.radio-cell {
  text-align: center;
  padding-left: 16px;
}
.x-label {
  text-align: center;
  border-bottom: 1px solid #ccc;
  transition: 0.5s;
}
.y-label {
  text-align: left;
  padding-right: 15px;
  padding-top: 15px;
  border-right: 1px solid #ccc;
  transition: 0.5s;
}
.highlite {
  color: #82b1ff;
}
.required-error {
  margin-top: '5px' !important;
  color: #b71c1c;
  font-size: 12px;
  margin-right: 15px;
}
.hint {
  color: rgba(0, 0, 0, 0.54);
  font-size: 12px;
  margin-top: '5px' !important;
}
</style>
