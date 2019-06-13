<template>
  <div class='nobr'>
    <v-autocomplete
      :error-messages='errors'
      :hide-no-data='hideNoData'
      :hint='this.options.hint'
      :items='axItems'
      :label='name'
      :loading='loading'
      :search-input.sync='search'
      @change='isValid'
      chips
      dense
      hide-selected
      item-text='axLabel'
      item-value='guid'
      multiple
      ref='tom_autocomplete'
      v-if='options.grid'
      v-model='currentValue'
    >
      <template v-slot:selection='{ item, selected }'>
        <v-chip @click='openFormModal(item)' @input='clearValue(item)' class='chip' close>
          <v-avatar class='grey'>
            <i :class='`ax-chip-icon fas fa-${formIcon}`'></i>
          </v-avatar>
          {{item.axLabel}}
        </v-chip>
      </template>

      <template v-slot:append-outer>
        <v-btn @click.prevent='openGridModal' icon>
          <i class='fas fa-link'></i>
        </v-btn>
      </template>
    </v-autocomplete>
    <v-alert
      :value='true'
      type='warning'
      v-if='!this.options.grid'
    >{{$t("common.no-field-settings-error", {name: this.name})}}</v-alert>

    <modal :name='`tom-form-${this.modalGuid}`' adaptive height='auto' scrollable width='70%'>
      <v-card>
        <v-btn :ripple='false' @click='closeModal' class='close' color='black' flat icon>
          <i class='fas fa-times close-ico'></i>
        </v-btn>
        <AxForm :db_name='options.form' :guid='activeItemGuid' no_margin></AxForm>
      </v-card>
    </modal>

    <modal :name='`tom-grid-${this.modalGuid}`' adaptive height='auto' scrollable width='70%'>
      <v-card>
        <v-btn :ripple='false' @click='closeModal' class='close' color='black' flat icon>
          <i class='fas fa-times close-ico'></i>
        </v-btn>
        <div :style='{height: this.options.height + "px"}'>
          <AxGrid
            :form='options.form'
            :grid='options.grid'
            :preselect='currentValue'
            @selected='onGridSelected'
            cy-data='to1Grid'
            tom_mode
          ></AxGrid>
        </div>
      </v-card>
    </modal>
  </div>
</template>

<script>
import i18n from '../../../locale.js';
import gql from 'graphql-tag';
import apolloClient from '../../../apollo.js';
import uuid4 from 'uuid4';
import AxForm from '@/components/AxForm.vue';
import AxGrid from '@/components/AxGrid.vue';

export default {
  name: 'Ax1tom',
  props: {
    name: null,
    dbName: null,
    tag: null,
    options: null,
    value: {
      type: Array,
      default: null
    },
    isRequired: null
  },
  data: () => ({
    currentValue: null,
    errors: [],
    loading: false,
    search: null,
    axItems: [],
    formIcon: null,
    modalGuid: null,
    activeItemGuid: null
  }),
  components: { AxForm, AxGrid },
  computed: {
    guidsString() {
      if (!this.currentValue) return null;
      const retObj = {
        items: this.currentValue
      };
      return JSON.stringify(retObj);
    },
    viewDbName() {
      if (this.options.grid) return this.options.form + this.options.grid;
      return this.options.form;
    },
    hideNoData() {
      if (this.search && this.search.length >= 2) return false;
      return true;
    }
  },
  watch: {
    currentValue(newValue) {
      if (newValue !== this.value) {
        this.$emit('update:value', newValue);
      }
    },
    search(newValue) {
      if (newValue && newValue !== this.select) this.doQuicksearch();
    },
    value(newValue, oldValue) {
      this.currentValue = newValue;
    }
  },
  created() {
    if (this.value) {
      this.currentValue = this.value;
      this.loadData();
    }
    this.modalGuid = uuid4();
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

    openGridModal() {
      this.$modal.show(`tom-grid-${this.modalGuid}`);
    },
    closeModal() {
      this.$modal.hide(`tom-form-${this.modalGuid}`);
      this.$modal.hide(`tom-grid-${this.modalGuid}`);
    },
    clearValue(axItem) {
      this.currentValue = [
        ...this.currentValue.filter(guid => guid !== axItem.guid)
      ];
    },
    isValid() {
      this.search = null;
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
    },
    doQuicksearch() {
      const searchQuery = this.search;
      if (searchQuery.length < 2) return false;
      this.loadData();
      return true;
    },
    loadData() {
      if (!this.currentValue && !this.search) return false;

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
            quicksearch: this.search,
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
            `Error in Ax1to1 => loadData apollo client => ${error}`
          );
        });

      return true;
    },
    onGridSelected(items) {
      this.currentValue = items;
      this.loadData();
      this.closeModal();
    }
  }
};
</script>

<style scoped>
.chip {
  cursor: pointer;
}
.settings-error {
  color: #f44336;
}
.nobr {
  white-space: nowrap;
}
.close {
  position: absolute;
  right: 10px;
  top: 10px;
  z-index: 100;
}
.close-ico {
  font-size: 20px;
}
</style>
