<template>
  <span>
    <slot v-show='false'></slot>
    <v-chip :key='item.guid' class='chip' v-for='item in axUsers'>
      <v-avatar class='grey' left>
        <i :class='`ax-chip-icon fas fa-user`'></i>
      </v-avatar>
      {{item.shortName}}
    </v-chip>
  </span>
</template>

<script>
import gql from 'graphql-tag';
import apolloClient from '@/apollo.js';

export default {
  name: 'AxUsersColumn',
  props: {
    options_json: null
  },
  data: () => ({
    value: [],
    options: null,
    axUsers: []
  }),
  computed: {
    guidsString() {
      if (!this.value || this.value.length == 0) return null;
      const userList = JSON.parse(this.value);
      const retObj = {
        items: userList
      };
      return JSON.stringify(retObj);
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
</style>
