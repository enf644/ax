<template>
  <span class='wrap'>
    <i :class='iconClass'></i>
    <input id='name_input' type='text' v-model='currentName'>
    <div id='db_div'>
      <i
        aria-hidden='true'
        class='fas fa-cog but hvr-pop'
        on-click='open_settings'
        title='Open settings'
      ></i>
      <input id='db_input' type='text' v-model='currentDbName'>
    </div>
  </span>
</template>

<script>
export default {
  name: 'construcor-field',
  props: {
    guid: null,
    name: null,
    db_name: null,
    tag: null,
    icon: null
  },
  data: () => ({
    currentName: null,
    currentDbName: null
  }),
  computed: {
    iconClass() {
      return `fas fa-${this.icon}`;
    }
  },
  created() {
    this.currentName = this.name;
    this.currentDbName = this.db_name;
  },
  mounted() {}
};
</script>

<style scoped>
#db_div {
  padding-left: 0px;
  position: absolute;
  top: 13px;
  white-space: nowrap;
  margin-left: 18px;
}
#name_input {
  margin-left: 5px;
  background: transparent;
  width: 150px;
  border: 0px;
  padding: 0px;
  font-weight: 300;
}
#name_input:focus {
  outline: none;
}
#db_input {
  margin-left: 5px;
  color: #cfcfcf;
  position: relative;
  background: transparent;
  width: 125px;
  border: 0px;
  padding: 0px;
  font-weight: 300;
}
#db_input:focus {
  color: black;
  outline: none;
}
.wrap {
  position: relative;
}
.but {
  color: #cfcfcf;
  cursor: pointer;
}
.but:hover {
  color: black !important;
}
.error {
  color: red !important;
  text-decoration: underline;
}
</style>
