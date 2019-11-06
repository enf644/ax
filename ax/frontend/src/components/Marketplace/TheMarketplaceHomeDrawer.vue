<template>
  <div>
    <v-btn id='btnId' small>
      <i class='fas fa-puzzle-piece'></i>
      &nbsp;
      {{locale("marketplace.upload-app-btn")}}
    </v-btn>

    <modal :name='`terminal-${this.modalGuid}`' adaptive height='auto' scrollable width='60%'>
      <div>
        <v-btn :ripple='false' @click='closeTerminalModal' class='close' color='black' icon text>
          <i class='fas fa-times close-ico'></i>
        </v-btn>
        <div class='header'>
          <i class='fas fa-terminal'></i>
          &nbsp;
          {{locale("marketplace.terminal-header")}}
        </div>
        <AxTerminal :modalGuid='modalGuid'></AxTerminal>
      </div>
    </modal>
  </div>
</template>

<script>
import i18n from '@/locale';
import uuid4 from 'uuid4';
import { getAxHost, uuidWithDashes, getAxHostProtocol } from '@/misc';
import '@uppy/core/dist/style.css';
import '@uppy/dashboard/dist/style.css';
import apolloClient from '@/apollo';
import gql from 'graphql-tag';
import AxTerminal from '@/components/AxTerminal.vue';

// prettier-ignore
import {
  Core, Dashboard, Webcam, Tus
} from 'uppy';

export default {
  name: 'TheMarketplaceHomeDrawer',
  components: { AxTerminal },
  data: () => ({
    currentValue: null,
    errors: [],
    uppy: null,
    modalGuid: null
  }),
  created() {
    this.modalGuid = uuid4();
  },
  mounted() {
    this.initUppy();
  },
  methods: {
    locale(key) {
      return i18n.t(key);
    },
    initUppy() {
      this.uppy = Core({
        id: 'AxAppUppy',
        autoProceed: false,
        allowMultipleUploads: false,
        debug: false,
        restrictions: {
          maxFileSize: 1000000000,
          allowedFileTypes: ['.zip']
        }
      });
      this.uppy.use(Tus, {
        endpoint: `${getAxHostProtocol()}/api/upload`
      });
      this.uppy.use(Dashboard, {
        trigger: `#btnId`,
        inline: false,
        target: 'body',
        showProgressDetails: true,
        showLinkToFileUploadResult: false,
        closeModalOnClickOutside: true,
        proudlyDisplayPoweredByUppy: false,
        browserBackButtonClose: true
      });

      this.uppy.on('upload-success', (file, response) => {
        const fileGuid = response.uploadURL.substr(
          response.uploadURL.lastIndexOf('/') + 1
        );
        this.openTerminalModal();
        setTimeout(() => {
          this.installFromPackage(fileGuid);
        }, 2000);
      });

      this.uppy.on('complete', () => {
        const dashboard = this.uppy.getPlugin('Dashboard');
        if (dashboard.isModalOpen()) {
          dashboard.closeModal();
        }
        this.uppy.reset();
      });
    },
    installFromPackage(fileGuid) {
      console.log(`guid = ${fileGuid}`);

      const FROM_PACKAGE = gql`
        mutation($fileGuid: String!, $modalGuid: String!) {
          installFromPackage(fileGuid: $fileGuid, modalGuid: $modalGuid) {
            msg
            ok
          }
        }
      `;

      apolloClient
        .mutate({
          mutation: FROM_PACKAGE,
          variables: {
            fileGuid: fileGuid,
            modalGuid: this.modalGuid
          }
        })
        .then(data => {
          const msg = data.data.installFromPackage.msg;
          console.log(msg);
          this.$store.commit(
            'home/setShowToastMsg',
            this.$t('marketplace.app-installed-toast')
          );

          this.$store.dispatch('home/getAllForms', {
            updateTime: Date.now()
          });
        })
        .catch(error => {
          this.$log.error(
            `Error in installFromPackage apollo client => ${error}`
          );
        });
    },
    openTerminalModal() {
      this.$modal.show(`terminal-${this.modalGuid}`);
    },
    closeTerminalModal() {
      this.$modal.hide(`terminal-${this.modalGuid}`);
    }
  }
};
</script>

<style scoped>
.close {
  position: absolute;
  right: 10px;
  top: 10px;
}
.close-ico {
  font-size: 20px;
}
.header {
  font-size: 1.2em;
  height: 40px;
  line-height: 40px;
  vertical-align: middle;
  padding-left: 25px;
  margin-top: 25px;
}
</style>
