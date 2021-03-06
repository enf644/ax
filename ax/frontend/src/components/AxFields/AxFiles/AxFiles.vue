<template>
  <div>
    <span class='label'>{{name}}</span>
    <br />
    <v-chip
      :close='isReadonly == false'
      :key='file.guid'
      @click='openFile(file)'
      @click:close='deleteFile(file.guid)'
      class='mr-2 mb-2'
      v-for='file in this.currentValue'
    >
      <v-avatar>
        <i :class='getFileIcon(file.extension)'></i>
      </v-avatar>
      {{ file.name }}
    </v-chip>

    <v-btn :id='btnId' small text v-if='this.isReadonly == false'>
      <i class='fas fa-upload'></i>
      &nbsp;
      {{locale("types.AxFiles.upload-btn")}}
    </v-btn>

    <hr :class='errorClass' />
    <transition enter-active-class='animated shake' leave-active-class='animated fadeOut'>
      <span class='required-error' v-show='errorString'>{{errorString}}</span>
    </transition>
    <span class='hint' v-show='this.options.hint'>{{this.options.hint}} &nbsp;</span>
  </div>
</template>

<script>
import i18n from '@/locale';
import uuid4 from 'uuid4';
import { getAxHost, uuidWithDashes, getAxHostProtocol } from '@/misc';
import '@uppy/core/dist/style.css';
import '@uppy/dashboard/dist/style.css';
import '@uppy/webcam/dist/style.css';
import getClassNameForExtension from 'font-awesome-filetypes';

// prettier-ignore

// import Uppy from '@uppy/core'
// import Dashboard from '@uppy/dashboard';
// import Webcam from '@uppy/webcam';
// import Tus from '@uppy/tus';

// import {
//   Core, Dashboard, Webcam, Tus
// } from 'uppy';

import Uppy, { Core, Dashboard, Webcam, Tus } from 'uppy'

const _ = require('lodash');

export default {
  name: 'AxFiles',
  props: {
    name: null,
    dbName: null,
    tag: null,
    options: null,
    value: null,
    isRequired: null,
    isReadonly: {
      type: Boolean,
      default: false
    },
    formGuid: null,
    rowGuid: null,
    fieldGuid: null
  },
  data: () => ({
    currentValue: null,
    errors: [],
    uppy: null,
    modalGuid: null
  }),
  computed: {
    btnId() {
      return `btn-${this.modalGuid}`;
    },
    errorString() {
      if (this.errors.length > 0) return this.errors.join('. ');
      return false;
    },
    errorClass() {
      if (this.errors.length > 0) return 'hr-error';
      return null;
    }
  },
  watch: {
    currentValue(newValue) {
      this.$emit('update:value', newValue);
    },
    value(newValue) {
      if (Array.isArray(newValue)) this.currentValue = newValue;
      else this.currentValue = JSON.parse(newValue);
    },
    options(newValue, oldValue) {
      if (oldValue) {
        this.uppy.close();
        this.initUppy();
      }
    }
  },
  created() {
    this.modalGuid = uuid4();
    if (this.value) {
      if (Array.isArray(this.value)) this.currentValue = this.value;
      else this.currentValue = JSON.parse(this.value);
    }
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
        id: 'AxFilesUppy',
        autoProceed: false,
        allowMultipleUploads: true,
        debug: false,
        restrictions: {
          maxFileSize: Number(_.get(this.options, 'maxFileSize', null)),
          maxNumberOfFiles: Number(
            _.get(this.options, 'maxNumberOfFiles', null)
          ),
          minNumberOfFiles: Number(
            _.get(this.options, 'minNumberOfFiles', null)
          ),
          allowedFileTypes: Number(
            _.get(this.options, 'allowedFileTypes', null)
          )
        }
      });
      this.uppy.use(Tus, {
        endpoint: `${getAxHostProtocol()}/api/upload`
      });
      this.uppy.use(Dashboard, {
        trigger: `#${this.btnId}`,
        inline: false,
        target: 'body',
        showProgressDetails: true,
        showLinkToFileUploadResult: false,
        closeModalOnClickOutside: true,
        proudlyDisplayPoweredByUppy: false,
        browserBackButtonClose: true
      });

      if (
        this.options.enableWebcam === true ||
        this.options.enableWebcam == null ||
        this.options.enableWebcam === undefined
      ) {
        this.uppy.use(Webcam, {
          target: Dashboard,
          modes: ['video-audio', 'video-only', 'audio-only', 'picture']
        });
      }

      this.uppy.on('upload-success', (file, response) => {
        const guid = response.uploadURL.substr(
          response.uploadURL.lastIndexOf('/') + 1
        );
        if (!this.currentValue) this.currentValue = [];
        const newFile = {
          guid,
          name: file.name,
          extension: file.extension,
          meta: file.meta,
          type: file.type,
          size: file.size,
          isTmp: true
        };
        this.currentValue.push(newFile);
      });

      this.uppy.on('complete', () => {
        const dashboard = this.uppy.getPlugin('Dashboard');
        if (dashboard.isModalOpen()) {
          dashboard.closeModal();
        }
        this.uppy.reset();
      });
    },
    isValid() {
      this.errors = [];
      if (this.requiredIsValid()) return true;
      return false;
    },
    requiredIsValid() {
      if (this.isRequired) {
        if (!this.currentValue || this.currentValue.length === 0) {
          let msg = i18n.t('common.field-required');
          if (this.options.required_text) msg = this.options.required_text;
          this.errors.push(msg);
          return false;
        }
        return true;
      }
      return true;
    },
    getFileIcon(extension) {
      if (extension) {
        const ico = getClassNameForExtension(extension);
        return `fas ${ico}`;
      }
      return 'fas fa-file';
    },
    deleteFile(guid) {
      this.currentValue = [
        ...this.currentValue.filter(element => element.guid !== guid)
      ];
    },
    openFile(file) {
      let rowGuid = uuidWithDashes(this.rowGuid);
      if (file.isTmp) rowGuid = 'null';

      const url = `${getAxHostProtocol()}/api/file/${
        this.formGuid
      }/${rowGuid}/${this.fieldGuid}/${file.guid}/${file.name}`;
      Object.assign(document.createElement('a'), {
        target: '_blank',
        href: url
      }).click();
    }
  }
};
</script>

<style scoped>
.label {
  font-size: 13px;
  color: #000;
  opacity: 0.54;
}
.file-a {
  margin-right: 15px;
  text-decoration: none;
}
.required-error {
  margin-top: '5px' !important;
  color: #b71c1c;
  font-size: 12px;
  margin-right: 15px;
}
.hr-error {
  border-color: #b71c1c;
}
.hint {
  color: rgba(0, 0, 0, 0.54);
  font-size: 12px;
  margin-top: '5px' !important;
}
</style>
