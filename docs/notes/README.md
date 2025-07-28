---
pageLayout: home
title: 笔记
icon: /images/memorandum.svg
pageClass: page-notes
config:
  -
    type: doc-hero
    hero:
      name: 笔记
      tagline: 无限进步。
      image: /images/memorandum.svg

  -
    type: features
    features:
      -
        title: Math Notes
        icon: noto:notebook
        details: 研究生期间的数学学习笔记。
        link: https://dead-summer.github.io/math-notes/
      
      -
        title: LeetCode 代码微光集
        icon: devicon:leetcode
        details: LeetCode 刷题记录
        link: ./LeetCode代码微光集/README.md
  -
    type: custom
permalink: /notes/
createTime: 2024/06/20 22:02:04
---

<style>
.page-notes {
  --vp-home-hero-name-color: transparent;
  --vp-home-hero-name-background: linear-gradient(120deg, #ff8736 30%, #ffdf85);
  --vp-home-hero-image-background-image: linear-gradient(
    45deg,
    rgb(255, 246, 215) 50%,
    rgb(239, 216, 177) 50%
  );
  --vp-home-hero-image-filter: blur(44px);
}

[data-theme="dark"] .page-notes {
  --vp-home-hero-image-background-image: linear-gradient(
    45deg,
    rgba(255, 246, 215, 0.07) 50%,
    rgba(239, 216, 177, 0.15) 50%
  );
}
</style>