<template>
  <div>
    <span class='label'>{{name}}</span>
    <transition enter-active-class='animated shake' leave-active-class='animated fadeOut'>
      <div class='required-error' v-show='errorString'>{{errorString}}</div>
    </transition>
    <div class='hint' v-show='this.options.hint'>{{this.options.hint}} &nbsp;</div>

    <div v-if='noPath'>
      <i class='fas fa-user-slash'></i>
      &nbsp; {{locale("types.AxApproval.no-path")}}
    </div>

    <div class='parallel-path'>
      <AxApprovalPath
        :allUsers='axUsers'
        :branch='item'
        :currentUserEmail='currentUserEmail'
        :key='item.reviewer'
        @emitChangeStatus='changeStatus'
        @emitSelected='emitSelected'
        class='chip'
        v-for='item in currentBranches'
      ></AxApprovalPath>
    </div>

    <div class='actions' v-if='actionsAvalible'>
      <v-btn @click='openUsersModal()' small text>
        <i class='fas fa-user-plus'></i>
        &nbsp;
        {{locale("types.AxApproval.add-users-btn")}}
      </v-btn>
    </div>
    <modal adaptive class='update-form-modal' height='auto' name='add-reviwers'>
      <AxApprovalAddReviwers @close='closeUsersModal' @selected='usersSelected' />
    </modal>
  </div>
</template>

<script>
import i18n from '@/locale';
import gql from 'graphql-tag';
import apolloClient from '@/apollo.js';
import uuid4 from 'uuid4';
import AxApprovalPath from '@/components/AxFields/AxApproval/AxApprovalPath.vue';
import AxApprovalAddReviwers from '@/components/AxFields/AxApproval/AxApprovalAddReviwers.vue';

export default {
  name: 'AxApproval',
  props: {
    name: null,
    dbName: null,
    tag: null,
    options: null,
    value: null,
    isRequired: null,
    isReadonly: null
  },
  components: { AxApprovalPath, AxApprovalAddReviwers },
  data: () => ({
    currentValue: null,
    errors: [],
    axUsers: [],
    currentUserEmail: null,
    tree: null,
    root: null
  }),
  computed: {
    currentBranches() {
      if (this.currentValue && this.currentValue.branches)
        return this.currentValue.branches;
      return [];
    },
    actionsAvalible() {
      // only if current user is initiator
      if (!this.currentValue || !this.currentValue.initiator) return true;
      if (this.currentUserEmail === this.currentValue.initiator) return true;
      return false;
    },
    errorString() {
      if (this.errors.length > 0) return this.errors.join('. ');
      return false;
    },
    errorClass() {
      if (this.errors.length > 0) return 'hr-error';
      return null;
    },
    noPath() {
      if (
        this.currentValue &&
        this.currentValue.branches &&
        this.currentValue.branches.length > 0
      ) {
        return false;
      }
      return true;
    }
  },
  watch: {
    currentValue(newValue, oldValue) {
      this.$emit('update:value', newValue);
    },
    value(newValue) {
      this.currentValue = newValue;
      if (this.currentValue) {
        this.initTree();
      }
    }
  },
  mounted() {
    this.currentValue = this.value;
    if (!this.currentValue) {
      this.currentValue = {
        branches: [],
        modifications: []
      };
    }
    this.initTree();
  },
  methods: {
    locale(key) {
      return i18n.t(key);
    },
    initTree() {
      this.currentValue.modifications = [];
      var TreeModel = require('tree-model');
      this.tree = new TreeModel({
        childrenPropertyName: 'branches'
      });
      this.root = this.tree.parse(this.currentValue);
      this.loadUsers();
    },
    openUsersModal() {
      this.$modal.show('add-reviwers');
    },
    closeUsersModal() {
      this.$modal.hide('add-reviwers');
    },
    isValid() {
      this.errors = [];
      if (this.requiredIsValid()) return true;
      return false;
    },
    requiredIsValid() {
      if (this.isRequired) {
        return true;
      }
      return true;
    },
    collectEmails(reviewerData) {
      if (!reviewerData) return [];
      let retList = [];

      if (reviewerData.branches && reviewerData.branches.length > 0) {
        reviewerData.branches.forEach(rev => {
          if (rev.reviewer) retList.push(rev.reviewer);
          const subRevs = this.collectEmails(rev);
          retList = retList.concat(subRevs);
        });
      }
      return retList;
    },
    loadUsers() {
      const allUserEmails = this.collectEmails(this.currentValue);
      if (!allUserEmails) return false;

      const SEARCH_USERS = gql`
        query($updateTime: String, $emails: String) {
          onlyUsers(updateTime: $updateTime, emails: $emails) {
            guid
            email
            shortName
          }
          currentAxUser(updateTime: $updateTime) {
            guid
            email
            shortName
            name
          }
        }
      `;

      apolloClient
        .query({
          query: SEARCH_USERS,
          variables: {
            emails: allUserEmails,
            updateTime: Date.now()
          }
        })
        .then(data => {
          this.currentUserEmail = data.data.currentAxUser.email;
          this.axUsers = data.data.onlyUsers;
        })
        .catch(error => {
          this.$log.error(`Error in AxApproval -> loadUsers gql => ${error}`);
          this.$dialog.message.error(`${error}`);
        });

      return true;
    },
    usersSelected(usersInfo, branchGuid) {
      usersInfo.users.forEach(user => {
        this.currentValue.branches = this.concatUser(
          this.currentValue.branches,
          user
        );

        // Push node to modifications list
        if (!this.currentValue.modifications)
          this.currentValue.modifications = [];
        this.currentValue.modifications.push({
          type: 'add',
          branchId: null,
          reviewer: user.email
        });

        this.axUsers.push(user);
      });

      this.closeUsersModal();
    },
    emitSelected(usersInfo) {
      const nodeToModify = this.root.first(
        node => node.model.id === usersInfo.branchId
      );
      usersInfo.users.forEach(usr => {
        // Create new node in tree model
        const newNode = this.tree.parse({
          reviewer: usr.email,
          status: 1,
          isNotSaved: true
        });
        nodeToModify.addChild(newNode);

        // Push user to all-users - for visualisation
        this.axUsers.push(usr);

        // Push node to modifications list
        if (!this.root.model.modifications) this.root.model.modifications = [];
        this.root.model.modifications.push({
          type: 'add',
          branchId: usersInfo.branchId,
          reviewer: usr.email
        });
      });
      this.currentValue = this.root.model;
    },
    concatUser(list, user) {
      let thisList = [...list];
      const alreadyAdded = thisList.find(rev => rev.reviewer === user.email);
      if (!alreadyAdded)
        thisList.push({
          reviewer: user.email,
          status: 1,
          isNotSaved: true
        });
      return thisList;
    },
    changeStatus(statusData) {
      // Find node and change status
      const modifiedNode = this.root.first(
        node => node.model.id === statusData.branchId
      );
      modifiedNode.model.status = statusData.status;
      modifiedNode.model.isNotSaved = true;

      // push modification
      if (!this.root.model.modifications) this.root.model.modifications = [];
      this.root.model.modifications.push({
        type: 'status',
        branchId: statusData.branchId,
        status: statusData.status,
        resolution: statusData.resolution
      });
      this.currentValue = this.root.model;
    }
  }
};
</script>

<style scoped>
.chip {
  margin-top: 5px;
}

.label {
  font-size: 13px;
  color: #000;
  opacity: 0.54;
}

.radio-cell {
  text-align: center;
  padding-left: 16px;
}
.x-label {
  text-align: center;
  border-bottom: 1px solid #ccc;
  transition: 0.5s;
}
.y-label {
  text-align: left;
  padding-right: 15px;
  padding-top: 15px;
  border-right: 1px solid #ccc;
  transition: 0.5s;
}
.highlite {
  color: #82b1ff;
}
.required-error {
  margin-top: '5px' !important;
  color: #b71c1c;
  font-size: 12px;
  margin-right: 15px;
}
.hint {
  color: rgba(0, 0, 0, 0.54);
  font-size: 12px;
  margin-top: '5px' !important;
}

.sequence-path {
  margin-top: 20px;
  border-left: 1px dashed #ccc;
  margin-left: 20px;
  padding-left: 10px;
}

.parallel-path {
  margin-top: 20px;
  border-left: 1px solid #ccc;
  margin-left: 20px;
  padding-left: 10px;
}
.actions {
  margin-top: 10px;
}
</style>
