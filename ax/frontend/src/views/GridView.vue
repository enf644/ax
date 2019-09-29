<template>
  <v-app id='ax-grid-viewer'>
    <div class='grid-wrapper'>
      <AxGrid :form='formDbName' :grid='gridDbName'></AxGrid>
    </div>
  </v-app>
</template>

<script>
import AxGrid from '@/components/AxGrid.vue';

export default {
  name: 'GridView',
  components: { AxGrid },
  computed: {
    formDbName() {
      return this.$route.params.form;
    },
    gridDbName() {
      return this.$route.params.grid;
    }
  }
};
</script>

<style scoped>
.grid-wrapper {
  background: white;
  /* padding-top: 25px;
  padding-bottom: 25px;
  padding-left: 10%;
  padding-right: 10%; */
  width: 100%;
  height: 100%;
}
</style>
