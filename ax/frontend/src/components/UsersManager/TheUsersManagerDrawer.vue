<template>
  <div>
    <h3>{{$t("users.drawer-users-header")}}:</h3>
    <v-btn @click='gotoAllUsers' data-cy='all-users-btn' small>
      <i class='far fa-user'></i>
      &nbsp; {{$t("users.all-users-btn")}}
    </v-btn>

    <br />
    <br />

    <h3>{{$t("users.drawer-groups-header")}}</h3>
    <div class='groups-tree' data-cy='groups-tree' ref='tree'></div>
    <br />
    <v-btn @click='promptNewGroup' data-cy='create-group-btn' small>
      <i class='fas fa-plus'></i>
      &nbsp; {{$t("users.create-group-btn")}}
    </v-btn>
  </div>
</template>

<script>
import $ from 'jquery';
import 'jstree/dist/jstree.js';
import 'jstree/dist/themes/default/style.css';
import gql from 'graphql-tag';
import apolloClient from '@/apollo';

export default {
  name: 'TheusersManagerDrawer',
  data: () => ({
    treeInitiated: false
  }),
  computed: {
    groups() {
      return this.$store.state.users.groups;
    },
    jsTreeData() {
      const jsTreeData = [];

      this.groups.forEach(group => {
        console.log(group);

        let icon = 'fas fa-users';
        if (group.isAdmin) icon = 'fas fa-users-cog';

        const parent = group.parent || '#';
        const node = {
          id: group.guid,
          parent,
          text: `<i class="${icon}"></i> &nbsp; ${group.shortName}`,
          type: 'default',
          data: {
            shortName: group.shortName
          }
        };
        jsTreeData.push(node);
      });

      return jsTreeData;
    }
  },
  watch: {
    groups(newValue) {
      if (newValue) {
        const tree = $(this.$refs.tree).jstree(true);
        tree.settings.core.data = this.jsTreeData;
        tree.refresh();
      }
    }
  },
  mounted() {
    window.jQuery = $;
    window.$ = $;
    this.loadGroups();
  },
  methods: {
    gotoAllUsers() {
      const url = `/admin/users`;
      if (url != this.$route.fullPath) this.$router.push({ path: url });
    },
    loadGroups() {
      const ALL_GROUPS = gql`
        query($updateTime: String!) {
          allGroups(updateTime: $updateTime) {
            guid
            shortName
            parent
            isAdmin
          }
        }
      `;
      apolloClient
        .query({
          query: ALL_GROUPS,
          variables: {
            updateTime: Date.now()
          }
        })
        .then(data => {
          this.$store.commit('users/setGroups', data.data.allGroups);

          if (!this.treeInitiated) {
            this.initJstree(this.jsTreeData);
          } else {
            const tree = $(this.$refs.tree).jstree(true);
            tree.settings.core.data = this.jsTreeData;
            tree.refresh();
          }
        })
        .catch(error => {
          this.$log.error(
            `Error in TheusersManagerDrawer => loadData apollo client => ${error}`
          );
        });
    },
    initJstree(groupsData) {
      $(this.$refs.tree)
        .on('activate_node.jstree', (e, data) => this.gotoGroup(e, data))
        .jstree({
          core: {
            data: groupsData,
            check_callback() {
              return true;
            }
          },
          plugins: ['types', 'dnd', 'sort'],
          types: {
            default: {
              icon: false,
              valid_children: ['default']
            }
          },
          sort(a, b) {
            return this.get_node(a).data.shortName >
              this.get_node(b).data.shortName
              ? 1
              : -1;
          }
        });
      this.treeInitiated = true;
    },
    gotoGroup(event, data) {
      const url = `/admin/group/${data.node.id}`;
      if (url != this.$route.fullPath) this.$router.push({ path: url });
    },
    async promptNewGroup() {
      const res = await this.$dialog.prompt({
        text: this.$t('users.add-group-prompt'),
        actions: {
          true: {
            text: this.$t('common.confirm')
          }
        }
      });
      if (res) {
        // this.$dialog.message.error(`Wrong group name`);
        this.createNewGroup(res);
      }
    },
    createNewGroup(groupName) {
      const CREATE_NEW_GROUP = gql`
        mutation($shortName: String) {
          createGroup(shortName: $shortName) {
            user {
              guid
              shortName
            }
            ok
            msg
          }
        }
      `;

      apolloClient
        .mutate({
          mutation: CREATE_NEW_GROUP,
          variables: {
            shortName: groupName
          }
        })
        .then(data => {
          if (data.data.createGroup.ok) {
            const msg = this.$t('users.group-created-toast');
            this.$dialog.message.success(
              `<i class="fas fa-plus"></i> &nbsp ${msg}`
            );
            this.loadGroups();
          } else {
            this.$dialog.message.error(this.$t(data.data.createGroup.msg));
          }
        })
        .catch(error => {
          this.$log.error(`Error in createNewGroup gql => ${error}`);
          this.$dialog.message.error(`${error}`);
        });
    }
  }
};
</script>

<style scoped>
</style>
