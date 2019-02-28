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
  chainWebpack: config => {
    // config.optimization.delete('splitChunks');
  },
  configureWebpack: {
    devtool: 'source-map',
    output: {
      filename: 'static/js/ax-bundle.js'
    },
    optimization: {
      splitChunks: false
    },
    module: {

      rules: [
      ]
    }
  }
};
