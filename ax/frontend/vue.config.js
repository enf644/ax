const Visualizer = require('webpack-visualizer-plugin');
const VuetifyLoaderPlugin = require('vuetify-loader/lib/plugin');
const MonocoEditorPlugin = require('monaco-editor-webpack-plugin');

module.exports = {
  outputDir: './../dist',
  assetsDir: 'static',
  css: {
    extract: false
  },
  devServer: {
    disableHostCheck: true,
    proxy: {
      '/api': {
        target_temp: 'http://axy-20-enf644.c9users.io',
        target: 'http://127.0.0.1:8080',
        secure: false
      }
    }
  },
  runtimeCompiler: false,
  chainWebpack: () => {
    // config
  },
  configureWebpack: () => {
    const conf = {
      devtool: 'source-map',
      output: {
        filename: 'static/js/ax-bundle.js'
      },
      optimization: {
        splitChunks: false,
        minimize: true
      },
      module: {
        rules: []
      },
      plugins: [
        new Visualizer(),
        new VuetifyLoaderPlugin(),
        new MonocoEditorPlugin({
          languages: ['json', 'python', 'markdown', 'yaml']
        })
      ]
    };

    if (process.env.NODE_ENV === 'production') {
      // mutate config for production...
    } else {
      delete conf.optimization.splitChunks;
      conf.optimization.minimize = false;
    }

    return conf;
  }
};
