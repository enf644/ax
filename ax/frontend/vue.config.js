// const Visualizer = require('webpack-visualizer-plugin');
const VuetifyLoaderPlugin = require('vuetify-loader/lib/plugin');
const MonocoEditorPlugin = require('monaco-editor-webpack-plugin');
const TerserPlugin = require('terser-webpack-plugin');
const webpack = require('webpack');

module.exports = {
  outputDir: '../dist/ax',
  assetsDir: 'static',
  css: {
    extract: false,
    loaderOptions: {
      sass: {
        implementation: require('sass'),
        fiber: require('fibers')
      }
    }
  },
  devServer: {
    disableHostCheck: true,
    // https: true,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8080',
        secure: false
      }
    }
  },
  runtimeCompiler: false,
  configureWebpack: () => {
    let conf = {};

    if (process.env.NODE_ENV === 'production') {
      // --- PRODUCTION CONFIG -----
      conf = {
        // devtool: 'source-map',
        output: {
          filename: 'static/js/ax-bundle.js',
          pathinfo: false
        },
        optimization: {
          minimizer: [new TerserPlugin()],
          minimize: true,
          // removeAvailableModules: false,
          removeEmptyChunks: false,
          splitChunks: false
        },
        module: {
          rules: []
        },
        plugins: [
          new webpack.optimize.LimitChunkCountPlugin({
            maxChunks: 1
          }),
          // new Visualizer(),
          new VuetifyLoaderPlugin(),
          new MonocoEditorPlugin({
            languages: ['json', 'html', 'python', 'markdown', 'yaml']
          })
        ]
      };
    } else {
      // --- DEVELOPMENT CONFIG -----
      // delete conf.optimization.splitChunks;
      // conf.optimization.minimize = false;
      conf = {
        output: {
          pathinfo: false
        },
        optimization: {
          removeAvailableModules: false,
          removeEmptyChunks: false,
          splitChunks: false
        },
        module: {
          rules: []
        },
        plugins: [
          new VuetifyLoaderPlugin(),
          new MonocoEditorPlugin({
            languages: ['json', 'html', 'python', 'markdown', 'yaml']
          })
        ]
      };
    }

    return conf;
  },
  filenameHashing: false,
  chainWebpack: config => {
    config.module
      .rule('vue')
      .use('vue-loader')
      .loader('vue-loader')
      .tap(options => {
        options.prettify = false;
        return options;
      });
    config.optimization.delete('splitChunks');
  }
};
