<template>
  <div class='status-wrapper'>
    <!-- 0 - waiting -->
    <!-- <div v-if='status == 0'>
      <v-tooltip bottom>
        <template v-slot:activator='{ on }'>
          <i class='far fa-pause-circle approve-status waiting' v-on='on'></i>
        </template>
        <span>{{locale('types.AxApproval.waiting-status')}}</span>
      </v-tooltip>
    </div>-->

    <!-- 1 - action needed -->
    <!-- <div v-if='status == 1'>
      <v-tooltip bottom>
        <template v-slot:activator='{ on }'>
          <i class='fas fa-stopwatch approve-status action' v-on='on'></i>
        </template>
        <span>{{locale('types.AxApproval.action-status')}}</span>
      </v-tooltip>
    </div>-->

    <!-- 3 - question added -->
    <div v-if='status == 3'>
      <v-tooltip bottom>
        <template v-slot:activator='{ on }'>
          <i class='fas fa-question approve-status question' v-on='on'></i>
        </template>
        <span>
          <b>{{locale('types.AxApproval.question-status')}}</b>
          <br />
          {{resolution}}
        </span>
      </v-tooltip>
    </div>

    <!-- 4 - approved -->
    <div v-if='status == 4'>
      <v-tooltip bottom>
        <template v-slot:activator='{ on }'>
          <i class='fas fa-check approve-status approved' v-on='on'></i>
        </template>
        <span>
          <b>{{locale('types.AxApproval.approved-status')}}</b>
          <br />
          {{resolution}}
        </span>
      </v-tooltip>
    </div>

    <!-- 5 - rejected -->
    <div v-if='status == 5'>
      <v-tooltip bottom>
        <template v-slot:activator='{ on }'>
          <i class='fas fa-times approve-status rejected' v-on='on'></i>
        </template>
        <span>
          <b>{{locale('types.AxApproval.rejected-status')}}</b>
          <br />
          {{resolution}}
        </span>
      </v-tooltip>
    </div>

    <div v-if='this.branch && this.branch.isNotSaved'>
      <v-tooltip bottom>
        <template v-slot:activator='{ on }'>
          <i class='fas fa-exclamation approve-status rejected' v-on='on'></i>
        </template>
        <span>{{locale('types.AxApproval.not-saved-warning')}}</span>
      </v-tooltip>
    </div>
  </div>
</template>

<script>
import i18n from '@/locale';
// import CatalogItem from '@/components/CatalogItem.vue';

export default {
  name: 'AxApprovalStatus',
  props: {
    branch: null
  },
  components: {},
  data: () => ({
    guid: null
  }),
  computed: {
    status() {
      if (this.branch) return this.branch.status * 1;
      return null;
    },
    resolution() {
      if (this.branch && this.branch.resolution) return this.branch.resolution;
      return null;
    }
  },
  watch: {},
  mounted() {},
  methods: {
    locale(key) {
      return i18n.t(key);
    }
  }
};
</script>

<style scoped>
.approve-status {
  font-size: 20px;
  margin-right: 10px;
  margin-top: 4px;
}
.approved {
  color: #4caf50;
}
.rejected {
  color: #f44336;
}
.question {
  color: #2196f3;
}
.waiting {
  color: #607d8b;
}
.action {
  color: #ff9800;
}
.status-wrapper {
  display: flex;
  flex-direction: row;
}
</style>