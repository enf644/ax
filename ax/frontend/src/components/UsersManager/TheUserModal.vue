<template>
  <div class='card'>
    <h1 v-show='this.guid == null'>{{$t("users.modal-header-new")}}</h1>
    <h1 v-show='this.guid'>{{$t("users.modal-header-update")}}</h1>

    <v-btn :ripple='false' @click='closeModal' class='close' color='black' icon text>
      <i class='fas fa-times close-ico'></i>
    </v-btn>
    <br />
    <v-form @submit.prevent='updateGrid' ref='form' v-model='valid'>
      <v-container>
        <v-row>
          <v-col>
            <v-text-field
              :disabled='this.guid != null'
              :hint='$t("users.modal-email-hint")'
              :label='$t("users.modal-email")'
              :rules='[rules.isEmail, rules.required]'
              data-cy='email'
              required
              v-model='email'
            />
          </v-col>
          <v-col>
            <v-text-field
              :hint='$t("users.modal-short-name-hint")'
              :label='$t("users.modal-short-name")'
              :rules='[rules.required]'
              data-cy='user-short-name'
              v-model='shortName'
            ></v-text-field>
          </v-col>
        </v-row>
        <v-row>
          <v-col>
            <v-text-field
              :hint='$t("users.modal-name-hint")'
              :label='$t("users.modal-name")'
              data-cy='user-name'
              v-model='userName'
            ></v-text-field>
          </v-col>
        </v-row>
        <v-row>
          <v-col>
            <v-text-field
              :hint='$t("users.modal-password-hint")'
              :label='$t("users.modal-password")'
              :rules='[rules.createReuired, rules.password]'
              type='password'
              v-model='password'
            ></v-text-field>
          </v-col>
          <v-col>
            <v-text-field
              :label='$t("users.modal-re-password")'
              :rules='[rules.createReuired, rules.rePassword]'
              type='password'
              v-model='rePassword'
            ></v-text-field>
          </v-col>
        </v-row>
        <v-row>
          <v-switch :label='$t("users.modal-block-switch")' v-model='isBlocked'></v-switch>
        </v-row>
      </v-container>

      <br />
      <div class='actions'>
        <v-btn
          @click.prevent='createUser'
          data-cy='create-user-btn'
          small
          type='submit'
          v-show='this.guid == null'
        >
          <i class='fas fa-plus'></i>
          &nbsp; {{$t("users.create-user-btn")}}
        </v-btn>

        <v-btn
          @click.prevent='updateUser'
          data-cy='update-user-btn'
          small
          type='submit'
          v-show='guid'
        >
          <i class='fas fa-pencil-alt'></i>
          &nbsp; {{$t("users.update-user-btn")}}
        </v-btn>

        <v-btn
          @click='promptDeleteUser'
          color='error'
          data-cy='delete-grid-btn'
          small
          text
          v-show='guid'
        >
          <i class='fas fa-trash-alt'></i>
          &nbsp; {{$t("users.delete-user-btn")}}
        </v-btn>
      </div>
    </v-form>
  </div>
</template>

<script>
import apolloClient from '@/apollo';
import gql from 'graphql-tag';

export default {
  name: 'TheUserModal',
  props: {
    guid: null
  },
  data() {
    return {
      email: null,
      userName: null,
      shortName: null,
      password: null,
      rePassword: null,
      isBlocked: null,
      info: null,
      avatarTmp: null,
      valid: false,
      rules: {
        required: value => !!value || this.$t('common.field-required'),
        isEmail: value => {
          const pattern = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
          return pattern.test(value) || this.$t('common.invalid-email');
        },
        createReuired: value => {
          if (this.guid == null) {
            if (value) return true;
            return this.$t('common.field-required');
          }
          return true;
        },
        password: value => {
          if (value == null) return true;
          const reg = /^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])[0-9a-zA-Z]{8,}$/;
          return reg.test(value) || this.$t('users.invalid-new-password');
        },
        rePassword: value => {
          if (this.password == value) return true;
          return this.$t('users.re-password-invalid');
        }
      }
    };
  },
  computed: {
    isNotDefaultView() {
      return !this.isDefaultView;
    },
    defaultGridDbName() {
      const defaultGrid = this.$store.state.form.grids.find(
        grid => grid.isDefaultView === true
      );
      return defaultGrid ? defaultGrid.dbName : null;
    }
  },
  watch: {
    dbName(newValue) {
      if (newValue) {
        if (newValue[0] !== newValue[0].toUpperCase()) {
          const firstLetter = newValue.charAt(0).toUpperCase();
          this.dbName = firstLetter + newValue.slice(1);
        }
      }
    },
    guid(newValue) {
      if (newValue == null) {
        this.email = null;
        this.userName = null;
        this.shortName = null;
        this.password = null;
        this.rePassword = null;
        this.info = null;
        this.avatarTmp = null;
        this.valid = false;
      } else {
        this.loadUser();
      }
    }
  },
  mounted() {
    if (this.guid) {
      this.loadUser();
    }
  },
  methods: {
    loadUser() {
      const LOAD_USER = gql`
        query($guid: String!, $updateTime: String) {
          findUser(guid: $guid, updateTime: $updateTime) {
            guid
            email
            name
            shortName
            info
            isBlocked
          }
        }
      `;

      apolloClient
        .query({
          query: LOAD_USER,
          variables: {
            guid: this.guid,
            updateTime: Date.now()
          }
        })
        .then(data => {
          this.email = data.data.findUser.email;
          this.userName = data.data.findUser.name;
          this.shortName = data.data.findUser.shortName;
          this.info = data.data.findUser.info;
          this.isBlocked = data.data.findUser.isBlocked;
        })
        .catch(error => {
          this.$log.error(`Error in findUser gql => ${error}`);
          this.$dialog.message.error(`${error}`);
        });
    },
    createUser() {
      if (this.$refs.form.validate()) {
        const CREATE_NEW_USER = gql`
          mutation(
            $email: String!
            $name: String
            $shortName: String
            $password: String!
            $avatarTmp: String
            $info: String
            $isBlocked: Boolean
          ) {
            createUser(
              email: $email
              name: $name
              shortName: $shortName
              password: $password
              avatarTmp: $avatarTmp
              info: $info
              isBlocked: $isBlocked
            ) {
              user {
                guid
                email
              }
              ok
              msg
            }
          }
        `;

        apolloClient
          .mutate({
            mutation: CREATE_NEW_USER,
            variables: {
              email: this.email,
              name: this.userName,
              shortName: this.shortName,
              password: this.password,
              avatarTmp: this.avatarTmp,
              info: this.info,
              isBlocked: this.isBlocked
            }
          })
          .then(data => {
            if (data.data.createUser.ok) {
              const msg = this.$t('users.user-created-toast');
              this.$dialog.message.success(
                `<i class="fas fa-plus"></i> &nbsp ${msg}`
              );
              this.closeAndReload();
            } else {
              this.$dialog.message.error(this.$t(data.data.createUser.msg));
            }
          })
          .catch(error => {
            this.$log.error(`Error in createNewUser gql => ${error}`);
            this.$dialog.message.error(`${error}`);
          });
      }
    },
    updateUser() {
      if (this.$refs.form.validate()) {
        const UPDATE_USER = gql`
          mutation(
            $guid: String!
            $name: String
            $shortName: String
            $password: String
            $avatarTmp: String
            $info: String
            $isBlocked: Boolean
          ) {
            updateUser(
              guid: $guid
              name: $name
              shortName: $shortName
              password: $password
              avatarTmp: $avatarTmp
              info: $info
              isBlocked: $isBlocked
            ) {
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
            mutation: UPDATE_USER,
            variables: {
              guid: this.guid,
              name: this.userName,
              shortName: this.shortName,
              password: this.password,
              avatarTmp: this.avatarTmp,
              info: this.info,
              isBlocked: this.isBlocked
            }
          })
          .then(data => {
            const msg = this.$t('users.user-updated-toast');
            this.$dialog.message.success(
              `<i class="fas fa-pencil-alt"></i> &nbsp ${msg}`
            );
            this.closeAndReload();
          })
          .catch(error => {
            this.$log.error(`Error in updateUser gql => ${error}`);
            this.$dialog.message.error(`${error}`);
          });
      }
    },
    async promptDeleteUser(e) {
      e.preventDefault();
      const res = await this.$dialog.confirm({
        text: this.$t('users.user-delete-confirm', { name: this.name }),
        actions: {
          false: this.$t('common.confirm-no'),
          true: {
            text: this.$t('common.confirm-yes'),
            color: 'red'
          }
        }
      });
      if (res) this.deleteUser(this.guid);
    },
    deleteUser(guid) {
      const DELETE_USER = gql`
        mutation($guid: String!) {
          deleteUser(guid: $guid) {
            deleted
          }
        }
      `;

      apolloClient
        .mutate({
          mutation: DELETE_USER,
          variables: {
            guid: this.guid
          }
        })
        .then(data => {
          const msg = this.$t('users.user-deleted-toast');
          this.$dialog.message.success(
            `<i class="fas fa-trash-alt"></i> &nbsp ${msg}`
          );
          this.closeAndReload();
        })
        .catch(error => {
          this.$log.error(`Error in deleteUser gql => ${error}`);
          this.$dialog.message.error(`${error}`);
        });
    },
    closeModal() {
      this.$emit('close');
    },
    closeAndReload() {
      this.$emit('closeAndReload');
    }
  }
};
</script>

<style scoped>
.card {
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
.actions {
  justify-content: space-between;
  display: flex;
}
</style>
