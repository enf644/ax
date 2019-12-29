<template>
  <v-app id='ax-grid-app'>
    <AxGrid
      :arguments='this.arguments'
      :form='form'
      :grid='grid'
      :height='height'
      :update_time='update_time'
      :width='width'
    />
  </v-app>
</template>

<script>
import AxGrid from '@/components/AxGrid.vue';

export default {
  name: 'AxGridComponent',
  components: { AxGrid },
  props: {
    form: null,
    grid: null,
    update_time: null,
    arguments: null,
    width: null,
    height: null
  },
  data: () => ({
    guid: null
  }),
  computed: {},
  watch: {},
  mounted() {},
  methods: {}
};
</script>

<style scoped>
</style>