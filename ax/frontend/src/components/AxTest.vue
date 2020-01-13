<template>
  <div>
    <div id='drag-drop-area'></div>
  </div>
</template>

<script>
import '@uppy/core/dist/style.css';
// import Core from '@uppy/core';
// import Tus from '@uppy/tus';

import Uppy, { Core, Dashboard, Webcam, Tus } from 'uppy';

export default {
  props: {
    propD: {
      type: String,
      default: 'wtf'
    }
  },
  mounted() {
    console.log(uppy);
    console.log(Uppy);
  },
  data() {
    return {
      theUppy: null
    };
  },
  mounted() {
    this.theUppy = Core()
      .use(Dashboard, {
        inline: true,
        target: '#drag-drop-area'
      })
      .use(Tus, { endpoint: 'https://master.tus.io/files/' });

    this.theUppy.on('complete', result => {
      console.log(
        'Upload complete! We’ve uploaded these files:',
        result.successful
      );
    });
  },
  methods: {}
};
</script>

<style scoped>
</style>
