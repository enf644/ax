<template>
  <div class='users-wrapper'>
    <h1>{{locale("types.AxApproval.add-users-header")}}</h1>
    <v-btn :ripple='false' @click='closeModal()' class='close' color='black' icon text>
      <i class='fas fa-times close-ico'></i>
    </v-btn>
    <v-autocomplete
      :hide-no-data='hideNoData'
      :items='axUsers'
      :label='locale("types.AxApproval.add-users-label")'
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
        <v-chip @click:close='clearValue(item)' class='chip' close>
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

    <br />
    <v-btn @click='addReviwers()' small>
      <i class='fas fa-user-plus'></i>
      &nbsp;
      {{locale("types.AxApproval.add-users-btn")}}
    </v-btn>
  </div>
</template>

<script>
// import CatalogItem from '@/components/CatalogItem.vue';
import i18n from '@/locale';
import gql from 'graphql-tag';
import apolloClient from '@/apollo.js';
import uuid4 from 'uuid4';

export default {
  name: 'AxApprovalAddReviwers',
  components: {},
  data: () => ({
    isSequence: false,
    currentValue: null,
    errors: [],
    loading: false,
    search: null,
    axUsers: []
  }),
  computed: {
    hideNoData() {
      if (this.search && this.search.length >= 2) return false;
      return true;
    },
    guidsString() {
      if (!this.currentValue || this.currentValue.length == 0) return null;
      const retObj = {
        items: this.currentValue
      };
      return JSON.stringify(retObj);
    }
  },
  watch: {
    search(newValue) {
      if (newValue && newValue !== this.select) this.doQuicksearch();
    }
  },
  mounted() {},
  methods: {
    locale(key) {
      return i18n.t(key);
    },
    doQuicksearch() {
      const searchQuery = this.search;
      if (searchQuery.length < 2) return false;
      this.loadData();
      return true;
    },
    isValid() {
      this.search = null;
    },
    loadData() {
      if (!this.search) return false;

      const SEARCH_USERS = gql`
        query($updateTime: String, $guids: String, $searchString: String) {
          onlyUsers(
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
          this.axUsers = data.data.onlyUsers;
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
          this.$log.error(
            `Error in AxApprovalAddReviewrs -> loadData gql => ${error}`
          );
          this.$dialog.message.error(`${error}`);
        });

      return true;
    },
    closeModal() {
      this.$emit('close');
    },
    addReviwers() {
      const realUsers = [];
      this.axUsers.forEach(user => {
        if (this.currentValue.includes(user.guid)) realUsers.push(user);
      });

      const retValue = {
        users: realUsers,
        isSequence: this.isSequence
      };
      this.$emit('selected', retValue);
    }
  }
};
</script>

<style scoped>
.users-wrapper {
  padding: 25px;
}
.close {
  position: absolute;
  right: 10px;
  top: 10px;
}
.close-ico {
  font-size: 20px;
}
</style>