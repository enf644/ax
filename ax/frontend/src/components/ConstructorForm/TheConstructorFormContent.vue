<template>
  <div>
    <ax-form
      :db_name='dbName'
      :opened_tab='openedTab'
      :update_time='updateFormFlag'
      @update:tab='updateTab'
      @update:value='updateValue'
      ref='form'
      v-if='dbName'
    ></ax-form>

    <div class='footer'>
      <v-btn
        :to='"/admin/" + this.$route.params.db_name + "/workflow"'
        class='constructor-button'
        flat
        small
      >
        &nbsp;
        <b>Next</b> &nbsp;
        <i class='fas fa-arrow-right'></i> &nbsp;
        build Workflow
        &nbsp;
        <i class='fas fa-code-branch'></i>
      </v-btn>
    </div>
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
      return Date.now();
    }
  },
  watch: {
    formWatcher() {
      this.updateFormFlag = Date.now();
    }
  },
  methods: {
    updateValue() {
      this.value = this.$refs.form.value;
    },
    updateTab() {
      this.openedTab = this.$refs.form.activeTab;
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
</style>
