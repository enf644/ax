<template>
  <v-app fill-height id='app' standalone>
    <v-card class='card' v-if='authCookiePresent'>
      <p v-html='locale("users.already-signed")'></p>

      <v-btn @click='doLogOut()'>{{locale("home.logout")}}</v-btn>
      <br />
    </v-card>

    <v-card class='card' v-if='authCookiePresent === false'>
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
        <div class='actions'>
          <v-btn @click='doSignIn()' small>
            <i class='fas fa-sign-in-alt'></i>
            &nbsp;{{locale("users.do-sign-in")}}
          </v-btn>&nbsp;
          <v-btn @click='adminSignIn()' small>
            <i class='fas fa-tractor'></i>
            &nbsp;Admin sign in
          </v-btn>
        </div>
        <br />
        <br />
        <div class='signin-error' v-if='error'>{{error}}</div>
      </v-form>
    </v-card>
  </v-app>
</template>

<script>
import i18n from '@/locale';
import axios from 'axios';
import store from '@/store';
import { getAxHostProtocol } from '@/misc';

export default {
  name: 'AxSignIn',
  components: {},
  data() {
    return {
      valid: true,
      // email: 'default@ax-workflow.com',
      // password: 'deleteme',
      email: 'enf644@gmail.com',
      password: 'Qwerty644',
      showPass: false,
      rules: {
        required: value => !!value || this.locale('common.field-required'),
        isEmail: value => {
          const pattern = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
          return pattern.test(value) || this.locale('common.invalid-email');
        }
      },
      authCookiePresent: false,
      error: null
    };
  },
  computed: {
    currentUserShortName() {
      if (store.state.users.currentUser) {
        return store.state.users.currentUser.shortName;
      }
      return null;
    }
  },
  watch: {},
  mounted() {
    if (this.$cookies.get('access_token')) this.authCookiePresent = true;
    else this.authCookiePresent = false;
  },
  methods: {
    locale(key, values) {
      return i18n.t(key, values);
    },
    adminSignIn() {
      const host = getAxHostProtocol();
      this.email = 'default@ax-workflow.com';
      this.password = 'deleteme';
      this.doSignIn();
    },
    doSignIn() {
      this.error = null;
      if (this.$refs.form.validate()) {
        const host = getAxHostProtocol();
        axios
          .post(`${host}/api/auth`, {
            email: this.email,
            password: this.password,
            deviceGuid: window.axDeviceGuid
          })
          .then(response => {
            this.$log.info(response);
            store.commit('auth/setTokens', {
              access: response.data.access_token,
              refresh: response.data.refresh_token
            });
            this.$cookies.set('access_token', response.data.access_token);
            this.$cookies.set('refresh_token', response.data.refresh_token);

            let url = `/pages`;
            // window.location.href = url;
            // this.$router.push({ path: url });
            this.$emit('signin', url);
          })
          .catch(error => {
            this.$log.error(error);
            this.error = this.locale('users.sigin-failed');
          });
      }
    },
    doLogOut() {
      // this.authCookiePresent = false;
      const host = getAxHostProtocol();
      window.location.href = `${host}/api/signout`;
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
.signin-error {
  color: #f44336;
}
.actions {
  justify-content: space-between;
  display: flex;
}
</style>