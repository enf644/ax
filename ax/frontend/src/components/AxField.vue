<template>
  <v-flex :xs12='isWholeRow' class='ax-field'>
    <component
      :dbName='dbName'
      :is='component'
      :isRequired='isRequired'
      :name='name'
      :options='options'
      :value.sync='currentValue'
      ref='thisField'
    ></component>
  </v-flex>
</template>

<script>
import i18n from '../locale.js';

export default {
  name: 'ax-field',
  props: {
    name: null,
    dbName: null,
    tag: null,
    optionsJson: null,
    value: null,
    isRequired: null,
    isWholeRow: null
  },
  data: () => ({
    options: null,
    component: null,
    currentName: null,
    currentValue: null
  }),
  computed: {
    loader() {
      if (!this.tag) {
        return null;
      }
      return () => import(`@/components/AxFields/${this.tag}/${this.tag}.vue`);
    }
  },
  watch: {
    currentValue(newValue) {
      this.$emit('update:value', newValue);
    },
    optionsJson(newValue) {
      this.options = JSON.parse(newValue);
      if (this.$refs.thisField.errors.length > 0) {
        setTimeout(() => {
          this.$refs.thisField.errors = [];
          this.$refs.thisField.isValid();
        }, 10);
      }
    }
  },
  created() {
    this.options = JSON.parse(this.optionsJson);
    if (!this.options.required_text) {
      this.options.required_text = i18n.t('common.field-required');
    }
  },
  mounted() {
    this.loader().then(() => {
      this.component = () => this.loader();
      this.currentValue = this.value;
    });
  },
  methods: {
    isValid() {
      if (typeof this.$refs.thisField.isValid === 'function') {
        return this.$refs.thisField.isValid();
      }
      return true;
    }
  }
};
</script>

<style scoped>
.ax-field {
  min-width: 220px;
  padding-left: 3% !important;
  padding-right: 3% !important;
}
@media only screen and (min-width: 2000px) {
  /* big screens */
  /* .ax-field {
    margin: 0px 30px;
    width: 450px;
  } */
}

@media only screen and (min-width: 650px) and (max-width: 2000px) {
  /* tablets and desktop */
  /* .ax-field {
    margin: 0px 5%;
    width: 40%;
  } */
}

@media only screen and (max-width: 650px) {
  /* .ax-field {
    margin: 15px 0px;
    width: 80%;
  } */
}
</style>
