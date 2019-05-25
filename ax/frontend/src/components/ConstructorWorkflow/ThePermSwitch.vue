<template>
  <div class='nobr'>
    <i :class='getHiddenClass()' @click='dispatchSetStatePermission(false, false)' ref='hidden'></i>
    <i :class='getReadClass()' @click='dispatchSetStatePermission(true, false)' ref='read'></i>
    <i :class='getEditClass()' @click='dispatchSetStatePermission(true, true)' ref='write'></i>
  </div>
</template>

<script>
export default {
  name: 'ThePermSwitch',
  props: {
    roleGuid: null,
    fieldGuid: null,
    stateGuid: null
  },
  data: () => ({}),
  computed: {
    read() {
      const permission = this.$store.state.workflow.permissions.find(
        perm => perm.roleGuid === this.roleGuid
          && perm.fieldGuid === this.fieldGuid
          && perm.stateGuid === this.stateGuid
      );
      if (permission) return permission.read;
      return null;
    },
    edit() {
      const permission = this.$store.state.workflow.permissions.find(
        perm => perm.roleGuid === this.roleGuid
          && perm.fieldGuid === this.fieldGuid
          && perm.stateGuid === this.stateGuid
      );
      if (permission) return permission.edit;
      return null;
    },
    isVirtual() {
      return this.$store.state.form.fields.find(
        field => field.guid === this.fieldGuid
      ).isVirtual;
    },
    isTab() {
      return this.$store.state.form.fields.find(
        field => field.guid === this.fieldGuid
      ).isTab;
    }
  },
  methods: {
    getHiddenClass() {
      let addedClass = '';
      if (this.isTab) addedClass += ' tab';
      else if (!this.read && !this.edit) addedClass += ' redIcon';
      return `fas fa-ban switch${addedClass}`;
    },
    getReadClass() {
      let addedClass = '';
      if (this.isTab) addedClass += ' tab';
      else if (this.read && !this.edit) addedClass += ' blueIcon';
      return `fas fa-eye switch${addedClass}`;
    },
    getEditClass() {
      let addedClass = '';
      if (this.isTab) addedClass += ' tab';
      else if (this.edit) addedClass += ' greenIcon';
      return `fas fa-pencil-alt switch${addedClass}`;
    },
    dispatchSetStatePermission(read, edit) {
      const args = {
        stateGuid: this.stateGuid,
        roleGuid: this.roleGuid,
        fieldGuid: this.fieldGuid,
        read,
        edit
      };
      this.$store.dispatch('workflow/setStatePermission', args).then(() => {
        const msg = this.$t('workflow.role.permission-set-toast');
        this.$dialog.message.success(
          `<i class="fas fa-pencil-alt"></i> &nbsp ${msg}`
        );
      });
    }
  }
};
</script>

<style scoped>
.redIcon {
  color: #ff5722;
}
.blueIcon {
  color: #03a9f4;
}
.greenIcon {
  color: #8bc34a;
}
.nobr {
  white-space: nowrap;
}
.switch {
  padding: 0px 4px 0px 4px;
  cursor: pointer;
}

i {
  color: #c0c0c0;
}

.tab {
  color: #555;
}
</style>
