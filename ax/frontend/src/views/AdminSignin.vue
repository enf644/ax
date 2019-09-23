<template>
  <!-- <div class='wrapper'> -->
  <v-app fill-height id='app' standalone>
    <v-card class='card'>
      <v-form @submit='doSignIn' ref='form' v-model='valid'>
        <div class='logo-div'>
          <img class='logo' src='@/assets/small_axe.png' />
        </div>
        <br />
        <v-text-field
          :label='locale("users.signin-email")'
          :rules='[rules.required, rules.isEmail]'
          v-model='email'
        ></v-text-field>

        <v-text-field
          :label='locale("users.signin-password")'
          :rules='[rules.required]'
          type='password'
          v-model='password'
        ></v-text-field>
        <br />
        <v-btn @click='doSignIn()'>
          <i class='fas fa-sign-in-alt'></i>
          &nbsp;{{$t("users.do-sign-in")}}
        </v-btn>
      </v-form>
    </v-card>
  </v-app>
  <!-- </div> -->
</template>

<script>
// import CatalogItem from '@/components/CatalogItem.vue';
import axios from 'axios';
// import { setTokens, getAccessToken } from '@/apollo';
import store from '@/store';
import { getAxHostProtocol } from '@/misc';

export default {
  name: 'AdminSignin',
  components: {},
  data() {
    return {
      valid: true,
      email: 'enf644@gmail.com',
      password: '123',
      showPass: false,
      rules: {
        required: value => !!value || this.locale('common.field-required'),
        isEmail: value => {
          const pattern = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
          return pattern.test(value) || this.locale('common.invalid-email');
        }
      }
    };
  },
  computed: {},
  watch: {},
  mounted() {},
  methods: {
    locale(key) {
      return this.$t(key);
    },
    doSignIn() {
      if (this.$refs.form.validate()) {
        const host = getAxHostProtocol();
        console.log(host);
        axios
          .post(`${host}/api/auth`, {
            email: this.email,
            password: this.password
          })
          .then(response => {
            this.$log.info(response);
            store.commit('auth/setTokens', {
              access: response.data.access_token,
              refresh: response.data.refresh_token
            });
            this.$cookies.set('access_token', response.data.access_token);
            this.$cookies.set('refresh_token', response.data.refresh_token);

            let url = `/deck`;
            if (this.$store.state.home.redirectFromUrl) {
              url = this.$store.state.home.redirectFromUrl;
            }
            this.$router.push({ path: url });

            // setTimeout(() => {
            //   console.log(window.$cookies.get('access_token'));
            // }, 400);
          })
          .catch(error => {
            this.$log.error(error);
          });
      }
    }
  }
};
</script>

<style scoped>
.card {
  width: 400px;
  padding: 50px;
  margin: auto;
  margin-top: 5%;
}

.logo-div {
  width: 100%;
  text-align: center;
}
.wrapper {
  background: #f8f8f8;
}
</style>
