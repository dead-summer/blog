---
title: Obsidian笔记上传到博客
createTime: 2025/05/16 20:16:30
permalink: /article/obsidian-to-blog/
---
- 博客类型：Vuepress
- 主题：[vuepress-theme-plume](https://theme-plume.vuejs.press/)

要想从 Obsidian 完美上传到博客，即在 Obsidian 和博客上均不会产生冲突，应当解决如下问题：

1. 重命名源目录名。
2. 隐藏博客所需的文件夹。
3. 匹配博客的 frontmatter（必须）。

其中第 3 条是必须要解决的，剩下则可根据个人习惯选择性修改。

## **重命名文件名**
### **源文件名**

Plume 主题的文档源目录由 `package.json` 文件指定，如：

```json
{
  "scripts": {
    "docs:dev": "vuepress dev docs",
    //                        ^^^^
    "docs:build": "vuepress build docs"
    //                            ^^^^
  }
}
```

因此，在将文件夹名字修改后，还需要将所有的 `docs` 改为目标名称，如 `博客` ：

```json
{
  "scripts": {
    "docs:dev": "vuepress dev 博客",
	 "docs:dev-clean": "vuepress dev 博客 --clean-cache --clean-temp",
	 "docs:build": "vuepress build 博客 --clean-cache --clean-temp",
	 "docs:preview": "http-server 博客/.vuepress/dist"
  }
}
```
### **笔记文件名**

另外，Plume 主题默认笔记系列文件存在 `notes` 文件夹下，其他分类则自定义文件夹。一般而言，在中文博客中，分类名也为中文，此时的 `notes` 略显别扭。因此，可修改为 `笔记`。

在 `博客\.vuepress\notes.ts` 文件中，修改 `dir` 属性：

```ts
export const notes = defineNotesConfig({
  dir: 'notes',
  // 修改为 笔记
  link: '/',
  notes: [demoNote],
})
```
## **隐藏文件夹**

Plume 创建的项目会自带一些 npm 包，并存放于 `node_modules` 文件夹下。在使用 Obsidian 时，该文件夹可能会在一定程度上干扰正常使用。建议使用 [[Hide Folders]] 插件进行屏蔽，以提升使用体验。

## **匹配博客的 frontmatter**