<template>
  <div>
    <v-sheet class='form-container' elevation='5' light>
      <AxForm></AxForm>
    </v-sheet>
  </div>
</template>

<script>
import AxForm from '@/components/AxForm.vue';

export default {
  components: {
    AxForm
  }
};
</script>

<style scoped>
.form-container {
  margin: 20px;
}
</style>
