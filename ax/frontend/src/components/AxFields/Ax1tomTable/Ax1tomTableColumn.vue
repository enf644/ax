<template>
  <span>
    <slot v-show='false'></slot>
    <v-chip :key='item.guid' class='chip' v-for='item in axItems'>
      <v-avatar class='grey'>
        <i :class='`ax-chip-icon fas fa-${formIcon}`'></i>
      </v-avatar>
      {{item.axLabel}}
    </v-chip>
  </span>
</template>

<script>
import gql from 'graphql-tag';
import apolloClient from '../../../apollo.js';

export default {
  name: 'Ax1tomTableColumn',
  props: {
    options_json: null
  },
  data: () => ({
    value: [],
    options: null,
    axItems: [],
    formIcon: null
  }),
  computed: {
    guidsString() {
      if (!this.value || this.value.length === 0) return null;
      const retObj = {
        items: this.value
      };
      return JSON.stringify(retObj);
    },
    viewDbName() {
      if (this.options.grid) return this.options.form + this.options.grid;
      return this.options.form;
    }
  },
  mounted() {
    const columnValue = this.$slots.default[0].elm.innerText;
    if (columnValue && columnValue !== 'null') this.value.push(columnValue);
    this.$slots.default[0].elm.innerText = '';

    if (this.options_json) {
      this.options = JSON.parse(this.options_json);
      this.loadData();
    }
  },
  methods: {
    loadData() {
      if (!this.value || this.value.length === 0) return false;

      const GRID_DATA = gql`
        query ($updateTime: String, $quicksearch: String, $guids: String, $dbName: String!) {
          ${this.viewDbName} (
            updateTime: $updateTime, 
            quicksearch: $quicksearch,
            guids: $guids
          ) {
              guid
              axLabel
          }
          form (dbName: $dbName) {
              name
              icon
          }          
        }
      `;

      apolloClient
        .query({
          query: GRID_DATA,
          variables: {
            updateTime: Date.now(),
            quicksearch: null,
            guids: this.guidsString,
            dbName: this.options.form
          }
        })
        .then(data => {
          this.axItems = data.data[this.viewDbName];
          this.formIcon = data.data.form.icon;
        })
        .catch(error => {
          this.$log.error(
            `Error in Ax1tomTableColumn => loadData apollo client => ${error}`
          );
        });

      return true;
    }
  }
};
</script>

<style scoped>
</style>
