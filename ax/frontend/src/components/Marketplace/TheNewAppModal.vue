<template>
  <div class='card'>
    <v-btn :ripple='false' @click='closeModal' class='close' color='black' icon text>
      <i class='fas fa-times close-ico'></i>
    </v-btn>
    <div v-if='!this.showLoading && !this.appUrl '>
      <h1>{{locale("marketplace.create-modal-header")}}</h1>
      <v-form @submit.prevent='createApp()' ref='form' v-model='valid'>
        <!-- <v-text-field
        :label='locale("marketplace.name-input")'
        :rules='rules.required'
        v-model='name'
      ></v-text-field>
        <br />-->
        <v-text-field
          :hint='locale("marketplace.db-name-input-hint")'
          :label='locale("marketplace.db-name-input")'
          :rules='rules.kebab'
          v-model='dbName'
        ></v-text-field>
        <br />
        <v-text-field
          :hint='locale("marketplace.version-input-hint")'
          :label='locale("marketplace.version-input")'
          :rules='rules.required'
          ref='versionInput'
          v-model='version'
        ></v-text-field>
        <br />
        <v-text-field
          :hint='locale("marketplace.root-page-input-hint")'
          :label='locale("marketplace.root-page-input")'
          :rules='rules.dbName'
          v-model='rootPage'
        ></v-text-field>
      </v-form>
      <v-switch :label='locale("marketplace.include-data-input")' v-model='includeData'></v-switch>
      <div class='actions'>
        <v-btn @click='createApp()' small>
          <i class='fas fas fa-store'></i>
          &nbsp;
          {{locale("marketplace.create-app")}}
        </v-btn>
      </div>
    </div>
    <div v-if='showLoading'>
      <i class='fas fa-spinner fa-spin app-spinner'></i>
    </div>
    <div v-if='appUrl'>
      <h1>{{$t("marketplace.download-package-header")}}</h1>
      <br />
      <v-btn @click='downloadPackage()' small>
        <i class='fas fa-puzzle-piece'></i>
        &nbsp;
        {{$t("marketplace.download-package-btn")}}
      </v-btn>
    </div>
  </div>
</template>

<script>
import AutoNumeric from 'autonumeric';
// import CatalogItem from '@/components/CatalogItem.vue';
import gql from 'graphql-tag';
import apolloClient from '@/apollo';
import { getAxHostProtocol } from '@/misc';

export default {
  name: 'TheNewAppModal',
  components: {},
  props: {
    folderGuid: null
  },
  data() {
    return {
      valid: false,
      name: '',
      version: '0,01',
      dbName: null,
      rootPage: null,
      includeData: false,
      rules: {
        required: [v => !!v || this.$t('common.field-required')],
        pageDbName: [
          v =>
            /^([a-z0-9]+)*([A-Z][a-z0-9]*)*$/.test(v) ||
            this.$t('pages.modal-db-name-error')
        ],
        kebab: [
          v => !!v || this.$t('common.field-required'),
          v =>
            /^[a-z0-9-]+$/.test(v) || this.$t('marketplace.kebab-db-name-error')
        ]
      },
      numericObject: null,
      appUrl: null,
      showLoading: false
    };
  },
  computed: {},
  watch: {},
  mounted() {
    let autoNumberOptions = {
      currencySymbol: '',
      decimalCharacter: ',',
      decimalPlaces: 2,
      decimalPlacesRawValue: 2,
      digitGroupSeparator: '',
      wheelStep: 0.01,
      minimumValue: 0.01,
      formulaMode: false
    };

    this.numericObject = new AutoNumeric(
      this.$refs.versionInput.$refs.input,
      autoNumberOptions
    );
  },
  methods: {
    locale(key) {
      return this.$t(key);
    },
    closeModal() {
      this.$emit('close');
    },
    downloadPackage() {
      Object.assign(document.createElement('a'), {
        target: '_blank',
        href: this.appUrl
      }).click();
    },
    createApp() {
      if (this.$refs.form.validate()) {
        this.showLoading = true;

        const CREATE_APP = gql`
          mutation(
            $folderGuid: String!
            $name: String!
            $version: String!
            $dbName: String!
            $rootPage: String
            $includeData: Boolean
          ) {
            createMarketplaceApplication(
              folderGuid: $folderGuid
              name: $name
              version: $version
              dbName: $dbName
              rootPage: $rootPage
              includeData: $includeData
            ) {
              downloadUrl
              ok
            }
          }
        `;

        const vars = {
          folderGuid: this.folderGuid,
          name: this.name,
          version: this.version,
          dbName: this.dbName,
          rootPage: this.rootPage,
          includeData: this.includeData
        };

        apolloClient
          .mutate({
            mutation: CREATE_APP,
            variables: vars
          })
          .then(data => {
            const url = data.data.createMarketplaceApplication.downloadUrl;
            const host = getAxHostProtocol();
            this.appUrl = host + url;
            this.showLoading = false;
          })
          .catch(error => {
            const err = `Error in createApp apollo client => ${error}`;
            this.$store.commit('home/setShowErrorMsg', err);
          });
      }
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
.app-spinner {
  font-size: 40px;
}
</style>