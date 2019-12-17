<template>
  <div class='password-wrapper'>
    <h2>{{locale("users.change-password")}}</h2>
    <div v-if='is_new' class='warining-temp'>{{locale("users.change-password-user-warning")}}</div>
    <v-form @submit.prevent='updateUser' ref='form' v-model='valid'>
      <v-container>
        <v-row>
          <v-col>
            <v-text-field
              :hint='locale("users.modal-password-hint")'
              :label='locale("users.modal-password")'
              :rules='[rules.required, rules.password]'
              type='password'
              v-model='password'
            ></v-text-field>
          </v-col>
          <v-col>
            <v-text-field
              :label='locale("users.modal-re-password")'
              :rules='[rules.required, rules.rePassword]'
              type='password'
              v-model='rePassword'
            ></v-text-field>
          </v-col>
        </v-row>
        <v-row>
          <v-btn
            @click.prevent='updateUser'
            data-cy='update-user-btn'
            small
            type='submit'
            v-show='guid'
          >
            <i class='fas fa-pencil-alt'></i>
            &nbsp; {{locale("users.change-password")}}
          </v-btn>
        </v-row>
      </v-container>
    </v-form>
  </div>
</template>

<script>
// import CatalogItem from '@/components/CatalogItem.vue';
import i18n from '@/locale';
import gql from 'graphql-tag';
import apolloClient from '@/apollo.js';

export default {
  name: 'ThePasswordChange',
  components: {},
  props: {
    guid: null,
    is_new: null
  },
  data() {
    return {
      password: null,
      rePassword: null,
      valid: false,
      rules: {
        required: value => !!value || this.locale('common.field-required'),
        password: value => {
          if (value == null) return true;
          const reg = /^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])[0-9a-zA-Z]{8,}$/;
          return reg.test(value) || this.locale('users.invalid-new-password');
        },
        rePassword: value => {
          if (this.password == value) return true;
          return this.locale('users.re-password-invalid');
        }
      }
    };
  },
  computed: {},
  watch: {},
  mounted() {},
  methods: {
    locale(key) {
      return i18n.t(key);
    },
    updateUser() {
      if (this.$refs.form.validate()) {
        console.log('do update');
        const CHANGE_PASSWORD = gql`
          mutation($guid: String!, $password: String!) {
            changeUserPassword(guid: $guid, password: $password) {
              user {
                guid
                email
              }
              ok
            }
          }
        `;

        apolloClient
          .mutate({
            mutation: CHANGE_PASSWORD,
            variables: {
              guid: this.guid,
              password: this.password
            }
          })
          .then(data => {
            console.log('updated!');
            const msg = this.locale('users.change-password-toast');
            this.$dialog.message.success(
              `<i class="fas fa-pencil-alt"></i> &nbsp ${msg}`
            );
            this.$emit('close');
          })
          .catch(error => {
            console.log(`Error in updateUser gql => ${error}`);
            this.$dialog.message.error(`${error}`);
          });
      }
    }
  }
};
</script>

<style scoped>
.password-wrapper {
  padding: 25px;
}
.warining-temp {
  white-space: normal;
}
</style>