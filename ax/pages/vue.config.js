
module.exports = {
  outputDir: '../dist/pages',
  assetsDir: 'static',
  baseUrl: '/pages',
  css: {
    extract: false
  },
  devServer: {
    disableHostCheck: true,
    // https: true,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:80',
        secure: false
      },
      '/draw_ax': {
        target: 'http://127.0.0.1:80/draw_ax',
        secure: false
      }
    }
  },
  runtimeCompiler: false
};
