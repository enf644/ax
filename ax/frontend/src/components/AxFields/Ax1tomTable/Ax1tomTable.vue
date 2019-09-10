<template>
  <div>
    <div
      :class='getErrorClass'
      :style='{height: this.options.inline_height + "px"}'
      v-if='options.inline_grid'
    >
      <AxGrid
        :filtered='currentValue'
        :form='options.form'
        :grid='options.inline_grid'
        :guids='currentValue'
        :title='name'
        :update_time='updateTime'
        @openSelectDialog='openGridModal()'
        @tomRemove='clearValue'
        cy-data='tomTableGrid'
        tom_inline_mode
      ></AxGrid>

      <span class='hint' v-show='this.options.hint'>{{this.options.hint}} &nbsp;</span>

      <transition enter-active-class='animated shake' leave-active-class='animated fadeOut'>
        <span class='required-error' v-show='errorString'>{{errorString}}</span>
      </transition>
    </div>
    <v-alert
      :value='true'
      type='warning'
      v-if='!this.options.grid'
    >{{locale("common.no-field-settings-error", {name: this.name})}}</v-alert>

    <modal :name='`tom-form-${this.modalGuid}`' adaptive height='auto' scrollable width='70%'>
      <v-card>
        <v-btn :ripple='false' @click='closeModal' class='close' color='black' icon text>
          <i class='fas fa-times close-ico'></i>
        </v-btn>
        <AxForm :db_name='options.form' :guid='activeItemGuid' no_margin></AxForm>
      </v-card>
    </modal>

    <modal :name='`tom-grid-${this.modalGuid}`' adaptive height='auto' scrollable width='70%'>
      <v-card>
        <v-btn :ripple='false' @click='closeModal' class='close' color='black' icon text>
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
import i18n from '@/locale';
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
    value: null,
    isRequired: null
  },
  data: () => ({
    currentValue: null,
    errors: [],
    loading: false,
    search: null,
    axItems: [],
    formIcon: null,
    formName: null,
    modalGuid: null,
    activeItemGuid: null,
    updateTime: null
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
    },
    errorString() {
      if (this.errors.length > 0) return this.errors.join('. ');
      return false;
    },
    getErrorClass() {
      if (this.errors.length > 0) return 'div-error';
      return null;
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
    value(newValue) {
      this.currentValue = newValue;
      this.updateTime = Date.now();
    }
  },
  created() {
    if (this.value) {
      this.currentValue = this.value;
    }
    this.updateTime = Date.now();
    this.modalGuid = uuid4();
  },
  methods: {
    locale(key) {
      return i18n.t(key);
    },
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
    clearValue(guidToRemove) {
      this.currentValue = [
        ...this.currentValue.filter(guid => guid !== guidToRemove)
      ];
      this.updateTime = Date.now();
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
    onGridSelected(items) {
      this.currentValue = items;
      this.updateTime = Date.now();
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
.required-error {
  margin-top: '5px' !important;
  color: #b71c1c;
  font-size: 12px;
}
.hint {
  color: rgba(0, 0, 0, 0.54);
  font-size: 12px;
  margin-top: '5px' !important;
}
.div-error {
  border: 1px solid #b71c1c;
}
</style>
