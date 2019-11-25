<template>
  <div>
    <div class='approval-row'>
      <AxApprovalStatus :branch='branch' :status='branchStatus' />
      <AxUserChip
        :currentUserEmail='currentUserEmail'
        :email='reviewer'
        :guid='thisUserGuid'
        :shortName='thisUserShortName'
      ></AxUserChip>
      <v-btn @click='openCommentsModal' class='comments-btn' icon small v-if='branch.id'>
        <i class='far fa-comments comment-ico'></i>
      </v-btn>
    </div>

    <div class='parallel-path' v-if='branches && branches.length > 0'>
      <AxApprovalPath
        :allUsers='allUsers'
        :branch='item'
        :currentUserEmail='currentUserEmail'
        :key='item.id'
        @emitChangeStatus='emitChangeStatus'
        @emitSelected='emitSelected'
        class='chip'
        v-for='item in branches'
      ></AxApprovalPath>
    </div>
    <div class='actions' v-if='actionsAvalible'>
      <v-btn @click='openUsersModal()' small text>
        <i class='fas fa-user-plus'></i>
        &nbsp;
        {{$t("types.AxApproval.add-users-btn")}}
      </v-btn>
      <v-btn @click='approve()' small text>
        <i class='fas fa-check approved-color'></i>
        &nbsp;
        {{$t("types.AxApproval.approve-action")}}
      </v-btn>
      <v-btn @click='reject()' small text>
        <i class='fas fa-times rejected-color'></i>
        &nbsp;
        {{$t("types.AxApproval.reject-action")}}
      </v-btn>
      <v-btn @click='question()' small text>
        <i class='fas fa-question question-color'></i>
        &nbsp;
        {{$t("types.AxApproval.question-action")}}
      </v-btn>
    </div>

    <modal :name='`ax-approval-comments-${this.id}`' adaptive class='comments-modal' height='auto'>
      <h1></h1>
      <v-btn :ripple='false' @click='closeCommentsModal' class='close' color='black' icon text>
        <i class='fas fa-times close-ico'></i>
      </v-btn>

      <div class='comments-wrapper'>
        <AxMessages :height='400' :threadGuid='this.id'></AxMessages>
      </div>
    </modal>

    <modal :name='`add-reviwers-${this.id}`' adaptive class='update-form-modal' height='auto'>
      <AxApprovalAddReviwers @close='closeUsersModal' @selected='usersSelected' />
    </modal>
  </div>
</template>

<script>
import AxUserChip from '@/components/AxUserChip.vue';
import AxApprovalPath from '@/components/AxFields/AxApproval/AxApprovalPath.vue';
import AxApprovalAddReviwers from '@/components/AxFields/AxApproval/AxApprovalAddReviwers.vue';
import AxApprovalStatus from '@/components/AxFields/AxApproval/AxApprovalStatus.vue';
import AxMessages from '@/components/AxMessages.vue';

export default {
  name: 'AxApprovalPath',
  components: {
    AxApprovalPath,
    AxUserChip,
    AxApprovalAddReviwers,
    AxApprovalStatus,
    AxMessages
  },
  props: {
    branch: null,
    allUsers: null,
    currentUserEmail: null
  },
  data: () => ({}),
  computed: {
    branches() {
      return this.branch.branches;
    },
    reviewer() {
      return this.branch.reviewer;
    },
    id() {
      return this.branch.id;
    },
    isNotSaved() {
      return this.branch.isNotSaved;
    },
    actionsAvalible() {
      // only if current user is same as revier
      if (this.currentUserEmail === this.reviewer && !this.isNotSaved)
        return true;
      return false;
    },
    thisUser() {
      if (!this.allUsers) return null;
      return this.allUsers.find(user => user.email === this.reviewer);
    },
    thisUserGuid() {
      if (this.thisUser) return this.thisUser.guid;
      return null;
    },
    thisUserShortName() {
      if (this.thisUser) return this.thisUser.shortName;
      return null;
    },
    branchStatus() {
      if (this.branch) return this.branch.status;
      return null;
    }
  },
  watch: {
    branchStatus(newValue) {},
    actionsAvalible(newValue) {},
    reviewer(newValue) {
      console.log(newValue);
    }
  },
  mounted() {},
  methods: {
    openUsersModal() {
      this.$modal.show(`add-reviwers-${this.id}`);
    },
    closeUsersModal() {
      this.$modal.hide(`add-reviwers-${this.id}`);
    },
    openCommentsModal() {
      this.$modal.show(`ax-approval-comments-${this.id}`);
    },
    closeCommentsModal() {
      this.$modal.hide(`ax-approval-comments-${this.id}`);
    },
    usersSelected(usersInfo) {
      const updatedInfo = { ...usersInfo };
      updatedInfo.branchId = this.id;
      this.$emit('emitSelected', updatedInfo);
      this.closeUsersModal();
    },
    emitSelected(userInfo) {
      this.$emit('emitSelected', userInfo);
    },
    async approve() {
      const res = await this.$dialog.prompt({
        text: this.$t('types.AxApproval.enter-approve-resolution-prompt'),
        actions: {
          true: {
            text: this.$t('types.AxApproval.approve-action')
          }
        }
      });
      if (res) this.emitChangeStatus(4, res);
    },
    async reject() {
      const res = await this.$dialog.prompt({
        text: this.$t('types.AxApproval.enter-reject-resolution-prompt'),
        actions: {
          true: {
            text: this.$t('types.AxApproval.reject-action')
          }
        }
      });
      if (res) this.emitChangeStatus(5, res);
    },
    async question() {
      const res = await this.$dialog.prompt({
        text: this.$t('types.AxApproval.enter-question-prompt'),
        actions: {
          true: {
            text: this.$t('types.AxApproval.question-action')
          }
        }
      });
      if (res) this.emitChangeStatus(3, res);
    },
    emitChangeStatus(newStatus, newResolution) {
      this.$emit('emitChangeStatus', {
        branchId: this.id,
        status: newStatus,
        resolution: newResolution
      });
    }
  }
};
</script>

<style scoped>
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
.chip {
  margin-top: 5px;
}
.actions {
  margin-top: 10px;
}
.approval-row {
  display: flex;
  flex-direction: row;
}
.comment-ico {
  font-size: 16px;
  margin-left: 4px;
}
.comments-btn {
  margin-left: 10px;
}
.approved-color {
  color: #4caf50;
}
.rejected-color {
  color: #f44336;
}
.question-color {
  color: #2196f3;
}
.comments-wrapper {
  padding: 35px 25px 25px 25px;
}
.close {
  position: absolute;
  right: 10px;
  top: 10px;
}
.close-ico {
  font-size: 20px;
}
</style>