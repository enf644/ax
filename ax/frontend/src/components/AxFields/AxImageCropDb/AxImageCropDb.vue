<template>
  <div>
    <span class='label'>{{name}}</span>

    <div
      :id='divId'
      :style='placeholderStyle'
      class='img-placeholder'
      v-show='placeholderIsVisible'
    >
      <div
        :style='{width: this.width + "px", top: this.height/2 - 25 + "px"}'
        class='placeholder-text'
      >
        <i class='up-ico far fa-images'></i>
        <br />
        {{locale("types.AxImageCropDb.placeholder")}}
      </div>
    </div>

    <div
      :id='divId'
      :style='placeholderStyle'
      class='img-placeholder'
      v-show='miniPlaceholderIsVisible'
    >
      <div
        :style='{width: this.width + "px", top: this.height/2 - 10 + "px"}'
        class='placeholder-text'
      >
        <i class='far fa-images'></i>
      </div>
    </div>

    <div v-show='croppaIsVisible'>
      <croppa
        :canvas-color='"#FFFFFF"'
        :height='height'
        :image-border-radius='borderRadius'
        :initial-image='uppyImage'
        :remove-button-size='30'
        :width='width'
        :zoom-speed='zoomSpeed'
        @image-remove='resetAll()'
        prevent-white-space
        ref='croppa'
        remove-button-color='black'
        v-model='croppaData'
      ></croppa>
      <div>
        <v-btn @click='doUpload' class='upload-btn' text>
          <i class='fas fa-upload'></i>
          &nbsp;
          {{locale("types.AxImageCropDb.upload-btn")}}
        </v-btn>
        <v-btn @click='croppaData.rotate()' icon text>
          <i class='fas fa-sync-alt'></i>
        </v-btn>
      </div>
    </div>

    <div v-show='valueIsVisible'>
      <img :src='valueSrc' :style='{width: this.width + "px", height: this.height + "px"}' />
      <br />
      <v-btn @click='clearValue' small text>
        <i class='far fa-trash-alt'></i>
        &nbsp; {{locale("types.AxImageCropDb.clear-image")}}
      </v-btn>
    </div>

    <hr :class='errorClass' />
    <transition enter-active-class='animated shake' leave-active-class='animated fadeOut'>
      <span class='required-error' v-show='errorString'>{{errorString}}</span>
    </transition>
    <span class='hint' v-show='this.options.hint'>{{this.options.hint}} &nbsp;</span>
  </div>
</template>

<script>
import Vue from 'vue';
import Croppa from 'vue-croppa';
import uuid4 from 'uuid4';
import i18n from '@/locale';
import { getAxHost } from '../../../misc';
import '@uppy/core/dist/style.css';
import '@uppy/dashboard/dist/style.css';
import getClassNameForExtension from 'font-awesome-filetypes';
// prettier-ignore
import {
  Webcam, Tus, Core, Dashboard
} from 'uppy';

import 'vue-croppa/dist/vue-croppa.css';

Vue.use(Croppa);

const _ = require('lodash');

export default {
  name: 'AxImageCropDb',
  props: {
    name: null,
    dbName: null,
    tag: null,
    options: null,
    value: null,
    isRequired: null,
    formGuid: null,
    rowGuid: null,
    fieldGuid: null
  },
  data: () => ({
    currentValue: null,
    errors: [],
    uppy: null,
    modalGuid: null,
    croppaData: null,
    uppyImage: null,
    uppyFile: null
  }),
  computed: {
    divId() {
      return `div-${this.modalGuid}`;
    },
    errorString() {
      if (this.errors.length > 0) return this.errors.join('. ');
      return false;
    },
    errorClass() {
      if (this.errors.length > 0) return 'hr-error';
      return null;
    },
    placeholderIsVisible() {
      return (
        !this.uppyImage
        && !this.currentValue
        && this.width >= 120
        && this.height >= 120
      );
    },
    miniPlaceholderIsVisible() {
      return (
        !this.uppyImage
        && !this.currentValue
        && this.width < 120
        && this.height < 120
      );
    },
    croppaIsVisible() {
      return this.uppyImage && !this.currentValue;
    },
    valueIsVisible() {
      return this.currentValue;
    },
    valueSrc() {
      if (this.currentValue && typeof this.currentValue === 'object') {
        return `/api/file/${this.formGuid}/null/${this.fieldGuid}/${this.currentValue.guid}`;
      }
      if (this.currentValue) {
        return `/api/file/${this.formGuid}/${this.rowGuid}/${this.fieldGuid}`;
      }
      return null;
    },
    width() {
      if (this.options.width) return this.options.width * 1;
      return 200;
    },
    height() {
      if (this.options.isRound) return this.width;
      if (this.options.height) return this.options.height * 1;
      return 200;
    },
    borderRadius() {
      if (this.options.borderRadius) return this.options.borderRadius * 1;
      return 0;
    },
    placeholderStyle() {
      let placeholderRadius = 0;
      if (this.options.borderRadius > 0) {
        placeholderRadius = this.options.borderRadius;
      }
      if (this.options.isRound) {
        placeholderRadius = this.height / 2;
      }
      return {
        width: `${this.width}px`,
        height: `${this.height}px`,
        'border-radius': `${placeholderRadius}px`
      };
    },
    zoomSpeed() {
      if (this.width + this.height < 250) return 20;
      return 10;
    }
  },
  watch: {
    currentValue(newValue) {
      this.$emit('update:value', newValue);
    },
    value(newValue) {
      this.currentValue = newValue;
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
    this.currentValue = this.value;
  },
  mounted() {
    this.initUppy();
    this.croppaData.addClipPlugin((ctx, x, y, w, h) => {
      if (this.options.isRound) {
        ctx.beginPath();
        ctx.arc(x + w / 2, y + h / 2, w / 2, 0, 2 * Math.PI, true);
        ctx.closePath();
      }
    });
  },
  methods: {
    locale(key) {
      return i18n.t(key);
    },
    doUpload() {
      this.uppy.removeFile(this.uppyFile.id);
      this.$refs.croppa.generateBlob(blob => {
        this.uppy.addFile({
          name: this.uppyFile.name,
          type: this.uppyFile.type,
          data: blob,
          source: 'Local',
          isRemote: false
        });

        this.uppy.upload().then(result => {
          if (result.failed.length > 0) {
            result.failed.forEach(file => {
              this.$log.error(file.error);
            });
          }
        });
      });
    },
    initUppy() {
      this.uppy = Core({
        id: 'AxImageCropDbUppy',
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
        endpoint: `http://${getAxHost()}/api/upload`
      });
      this.uppy.use(Dashboard, {
        inline: false,
        trigger: `#${this.divId}`,
        target: 'body',
        showProgressDetails: true,
        showLinkToFileUploadResult: false,
        closeModalOnClickOutside: true,
        proudlyDisplayPoweredByUppy: false,
        browserBackButtonClose: true
      });

      if (
        this.options.enableWebcam === true
        || this.options.enableWebcam == null
        || this.options.enableWebcam === undefined
      ) {
        this.uppy.use(Webcam, { target: Dashboard });
      }

      this.uppy.on('file-added', file => {
        this.uppyFile = file;
        const img = new Image();
        const reader = new FileReader();

        reader.onloadend = () => {
          img.src = reader.result;
        };
        reader.readAsDataURL(file.data);

        this.uppyImage = img;
        // this.$refs.croppa.img = file.data;
        this.$refs.croppa.refresh();
        const dashboard = this.uppy.getPlugin('Dashboard');
        if (dashboard.isModalOpen()) {
          dashboard.closeModal();
        }
      });

      this.uppy.on('upload-success', (file, response) => {
        const guid = response.uploadURL.substr(
          response.uploadURL.lastIndexOf('/') + 1
        );
        this.currentValue = {
          guid,
          name: file.name,
          extension: file.extension,
          meta: file.meta,
          type: file.type,
          size: file.size
        };
      });
    },
    isValid() {
      let formIsValid = true;
      this.errors = [];
      if (!this.uploadFinished()) formIsValid = false;
      if (!this.requiredIsValid()) formIsValid = false;
      return formIsValid;
    },
    uploadFinished() {
      if (!this.currentValue && this.uppyImage) {
        this.errors.push(
          this.locale('types.AxImageCropDb.upload-not-finished')
        );
        return false;
      }
      return true;
    },
    requiredIsValid() {
      if (this.isRequired) {
        if (!this.currentValue) {
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
      return `fas ${getClassNameForExtension(extension)}`;
    },
    deleteFile(guid) {
      this.currentValue = [
        ...this.currentValue.filter(element => element.guid !== guid)
      ];
    },
    resetAll() {
      this.uppyImage = null;
      this.uppy.close();
      this.initUppy();
    },
    clearValue() {
      this.currentValue = null;
      this.uppyImage = null;
      this.uppyFile = null;
      this.resetAll();
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
.img-placeholder {
  border: 1px dashed #ccc;
  margin-bottom: 5px;
  border-radius: 3px;
  cursor: pointer;
  position: relative;
}
.placeholder-text {
  /* line-height: 200px; */
  /* margin: auto; */
  text-align: center;
  position: absolute;
  /* top: 50%; */
}
.up-ico {
  font-size: 30px;
}
.clear-value {
  position: absolute;
  right: 0px;
  top: 0px;
}
.hint {
  color: rgba(0, 0, 0, 0.54);
  font-size: 12px;
  margin-top: '5px' !important;
}
.upload-btn {
  color: #f44336;
}
</style>
