module.exports = {
  outputDir: "./../dist",
  assetsDir: "static",
  devServer: {
    disableHostCheck: true,
    proxy: {
      "/api": {
        target_temp: "http://axy-20-enf644.c9users.io",
        target: "http://127.0.0.1:8080",
        secure: false
      }
    }
  },
  configureWebpack: {
    devtool: "source-map"
  }
};
