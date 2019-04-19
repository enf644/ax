<template>
  <div class='container'>
    <ax-grid form='cars' update_time='gridUpdateTime'></ax-grid>
  </div>
</template>

<script>
import AxGrid from '@/components/AxGrid.vue';

export default {
  name: 'ConstructorGridContent',
  components: { AxGrid },
  data: () => ({})
};
</script>

<style scoped>
.container {
  padding: 25px;
  background: white;
  height: 100%;
}
</style>
