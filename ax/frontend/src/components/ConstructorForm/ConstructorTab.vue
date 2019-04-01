<template>
  <span class='wrap'>
    <i @click='focusName' class='far fa-bookmark'></i>
    <input @click='focusName' id='nameInput' ref='nameInput' type='text' v-model='currentName'>
  </span>
</template>

<script>
export default {
  name: 'construcor-field',
  props: {
    guid: null,
    name: null
  },
  data: () => ({
    currentName: null
  }),
  created() {
    this.currentName = this.name;
  },
  mounted() {},
  methods: {
    focusName() {
      setTimeout(() => {
        this.$refs.nameInput.focus();
        this.$refs.nameInput.select();
      }, 10);
    }
  }
};
</script>

<style scoped>
#nameInput {
  margin-left: 5px;
  border: 0px;
  padding: 0px;
  line-height: 12px;
  background: transparent;
  font-weight: 300;
}
#nameInput:focus {
  outline: none;
}
</style>
