/**
 * @see https://theme-plume.vuejs.press/config/navigation/ 查看文档了解配置详情
 *
 * Navbar 配置文件，它在 `.vuepress/plume.config.ts` 中被导入。
 */

import { defineNavbarConfig } from "vuepress-theme-plume";

export default defineNavbarConfig([
  { text: "首页", link: "/", icon: "ic:outline-home" },
  { text: "博客", link: "/blog/", icon: "ic:outline-book" },
  { text: "分类", link: "/blog/categories/", icon: "ic:outline-category" },
  { text: "笔记", link: "/notes/", icon: "ic:outline-note-alt" },
]);
