<template>
  <div class='overlay-wrapper'>
    <img class='overlay-img' id='overlayImg' v-show="overlayVisible"  src='https://fiverr-res.cloudinary.com/images/q_auto,f_auto/gigs/4249532/original/0d2b5550fa6fda18fdb592fa326a8085a01b9b55/create-2d-3d-cad-drawings-mechanism-in-pro-e.jpg' >
    <div id="webcam-div" class='webcam-div' v-show="webcamVisible" ></div>
    <div id="overlay-div" class='overlay-div' v-show="uppyVisible"></div>
  </div>
</template>

<script>
import i18n from '@/locale.js';
import '@uppy/core/dist/style.css';
import '@uppy/dashboard/dist/style.css';
import '@uppy/webcam/dist/style.css';
import { getAxHost, getAxHostProtocol } from '@/misc';

export default {
  name: 'AxImageWebcamOverlay',
  props: {
    name: null,
    dbName: null,
    tag: null,
    options: null,
    value: null,
    isRequired: null,
    isReadonly: null
  },
  data: () => ({
    modalGuid: null,
    currentValue: null,
    errors: [],
    uppy: null,
    uppyVisible: false,
    overlayVisible: true,
    webcamVisible: true
    
  }),
  computed: {
    divId() {
      return `div-${this.modalGuid}`;
    }
  },
  watch: {
    currentValue(newValue) {
      this.$emit('update:value', newValue);
    },
    value(newValue) {
      this.currentValue = newValue;
    }
  },
  created() {
    this.modalGuid = uuid4();
    this.currentValue = this.value;
  },
  mounted() {
    this.initUppy();
  },  
  methods: {
    initUppy() {
      const Uppy = require('@uppy/core');
      const Dashboard = require('@uppy/dashboard');
      const Webcam = require('@uppy/webcam');
      const Tus = require('@uppy/tus');

      this.uppy = new Uppy({
        debug: true,
        autoProceed: false,
        restrictions: {
          maxFileSize: 1000000,
          maxNumberOfFiles: 1,
          minNumberOfFiles: 1,
          allowedFileTypes: ['image/*']
        }
      })
        .use(Dashboard, {
          trigger: '.UppyModalOpenerBtn',
          inline: true,
          target: `#overlay-div`,
          replaceTargetContent: true,
          showProgressDetails: true,
          note: 'Images and video only, 2–3 files, up to 1 MB',
          height: 400,
          metaFields: [
            { id: 'name', name: 'Name', placeholder: 'file name' },
            {
              id: 'caption',
              name: 'Caption',
              placeholder: 'describe what the image is about'
            }
          ],
          browserBackButtonClose: true
        })
        .use(Webcam, {
            target: `#webcam-div`,
            onBeforeSnapshot: () => Promise.resolve().then( () => { this.showUppy() }),
            countdown: false,
            modes: [
              'picture'
            ],
            mirror: true,
            videoConstraints: {
              facingMode: 'user',
              width: { min: 720, ideal: 1920, max: 1920 },
              height: { min: 480, ideal: 1080, max: 1080 }
            },
            showRecordingLength: false,
            preferredVideoMimeType: null,
            preferredImageMimeType: null,
            locale: {}
          }        
        
        )
        .use(Tus, { endpoint: `${getAxHostProtocol()}/api/upload` });

      this.uppy.on('complete', result => {
        console.log('successful files:', result.successful);
        console.log('failed files:', result.failed);
      });
    },
    showUppy() {
      console.log('show uppy')
      this.uppyVisible = true;
      this.overlayVisible = false;
      this.webcamVisible = false;
    },
    isValid() {
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
        this.errors = [];
        return true;
      }
      return true;
    }
  }
};
</script>

<style scoped>
.overlay-wrapper{
  position: relative;
}
.overlay-div{

}

.overlay-img{
    position: absolute;
    top: 0;
    left: 0;
    height: calc(600px - 75px);
    opacity: 0.5;
    z-index: 100;
    margin-left: auto;
    margin-right: auto;
    left: 0;
    right: 0;
    text-align: center;    
}

.webcam-div {
  height: 600px
}

</style>
