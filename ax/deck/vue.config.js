
module.exports = {
  outputDir: '../dist/pages',
  assetsDir: 'static',
  baseUrl: '/pages',
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
  runtimeCompiler: false
};
