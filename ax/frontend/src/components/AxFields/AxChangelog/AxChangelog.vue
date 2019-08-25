<template>
  <div>
    <h3>{{name}}</h3>
    <div :key='item.timestamp' class='changelog-row' v-for='item in currentValue'>
      {{ $d(getDate(item.timestamp), 'normal') }} : [AnonUser] :
      <b>{{ item.action.name }}</b>
      &nbsp;
      <i class='fas fa-arrow-right'></i>
      &nbsp;
      <span v-html='getModifiedFields(item)'></span>
    </div>
    <b v-if='this.currentValue.length == 0'>{{locale("types.AxChangelog.no-records")}}</b>
  </div>
</template>

<script>
import i18n from '@/locale';

export default {
  name: 'AxChangelog',
  props: {
    name: null,
    dbName: null,
    tag: null,
    options: null,
    value: null,
    isRequired: null
  },
  data: () => ({
    currentValue: null,
    errors: []
  }),
  watch: {
    value(newValue) {
      this.currentValue = newValue;
      if (!newValue) this.currentValue = [];
    }
  },
  created() {
    this.currentValue = this.value;
    if (!this.value) this.currentValue = [];
  },
  methods: {
    locale(key) {
      return i18n.t(key);
    },
    isValid() {
      return true;
    },
    getDate(timestamp) {
      const dt = new Date(timestamp * 1000);
      return dt;
    },
    getModifiedFields(item) {
      const fieldNames = [];
      item.changed_fields.forEach(field => {
        fieldNames.push(field.name);
      });
      if (fieldNames.length > 0) return fieldNames.join(', ');

      return '<i class="far fa-window-close"></i>';
    }
  }
};
</script>

<style scoped>
.changelog-row {
  padding-top: 5px;
}
</style>
