<template>
  <div>
    <div
      :class='getErrorClass'
      :style='{height: this.options.inline_height + "px"}'
      v-if='options.inline_grid'
    >
      <AxGrid
        :form='options.form'
        :grid='options.inline_grid'
        :guids='childGuids'
        :title='name'
        :tom_disabled='isReadonly'
        :update_time='updateTime'
        @added='getChildGuids'
        cy-data='tomTableGrid'
        tom_children_mode
        v-if='childrenLoaded'
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
  </div>
</template>

<script>
import i18n from '@/locale';
import uuid4 from 'uuid4';
import AxForm from '@/components/AxForm.vue';
import AxGrid from '@/components/AxGrid.vue';
import apolloClient from '@/apollo';
import gql from 'graphql-tag';

export default {
  name: 'Ax1to1Children',
  props: {
    name: null,
    dbName: null,
    tag: null,
    options: null,
    value: null,
    isRequired: null,
    isReadonly: null,
    formGuid: null,
    rowGuid: null,
    fieldGuid: null
  },
  data: () => ({
    currentValue: [],
    errors: [],
    loading: false,
    search: null,
    axItems: [],
    formIcon: null,
    formName: null,
    modalGuid: null,
    activeItemGuid: null,
    updateTime: null,
    childGuids: [],
    childrenLoaded: false
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
  watch: {},
  created() {
    this.modalGuid = uuid4();
  },
  mounted() {
    this.getChildGuids();
  },
  methods: {
    locale(key) {
      return i18n.t(key);
    },
    openFormModal(item) {
      if (
        this.options.enableFormModal ||
        this.options.enableFormModal === undefined
      ) {
        this.activeItemGuid = item.guid;
        this.$modal.show(`tom-form-${this.modalGuid}`);
      }
    },
    closeModal() {
      this.$modal.hide(`tom-form-${this.modalGuid}`);
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
        return true;
      }
      return true;
    },
    getChildGuids() {
      if (!this.rowGuid) {
        this.childrenLoaded = true;
        return false;
      }

      const CHILD_GUIDS = gql`
        query($fieldGuid: String!, $rowGuid: String!, $updateTime: String!) {
          to1References(
            fieldGuid: $fieldGuid
            rowGuid: $rowGuid
            updateTime: $updateTime
          ) {
            guid
          }
        }
      `;

      const vars = {
        fieldGuid: this.fieldGuid,
        rowGuid: this.rowGuid,
        updateTime: Date.now()
      };
      apolloClient
        .query({
          query: CHILD_GUIDS,
          variables: vars
        })
        .then(data => {
          const to1References = data.data.to1References;
          this.childGuids = [];
          if (to1References && to1References.length > 0) {
            to1References.forEach(element => {
              this.childGuids.push(element.guid);
            });
          }
          this.childrenLoaded = true;
          this.updateTime = Date.now();
        })
        .catch(error => {
          this.$log.error(`Error in getChildGuids gql => ${error}`);
          this.$dialog.message.error(`${error}`);
        });
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
