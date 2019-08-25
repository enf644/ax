<template>
  <AxFieldSettings :guid='guid' :options='changedOptions' @closed='$emit("closed")'>
    <v-layout row wrap>
      <v-flex xs6>
        <v-text-field
          :label='locale("types.AxFiles.settings-min-number-label")'
          type='number'
          v-model='changedOptions.minNumberOfFiles'
        ></v-text-field>
      </v-flex>
      <v-flex offset-xs1 xs5>
        <v-text-field
          :label='locale("types.AxFiles.settings-max-number-label")'
          type='number'
          v-model='changedOptions.maxNumberOfFiles'
        ></v-text-field>
      </v-flex>
      <v-flex xs6>
        <v-text-field
          :hint='locale("types.AxFiles.settings-max-size-hint")'
          :label='locale("types.AxFiles.settings-max-size-label")'
          persistent-hint
          settings-max-size-hint
          type='number'
          v-model='changedOptions.maxFileSize'
        ></v-text-field>
      </v-flex>
      <v-flex offset-xs1 xs5>
        <v-switch
          :label='this.locale("types.AxFiles.settings-enable-webcam-label")'
          cy-data='settings-enableModal'
          v-model='changedOptions.enableWebcam'
        ></v-switch>
      </v-flex>
      <br />
      <v-text-field
        :hint='locale("types.AxFiles.settings-types-hint")'
        :label='locale("types.AxFiles.settings-types-label")'
        persistent-hint
        type='number'
        v-model='changedOptions.allowedFileTypes'
      ></v-text-field>
    </v-layout>
  </AxFieldSettings>
</template>


<script>
import AxFieldSettings from '@/components/AxFieldSettings.vue';
import i18n from '@/locale';

export default {
  name: 'AxFilesSettings',
  components: { AxFieldSettings },
  props: {
    guid: null,
    options: null
  },
  data: () => ({
    changedOptions: {}
  }),
  created() {
    this.changedOptions = this.options;
    if (
      this.changedOptions.enableWebcam == null
      || this.changedOptions.enableWebcam === undefined
    ) {
      this.changedOptions.enableWebcam = true;
    }
  },
  methods: {
    locale(key) {
      return i18n.t(key);
    }
  }
};
</script>

<style scoped>
</style>
