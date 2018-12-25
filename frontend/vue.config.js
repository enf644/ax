module.exports = {
  outputDir: './../dist',
  assetsDir: 'static',
  devServer: {
    disableHostCheck: true,
    proxy: {
        '/api': {
            target: 'http://axy-20-enf644.c9users.io',
            secure: false
        }
    }    
    
    
  }  
}