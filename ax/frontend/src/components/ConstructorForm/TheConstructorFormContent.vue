<template>
  <div class='ax-form-container'>
    <ax-form
      :db_name='dbName'
      :opened_tab='openedTab'
      :update_time='updateFormFlag'
      @update:tab='updateTab'
      @update:value='updateValue'
      constructor_mode
      ref='form'
      v-if='dbName'
    ></ax-form>
  </div>
</template>

<script>
import AxForm from '@/components/AxForm.vue';

export default {
  components: { AxForm },
  data: () => ({
    updateFormFlag: null,
    value: null,
    openedTab: null
  }),
  computed: {
    dbName() {
      return this.$store.state.form.dbName;
    },
    formWatcher() {
      // eslint-disable-next-line no-unused-vars
      let zero = null;
      zero = this.$store.state.form.fields;
      zero = this.$store.state.form.actions;
      zero = this.$store.state.form.name;
      zero = this.$store.state.form.dbName;
      zero = this.$store.state.form.icon;
      zero = this.$store.state.form.updateTime;
      return Date.now();
    }
  },
  watch: {
    formWatcher() {
      if (this.$store.state.form.dbName) this.updateFormFlag = Date.now();
    }
  },
  methods: {
    updateValue() {
      this.value = this.$refs.form.value;
    },
    updateTab() {
      this.openedTab = this.$refs.form.activeTab;
    },
    handleResize() {
      this.$refs.form.handleResize();
    }
  }
};
</script>

<style scoped>
.data-preview {
  width: 60%;
  margin: auto;
  padding: 20px;
}
.footer {
  width: 100%;
  text-align: right;
}
.ax-form-container {
  padding: 20px;
}
</style>
