/**
 * @see https://theme-plume.vuejs.press/config/navigation/ 查看文档了解配置详情
 *
 * Navbar 配置文件，它在 `.vuepress/plume.config.ts` 中被导入。
 */

import { defineNavbarConfig } from 'vuepress-theme-plume'

export default defineNavbarConfig([
  { text: '首页', link: '/' },
  { text: '博客', link: '/blog/' },
  { text: '标签', link: '/blog/tags/' },
  { text: '归档', link: '/blog/archives/' },
  {
    text: '笔记',
    items: [
      { text: '黑马程序员SpringBoot', link: '/notes/HMSpringBoot/README.md' },
      { text: '黑马程序员Redis', link: '/notes/HMRedis/README.md' },
      { text: '湖科大计算机网络', link: '/notes/HNUSTComputerNetwork/README.md' },
      { text: '廖雪峰Java', link: '/notes/LXFJava/README.md' },
      { text: 'LeetCode代码微光集', link: '/notes/leetcode/README.md' },
    ]
  },
])
