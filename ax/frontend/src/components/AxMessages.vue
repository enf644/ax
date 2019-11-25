<template>
  <div>
    <div v-if='!this.currentUserShortName'>
      <b>{{locale("types.AxComments.no-anon-warning")}}</b>
    </div>

    <div class='all-messages' v-if='this.currentUserShortName'>
      <div :style='{ height: this.height + "px" }' class='scrollBox' ref='scrollBox'>
        <div :key='message.guid' v-for='message in messages'>
          <div class='message-wrapper' v-if='isSelfMessage(message) == false'>
            <div class='message-body'>
              <div>
                <i class='user-avatar fas fa-user-circle'></i>
              </div>
              <div class='speech-bubble'>{{ message.text }}</div>
            </div>
            <div class='author-div'>
              <span class='author'>{{message.author.shortName}}</span>
              <span class='date'>{{formatDate(message.created)}}</span>
            </div>
          </div>
          <!--  -->
          <div class='self-message-wrapper' v-if='isSelfMessage(message)'>
            <div class='self-message-body'>
              <div class='self-speech-bubble'>
                <pre class='pre-class'>{{ message.text }}</pre>
              </div>
              <div>
                <i class='user-avatar fas fa-user-circle'></i>
              </div>
            </div>
            <div class='self-author-div'>
              <span class='date'>{{formatDate(message.created)}}</span>
              <span class='author'>{{message.author.shortName}}</span>
            </div>
          </div>
        </div>
      </div>

      <div class='actions'>
        <div class='action-btn-div'>
          <!-- <v-btn disabled icon>
            <i class='fas fa-paperclip'></i>
          </v-btn>-->
        </div>
        <v-textarea
          :hint='this.hint'
          :label='label'
          @keyup.ctrl.13='sendMessage'
          auto-grow
          class='input-field'
          ref='textarea'
          rows='1'
          v-if='!this.isReadonly'
          v-model='input'
        ></v-textarea>
        <div class='action-btn-div'>
          <v-btn @click='sendMessage' elevation='1' icon>
            <i class='far fa-paper-plane'></i>
          </v-btn>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import i18n from '@/locale';
import apolloClient from '@/apollo';
import gql from 'graphql-tag';
// import CatalogItem from '@/components/CatalogItem.vue';

export default {
  name: 'AxMessages',
  components: {},
  props: {
    height: {
      type: Number,
      default: 350
    },
    threadGuid: null,
    isReadonly: null,
    hint: null,
    inputLabel: null
  },
  data: () => ({
    messages: [],
    errors: [],
    input: null,
    currentUserGuid: null,
    currentUserEmail: null,
    currentUserShortName: null,
    currentUsername: null
  }),
  computed: {
    label() {
      if (this.inputLabel) return this.inputLabel;
      return this.$t('types.AxComments.enter-message');
    }
  },
  watch: {},
  mounted() {
    if (this.threadGuid) {
      this.getMessages();
      this.subscribeToThread();
    }
  },
  methods: {
    isSelfMessage(message) {
      if (message.author.shortName == this.currentUserShortName) return true;
      return false;
    },
    getMessages() {
      const LOAD_MESSAGES = gql`
        query($threadGuid: String!, $updateTime: String) {
          threadMessages(threadGuid: $threadGuid, updateTime: $updateTime) {
            guid
            created
            edited
            authorGuid
            author {
              guid
              name
              shortName
            }
            text
            dataJson
            threadGuid
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
          query: LOAD_MESSAGES,
          variables: {
            threadGuid: this.threadGuid,
            updateTime: Date.now()
          }
        })
        .then(data => {
          if (data.data) {
            this.messages = data.data.threadMessages;
            if (!this.messages) this.messages = [];

            this.currentUserGuid = data.data.currentAxUser.guid;
            this.currentUserEmail = data.data.currentAxUser.email;
            this.currentUserShortName = data.data.currentAxUser.shortName;
            this.currentUsername = data.data.currentAxUser.name;

            this.scrollBox();
          }
        })
        .catch(error => {
          this.$log.error(`Error in AxComments -> getMessages gql => ${error}`);
          this.$dialog.message.error(`${error}`);
        });
    },
    sendMessage() {
      const SEND_MESSAGE = gql`
        mutation(
          $threadGuid: String!
          $text: String!
          $dataJson: String
          $parent: String
        ) {
          createMessage(
            threadGuid: $threadGuid
            text: $text
            dataJson: $dataJson
            parent: $parent
          ) {
            message {
              guid
              created
              edited
              authorGuid
              author {
                guid
                name
                shortName
              }
              text
              dataJson
              threadGuid
            }
            ok
          }
        }
      `;

      apolloClient
        .mutate({
          mutation: SEND_MESSAGE,
          variables: {
            threadGuid: this.threadGuid,
            text: this.input,
            dataJson: null
          }
        })
        .then(data => {
          const newMessage = data.data.createMessage.message;
          const alreadyExists = this.messages.some(
            item => item.guid === newMessage.guid
          );

          if (!alreadyExists) {
            this.messages.push(newMessage);
            this.scrollBox();
          }
          this.input = null;
          this.$refs.textarea.focus();
        })
        .catch(error => {
          this.$log.error(
            `Error in AxComments -> sendMessage apollo client => ${error}`
          );
        });
    },
    subscribeToThread() {
      const THREAD_NOTIFY = gql`
        subscription($threadGuid: String!) {
          threadNotify(threadGuid: $threadGuid) {
            guid
            created
            edited
            authorGuid
            author {
              guid
              name
              shortName
            }
            text
            dataJson
            threadGuid
          }
        }
      `;

      apolloClient
        .subscribe({
          query: THREAD_NOTIFY,
          variables: {
            threadGuid: this.threadGuid
          }
        })
        .subscribe(
          data => {
            const notifyMessage = data.data.threadNotify;
            const alreadyExists = this.messages.some(
              item => item.guid === notifyMessage.guid
            );

            if (!alreadyExists) {
              this.messages.push(notifyMessage);
              this.scrollBox();
            }
          },
          {
            error(error) {
              logger.error(
                `ERRROR in AxComments -> subscribeToThread => ${error}`
              );
            }
          }
        );
    },
    formatDate(dateStr) {
      const dt = new Date(dateStr);
      return i18n.d(dt);
    },
    locale(key) {
      return i18n.t(key);
    },
    scrollBox() {
      setTimeout(() => {
        this.$refs.scrollBox.scrollTop = this.$refs.scrollBox.scrollHeight;
      }, 200);
    }
  }
};
</script>

<style scoped>
.actions {
  display: flex;
  flex-direction: row;
}
.input-field {
  padding-right: 20px;
}
.action-btn-div {
  padding-top: 15px;
}

.speech-bubble {
  position: relative;
  background: #eceff1;
  border-radius: 4px;
  padding: 10px;
  margin-left: 15px;
}

.speech-bubble:after {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  width: 0;
  height: 0;
  border: 15px solid transparent;
  border-right-color: #eceff1;
  border-left: 0;
  border-top: 0;
  margin-top: -0.5px;
  margin-left: -12px;
}

.message-wrapper {
  margin-bottom: 20px;
}

.message-body {
  display: flex;
  flex-direction: row;
}

.self-speech-bubble {
  position: relative;
  background: #e0f7fa;
  border-radius: 4px;
  padding: 10px;
  margin-right: 15px;
}

.self-speech-bubble:after {
  content: '';
  position: absolute;
  right: 0;
  top: 0;
  width: 0;
  height: 0;
  border: 15px solid transparent;
  border-left-color: #e0f7fa;
  border-right: 0;
  border-top: 0;
  margin-top: -0.5px;
  margin-right: -10px;
}

.self-message-wrapper {
  text-align: right;
  margin-bottom: 20px;
}

.self-message-body {
  display: flex;
  flex-direction: row;
  justify-content: flex-end;
}

.author-div {
  font-size: 13px;
  color: #000;
  opacity: 0.54;
  right: 0px;
  margin-left: 45px;
}

.self-author-div {
  font-size: 13px;
  color: #000;
  opacity: 0.54;
  right: 0px;
  margin-right: 45px;
}

.date {
  color: #ccc;
  margin-left: 15px;
  margin-right: 15px;
}

.user-avatar {
  font-size: 30px;
}
.all-messages {
  margin-top: 10px;
}

.scrollBox {
  overflow: auto;
  padding: 10px 30px 10px 30px;
  border: 1px solid #ccc;
  border-radius: 5px;
}
.pre-class {
  font: inherit;
}
</style>