<template>
  <v-flex class='ax-field'>
    <component
      :dbName='name'
      :is='component'
      :name='name'
      :optionsJson='optionsJson'
      :value.sync='currentValue'
    ></component>
  </v-flex>
</template>

<script>
export default {
  name: 'ax-field',
  props: {
    name: null,
    dbName: null,
    tag: null,
    optionsJson: null,
    value: null
  },
  data: () => ({
    component: null,
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
    }
  },
  mounted() {
    this.loader().then(() => {
      this.component = () => this.loader();
      this.currentValue = this.value;
    });
  }
};
</script>

<style scoped>
.ax-field {
  min-width: 266px;
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
