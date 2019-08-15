<template>
  <span class='wrap'>
    <i class='far fa-bookmark'></i>
    <input
      @change='applyChange'
      @click='focusName'
      id='nameInput'
      ref='nameInput'
      type='text'
      v-model='currentName'
    />
  </span>
</template>

<script>
//       tabindex='-1'
import i18n from '../../locale.js';
import store from '../../store';

export default {
  name: 'construcor-tab',
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
  mounted() {
    if (store.state.form.createdFieldGuid === this.guid) this.focusName();
  },
  methods: {
    focusName() {
      setTimeout(() => {
        this.$refs.nameInput.focus();
        this.$refs.nameInput.select();
      }, 10);
    },
    applyChange() {
      store
        .dispatch('form/updateTab', {
          guid: this.guid,
          name: this.currentName
        })
        .then(() => {
          this.$refs.nameInput.blur();
          const msg = i18n.tc('form.update-tab-toast');
          this.$dialog.message.success(
            `<i class="far fa-folder"></i> &nbsp ${msg}`
          );
        });
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
.wrap {
  white-space: nowrap;
}
</style>
