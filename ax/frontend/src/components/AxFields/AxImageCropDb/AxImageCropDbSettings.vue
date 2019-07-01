<template>
  <AxFieldSettings :guid='guid' :options='changedOptions' @closed='$emit("closed")'>
    <v-layout row wrap>
      <v-flex xs6>
        <v-text-field
          :label='locale("types.AxImageCropDb.settings-width")'
          type='number'
          v-model='changedOptions.width'
        ></v-text-field>
      </v-flex>
      <v-flex offset-xs1 xs5>
        <v-text-field
          :label='locale("types.AxImageCropDb.settings-height")'
          type='number'
          v-model='changedOptions.height'
        ></v-text-field>
      </v-flex>
      <v-flex xs6>
        <v-text-field
          :label='locale("types.AxImageCropDb.settings-border-radius")'
          persistent-hint
          settings-max-size-hint
          type='number'
          v-model='changedOptions.borderRadius'
        ></v-text-field>
      </v-flex>
      <v-flex offset-xs1 xs5>
        <v-switch
          :label='this.$t("types.AxImageCropDb.settings-is-round")'
          v-model='changedOptions.isRound'
        ></v-switch>
      </v-flex>
    </v-layout>
  </AxFieldSettings>
</template>


<script>
import AxFieldSettings from '@/components/AxFieldSettings.vue';
import i18n from '../../../locale.js';

export default {
  name: 'AxImageCropDbSettings',
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
    if (!this.changedOptions.width) this.changedOptions.width = 200;
    if (!this.changedOptions.height) this.changedOptions.height = 200;
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
