<template>
  <div class='nobr'>
    <v-autocomplete
      :disabled='isReadonly'
      :error-messages='errors'
      :hide-no-data='hideNoData'
      :hint='this.options.hint'
      :items='axUsers'
      :label='name'
      :loading='loading'
      :search-input.sync='search'
      @change='isValid'
      chips
      dense
      hide-selected
      item-text='shortName'
      item-value='guid'
      multiple
      ref='users_autocomplete'
      v-model='currentValue'
    >
      <template v-slot:selection='{ item, selected }'>
        <v-chip
          @click:close='clearValue(item)'
          @click.stop='openFormModal(item)'
          class='chip'
          close
        >
          <v-avatar class='grey mr-2' left>
            <i :class='`ax-chip-icon fas fa-user`'></i>
          </v-avatar>
          {{item.shortName}}
        </v-chip>
      </template>

      <template v-slot:append>
        <v-btn disabled icon>
          <i class='fas fa-users'></i>
        </v-btn>
      </template>
    </v-autocomplete>
  </div>
</template>

<script>
import i18n from '@/locale';
import gql from 'graphql-tag';
import apolloClient from '../../../apollo.js';
import uuid4 from 'uuid4';

export default {
  name: 'AxUsers',
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
    loading: false,
    search: null,
    axUsers: []
  }),
  components: {},
  computed: {
    guidsString() {
      if (!this.currentValue || this.currentValue.length == 0) return null;
      const retObj = {
        items: this.currentValue
      };
      return JSON.stringify(retObj);
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
    value(newValue) {
      if (newValue != this.currentValue) {
        this.currentValue = newValue;
        if (this.currentValue) this.loadData();
      }
    }
  },
  created() {
    if (this.value) {
      this.currentValue = this.value;
      this.loadData();
    }
  },
  methods: {
    locale(key) {
      return i18n.t(key);
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

      const SEARCH_USERS = gql`
        query($updateTime: String, $guids: String, $searchString: String) {
          usersAndGroups(
            updateTime: $updateTime
            guids: $guids
            searchString: $searchString
          ) {
            guid
            email
            shortName
          }
        }
      `;

      apolloClient
        .query({
          query: SEARCH_USERS,
          variables: {
            searchString: this.search,
            guids: this.guidsString,
            updateTime: Date.now()
          }
        })
        .then(data => {
          this.axUsers = data.data.usersAndGroups;
          // We re-create values incase some of items were deleted or permission was denied.
          const checkedValues = [];
          this.axUsers.forEach(element => {
            if (this.currentValue && this.currentValue.includes(element.guid)) {
              checkedValues.push(element.guid);
            }
          });
          this.currentValue = [...checkedValues];
        })
        .catch(error => {
          this.$log.error(`Error in AxUsers -> loadData gql => ${error}`);
          this.$dialog.message.error(`${error}`);
        });

      return true;
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
