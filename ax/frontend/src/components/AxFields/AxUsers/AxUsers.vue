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
      item-value='email'
      multiple
      ref='users_autocomplete'
      v-model='currentValue'
    >
      <template v-slot:selection='{ item, selected }'>
        <v-chip
          :close='isReadonly == false'
          @click:close='clearValue(item)'
          @click.stop='openUserModal(item)'
          class='chip'
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

    <modal :name='`ax-user-${this.modalGuid}`' adaptive height='auto' scrollable>
      <v-card>
        <v-btn :ripple='false' @click='closeModal' class='close' color='black' icon text>
          <i class='fas fa-times close-ico'></i>
        </v-btn>
        <div class='user-modal-div'>
          <b>{{currentShortName}}</b>
          <br />
          <a :href='currentEmail'>{{currentEmail}}</a>
        </div>
      </v-card>
    </modal>
  </div>
</template>

<script>
import i18n from '@/locale';
import gql from 'graphql-tag';
import apolloClient from '@/apollo.js';
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
    axUsers: [],
    modalGuid: null,
    currentShortName: null,
    currentEmail: null
  }),
  components: {},
  computed: {
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
    this.modalGuid = uuid4();
    if (this.value) {
      this.currentValue = this.value;
      this.loadData();
    }
  },
  methods: {
    openUserModal(item) {
      if (item) {
        this.currentShortName = item.shortName;
        this.currentEmail = item.email;
        this.$modal.show(`ax-user-${this.modalGuid}`);
      }
    },
    closeModal() {
      this.$modal.hide(`ax-user-${this.modalGuid}`);
    },
    locale(key) {
      return i18n.t(key);
    },
    clearValue(axItem) {
      this.currentValue = [
        ...this.currentValue.filter(email => email !== axItem.email)
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
        query($updateTime: String, $emails: String, $searchString: String) {
          onlyUsers(
            updateTime: $updateTime
            emails: $emails
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
            emails: this.currentValue,
            updateTime: Date.now()
          }
        })
        .then(data => {
          this.axUsers = data.data.onlyUsers;
          // We re-create values incase some of items were deleted or permission was denied.
          const checkedValues = [];
          this.axUsers.forEach(element => {
            if (
              this.currentValue &&
              this.currentValue.includes(element.email)
            ) {
              checkedValues.push(element.email);
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
.user-modal-div {
  padding: 30px;
}
</style>
