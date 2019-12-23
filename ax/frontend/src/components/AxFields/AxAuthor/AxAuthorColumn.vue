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
  name: 'AxSingleUserColumn',
  props: {
    options_json: null
  },
  data: () => ({
    value: [],
    options: null,
    axUsers: []
  }),
  computed: {},
  mounted() {
    const columnValue = this.$slots.default[0].elm.innerText;
    if (columnValue && columnValue !== 'null') this.value = [columnValue];
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
            emails: this.value,
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
</style>
