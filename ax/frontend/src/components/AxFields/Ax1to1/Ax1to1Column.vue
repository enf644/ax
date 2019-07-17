<template>
  <span>
    <slot v-show='false'></slot>
    <v-chip :key='item.guid' class='chip' v-for='item in axItems'>
      <v-avatar class='grey'>
        <i :class='`ax-chip-icon fas fa-${formIcon}`'></i>
      </v-avatar>
      {{item.axLabel}}
    </v-chip>
    <!-- <modal :name='`tom-form-${this.modalGuid}`' adaptive height='auto' scrollable width='70%'>
      <v-card>
        <v-btn :ripple='false' @click='closeModal' class='close' color='black' flat icon>
          <i class='fas fa-times close-ico'></i>
        </v-btn>
        <AxForm :db_name='optionsForm' :guid='activeItemGuid' no_margin></AxForm>
      </v-card>
    </modal>-->
  </span>
</template>

<script>
import uuid4 from 'uuid4';
import gql from 'graphql-tag';
import apolloClient from '../../../apollo.js';
import AxForm from '@/components/AxForm.vue';

export default {
  name: 'Ax1to1Column',
  props: {
    options_json: null
  },
  components: { AxForm },
  data: () => ({
    value: [],
    options: null,
    axItems: [],
    formIcon: null,
    modalGuid: null,
    activeItemGuid: null
  }),
  computed: {
    optionsForm() {
      if (!this.options) return null;
      return this.options.form;
    },
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
    this.modalGuid = uuid4();
    const columnValue = this.$slots.default[0].elm.innerText;
    if (columnValue && columnValue !== 'null') this.value.push(columnValue);
    this.$slots.default[0].elm.innerText = '';

    if (this.options_json) {
      this.options = JSON.parse(this.options_json);
      this.loadData();
    }
  },
  methods: {
    openFormModal(item) {
      if (
        this.options.enableFormModal
        || this.options.enableFormModal === undefined
      ) {
        this.activeItemGuid = item.guid;
        this.$modal.show(`tom-form-${this.modalGuid}`);
      }
    },
    closeModal() {
      this.$modal.hide(`tom-form-${this.modalGuid}`);
    },
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
            `Error in Ax1to1Column => loadData apollo client => ${error}`
          );
        });

      return true;
    }
  }
};
</script>

<style scoped>
</style>
