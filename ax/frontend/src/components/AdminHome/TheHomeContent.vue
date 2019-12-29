<template>
  <div class='global-container'>
    <v-sheet class='sheet-container home-top' elevation='1' light>
      <div class='home-top-logo'>
        <img class='logo' src='@/assets/android-chrome-192x192.png' width='120' />
        <br />
      </div>
      <div v-html='welcome'></div>
      <br />
      <br />
    </v-sheet>

    <div class='cols-div'>
      <v-sheet class='sheet-container home-col' elevation='1' light>
        <h3>
          <i class='fas fa-store'></i> &nbsp; Featured apps
        </h3>
        <hr />
        <div :key='item.repo' @click='openRepo(item)' class='app-box' v-for='item in featuredItems'>
          <div class='icon-box'>
            <i :class='item.icon'></i>
          </div>
          <div class='app-text'>
            <div>{{item.name}}</div>
            <div class='app-repo'>{{item.repo}}</div>
          </div>
        </div>
      </v-sheet>
      <v-sheet class='sheet-container home-col' elevation='1' light>
        <h3>
          <i class='fab fa-medium'></i> &nbsp; Blog posts
        </h3>
        <hr />
        <div :key='item.id' class='feed-item' v-for='item in blogItems'>
          <div class='feed-date'>{{dateLocale(item.pubDate)}}</div>
          <a :href='item.link' target='_blank'>{{ item.title }}</a>
        </div>
      </v-sheet>
      <v-sheet class='sheet-container home-col' elevation='1' light>
        <h3>
          <i class='fab fa-stack-overflow'></i> &nbsp; StackOverflow questions
        </h3>
        <hr />
        <div class='warning-tag'>
          Warning. This feed is for [workflow] tag.
          If someone having 1500+ rating on Stackoverrflow is willing to
          help me creating [ax-workflow] tag, please
          <a
            href='mailto:enf644@gmail.com'
          >contact me</a>
        </div>

        <div :key='item.id' class='feed-item' v-for='item in stackItems'>
          <div class='feed-date'>{{item.author}}</div>
          <a :href='item.link' target='_blank'>{{ item.title }}</a>
        </div>
      </v-sheet>
    </div>
  </div>
</template>

<script>
import { getAxHostProtocol, openInTab } from '@/misc';
import axios from 'axios';
import RSSParser from 'rss-parser';
import i18n from '@/locale';

// How to create stack filter - https://meta.stackexchange.com/questions/105945/stackoverflow-feed-on-specified-tags

export default {
  name: 'admin-toolbar',
  components: {},
  data: () => ({
    parser: null,
    blog: null,
    stackoverflow: null,
    welcome: null,
    featured: []
  }),
  mounted() {
    this.host = getAxHostProtocol();
    this.parser = new RSSParser();
    this.getBlogRss();
    this.getStackRss();
    this.getWelcome();
    this.getFetured();
  },
  computed: {
    blogItems() {
      if (this.blog && this.blog.items) return this.blog.items;
      return [];
    },
    stackItems() {
      if (this.stackoverflow && this.stackoverflow.items)
        return this.stackoverflow.items;
      return [];
    },
    featuredItems() {
      if (this.featured) return this.featured;
      return [];
    }
  },
  methods: {
    dateLocale(dateStr) {
      const dt = new Date(dateStr);
      return i18n.d(dt);
    },
    openRepo(item) {
      const url = `https://github.com/${item.repo}`;
      console.log(url);
      openInTab(url);
    },
    getBlogRss() {
      axios.get(`${this.host}/api/blog_rss`).then(response => {
        this.parser.parseString(response.data, (err, parsed) => {
          this.blog = parsed;
        });
      });
    },
    getStackRss() {
      // stackoverflow_rss
      axios.get(`${this.host}/api/stackoverflow_rss`).then(response => {
        this.parser.parseString(response.data, (err, parsed) => {
          this.stackoverflow = parsed;
        });
      });
    },
    getWelcome() {
      // home_welcome
      axios.get(`${this.host}/api/home_welcome`).then(response => {
        this.welcome = response.data;
      });
    },
    getFetured() {
      // marketplace_featured
      axios.get(`${this.host}/api/marketplace_featured`).then(response => {
        if (
          response &&
          response.data &&
          response.data.data &&
          response.data.data.AxApps
        ) {
          this.featured = response.data.data.AxApps;
        }
      });
    }
  }
};
</script>

<style scoped>
.global-container {
  padding: 10px;
}
.sheet-container {
  margin: 10px;
  padding: 20px;
  border-radius: 2px;
}
.cols-div {
  display: flex;
  flex-direction: row;
}
.home-top {
  display: flex;
  flex-direction: row;
  padding: 20px;
}
.home-top-logo {
  padding: 20px 40px 20px 20px;
}

.home-col {
  width: 33%;
  height: 100%;
}
.feed-item {
  margin-top: 20px;
}
.feed-date {
  font-size: 13px;
  color: #999;
}

.warning-tag {
  font-size: 13px;
  color: #f44336;
}

.icon-box {
  /* background: #2e7d32; */
  /* background: #2196f3; */
  background: #00897b;
  width: 70px;
  height: 70px;
  color: white;
  text-align: center;
  padding-top: 20px;
  border-radius: 2px;
}
.icon-box i {
  font-size: 30px;
  margin: 2px;
}

.app-box {
  display: flex;
  flex-direction: row;
  margin: 20px 0px;
  cursor: pointer;
}
.app-box:hover {
  font-weight: bolder;
}

.app-text {
  padding-left: 20px;
}
.app-repo {
  font-size: 13px;
  color: #999;
}
</style>
