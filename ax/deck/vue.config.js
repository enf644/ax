
module.exports = {
  outputDir: '../dist/deck',
  assetsDir: 'static',
  baseUrl: '/deck',
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
