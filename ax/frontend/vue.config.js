// const Visualizer = require('webpack-visualizer-plugin');
const VuetifyLoaderPlugin = require('vuetify-loader/lib/plugin');
const MonocoEditorPlugin = require('monaco-editor-webpack-plugin');
const TerserPlugin = require('terser-webpack-plugin');
const webpack = require('webpack');

module.exports = {
  outputDir: '../dist/ax',
  assetsDir: 'static',
  css: {
    extract: false
  },
  devServer: {
    disableHostCheck: true,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8080',
        secure: false
      }
    }
  },
  runtimeCompiler: false,
  configureWebpack: () => {
    const conf = {
      // devtool: 'source-map',
      output: {
        filename: 'static/js/ax-bundle.js'
      },
      // optimization: {
      //   // splitChunks: false,
      //   minimizer: [new TerserPlugin()],
      //   minimize: true,
      // },
      // module: {
      //   rules: []
      // },
      plugins: [
        new webpack.optimize.LimitChunkCountPlugin({
          maxChunks: 1
        }),
        // new Visualizer(),
        new VuetifyLoaderPlugin(),
        new MonocoEditorPlugin({
          languages: ['json', 'python', 'markdown', 'yaml']
        })
      ]
    };

    if (process.env.NODE_ENV === 'production') {
      // mutate config for production...
    } else {
      // delete conf.optimization.splitChunks;
      // conf.optimization.delete('splitChunks');
      conf.optimization.minimize = false;
    }

    return conf;
  },
  filenameHashing: false,
  chainWebpack: config => {
    config.optimization.delete('splitChunks');
  }
};
