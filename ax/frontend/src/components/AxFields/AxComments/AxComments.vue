<template>
  <div>
    <span class='label'>{{name}}</span>
    <div v-if='!this.rowGuid'>
      <b>{{locale("types.AxComments.new-row-warning")}}</b>
    </div>
    <div v-if='this.rowGuid'>
      <AxMessages
        :height='maxHeight'
        :hint='options.hint'
        :isReadonly='isReadonly'
        :threadGuid='value'
      ></AxMessages>
    </div>
  </div>
</template>

<script>
import i18n from '@/locale';
import AxMessages from '@/components/AxMessages.vue';

export default {
  name: 'AxComments',
  props: {
    name: null,
    dbName: null,
    tag: null,
    options: null,
    value: null,
    isRequired: null,
    isReadonly: null,
    formGuid: null,
    rowGuid: null,
    fieldGuid: null
  },
  components: { AxMessages },
  data: () => ({}),
  computed: {
    maxHeight() {
      if (this.options.maxHeight) return this.options.maxHeight;
      return 350;
    }
  },
  watch: {},
  created() {},
  mounted() {},
  methods: {
    locale(key) {
      return i18n.t(key);
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
</style>
