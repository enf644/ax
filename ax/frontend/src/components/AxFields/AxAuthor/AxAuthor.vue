<template>
  <div class='nobr'>
    <v-autocomplete
      :items='axUsers'
      :label='name'
      :loading='loading'
      chips
      dense
      disabled
      hide-selected
      item-text='shortName'
      item-value='email'
      multiple
      ref='users_autocomplete'
      v-model='currentValue'
    >
      <template v-slot:selection='{ item, selected }'>
        <v-chip @click.stop='openFormModal(item)' class='chip' close>
          <v-avatar class='grey mr-2' left>
            <i :class='`ax-chip-icon fas fa-user`'></i>
          </v-avatar>
          {{item.shortName}}
        </v-chip>
      </template>

      <template v-slot:append>
        <v-btn disabled icon>
          <i class='fas fa-user-tag'></i>
        </v-btn>
      </template>
    </v-autocomplete>
  </div>
</template>

<script>
import i18n from '@/locale';
import gql from 'graphql-tag';
import apolloClient from '@/apollo.js';
import uuid4 from 'uuid4';

export default {
  name: 'AxAuthor',
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
    hideNoData() {
      if (this.search && this.search.length >= 2) return false;
      return true;
    }
  },
  watch: {
    value(newValue) {
      if (newValue == null) this.currentValue = null;
      else if (
        newValue &&
        (!this.currentValue || !this.currentValue.includes(newValue))
      ) {
        this.currentValue = [];
        this.currentValue.push(newValue);
        this.loadData();
      }
    }
  },
  created() {
    if (this.value) {
      this.currentValue = [this.value];
      this.loadData();
    }
  },
  methods: {
    locale(key) {
      return i18n.t(key);
    },
    isValid() {
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
        })
        .catch(error => {
          this.$log.error(`Error in AxAuthor -> loadData gql => ${error}`);
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
