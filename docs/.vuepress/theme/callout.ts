import type MarkdownIt from 'markdown-it';
import { container } from '@mdit/plugin-container';

export const calloutContainer = (md: MarkdownIt): void => {
  // 注册 question 容器
  md.use(container, {
    name: 'question', // 容器的名称
    openRender: (tokens, index /*, options, env, self */) => {
      const token = tokens[index];
      // 提取 "question" 后面的文本作为自定义标题
      const customTitle = token.info.trim().slice('question'.length).trim();
      
      // 如果 customTitle 非空，则使用 customTitle；否则，使用默认标题
      const title = customTitle || '问题';

      return `<div class="hint-container question">\n<p class="hint-container-title">${title}</p>\n`;
    },
    closeRender: () => '</div>\n',
  });

  // 注册 example 容器
  md.use(container, {
    name: 'example', // 容器的名称
    openRender: (tokens, index /*, options, env, self */) => {
      const token = tokens[index];
      // 提取 "example" 后面的文本作为自定义标题
      const customTitle = token.info.trim().slice('example'.length).trim();
      
      // 如果 customTitle 非空，则使用 customTitle；否则，使用默认标题
      const title = customTitle || '示例';

      return `<div class="hint-container example">\n<p class="hint-container-title">${title}</p>\n`;
    },
    closeRender: () => '</div>\n',
  });
};


