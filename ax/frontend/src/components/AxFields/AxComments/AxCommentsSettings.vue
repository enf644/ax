<template>
  <AxFieldSettings :guid='guid' :options='changedOptions' @closed='$emit("closed")'>
    {{locale("types.AxComments.settings-height")}}
    <v-slider max='800' min='100' thumb-label v-model='changedOptions.maxHeight'></v-slider>
  </AxFieldSettings>
</template>

<script>
import AxFieldSettings from '@/components/AxFieldSettings.vue';
import i18n from '@/locale.js';
import MonacoEditor from 'vue-monaco';

export default {
  name: 'AxCommentsSettings',
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
    if (!this.options.maxHeight) this.changedOptions.maxHeight = 350;
  },
  mounted() {},
  methods: {
    locale(key) {
      return i18n.t(key);
    }
  }
};
</script>

<style scoped>
.editor {
  width: 100%;
  height: 400px;
}
</style>
