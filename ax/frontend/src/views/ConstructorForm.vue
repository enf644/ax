<template>
  <splitpanes @resize='resizeForm()' class='ax-admin-splits' watch-slots>
    <div class='ax-admin-drawer-first' splitpanes-min='20' splitpanes-size='20'>
      <TheConstructorFormDrawerFirst></TheConstructorFormDrawerFirst>
    </div>
    <div class='ax-admin-drawer-second' splitpanes-min='20' splitpanes-size='20'>
      <TheConstructorFormDrawerSecond></TheConstructorFormDrawerSecond>
    </div>
    <div class='ax-admin-content-pane' splitpanes-min='30' splitpanes-size='60'>
      <TheConstructorFormContent ref='formContent'></TheConstructorFormContent>
    </div>
  </splitpanes>
</template>

<script>
import TheConstructorFormContent from '@/components/ConstructorForm/TheConstructorFormContent.vue';
import TheConstructorFormDrawerFirst from '@/components/ConstructorForm/TheConstructorFormDrawerFirst.vue';
import TheConstructorFormDrawerSecond from '@/components/ConstructorForm/TheConstructorFormDrawerSecond.vue';
import Splitpanes from 'splitpanes';
import 'splitpanes/dist/splitpanes.css';

export default {
  name: 'constructor-form',
  components: {
    TheConstructorFormDrawerFirst,
    TheConstructorFormDrawerSecond,
    TheConstructorFormContent,
    Splitpanes
  },
  methods: {
    resizeForm() {
      this.$refs.formContent.handleResize();
    }
  }
};
</script>

<style scoped>
</style>
