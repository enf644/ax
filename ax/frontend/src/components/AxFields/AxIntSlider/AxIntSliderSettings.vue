<template>
  <AxFieldSettings :guid='guid' :options='changedOptions' @closed='$emit("closed")'>
    <v-text-field
      :label='locale("types.AxIntSlider.minValue-label")'
      v-model='changedOptions.minValue'
    ></v-text-field>
    <v-text-field
      :label='locale("types.AxIntSlider.maxValue-label")'
      v-model='changedOptions.maxValue'
    ></v-text-field>
    <v-text-field :label='locale("types.AxIntSlider.step-label")' v-model='changedOptions.step'></v-text-field>
  </AxFieldSettings>
</template>

<script>
import AxFieldSettings from '@/components/AxFieldSettings.vue';
import i18n from '@/locale.js';

export default {
  name: 'AxIntSliderSettings',
  components: { AxFieldSettings },
  props: {
    guid: null,
    options: null
  },
  data: () => ({
    changedOptions: {},
    errors: []
  }),
  created() {
    this.changedOptions = this.options;
    if (!this.changedOptions.minValue) this.changedOptions.minValue = 0;
    if (!this.changedOptions.maxValue) this.changedOptions.maxValue = 100;
    if (!this.changedOptions.step) this.changedOptions.step = 1;
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
