const { defineConfig } = require('@vue/cli-service')
const Dotenv = require('dotenv-webpack');

module.exports = defineConfig({
  transpileDependencies: true,
  configureWebpack: {
    plugins: [
      new Dotenv() // Add dotenv-webpack plugin to load environment variables
    ]
  }
})
