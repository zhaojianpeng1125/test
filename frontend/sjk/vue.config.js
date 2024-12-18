const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    host: '0.0.0.0',  // 允许所有 IP 地址访问
    port: 8080,       // 设置端口为 8080，或根据需要修改
    open: true,       // 启动时自动打开浏览器
    https: false,     // 如果你没有配置 https，可以设置为 false
    disableHostCheck: true,  // 允许所有的 Host 请求
  }
})
