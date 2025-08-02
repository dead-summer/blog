# Markdown 批处理器

一个强大且可扩展的 Markdown 文件批处理工具，支持多种文件处理功能，如正则替换、Permalink 生成、Obsidian 图片转换等。

## 功能特性

- 🔄 **正则表达式批量替换**
- 🔗 **AI 驱动的 Permalink 自动生成**
- 🖼️ **Obsidian 图片格式转 HTML**
- 📁 **内容自动包装到折叠块**
- 🏗️ **模块化设计，易于扩展**
- 📊 **详细的处理统计信息**
- ⚡ **批量处理，高效可靠**

## 安装依赖

```bash
pip install openai python-dotenv pyyaml regex
```

## 环境配置

创建 `.env` 文件并配置 API 密钥（用于 Permalink 生成）：

```env
SILICONFLOW_API_KEY=your_api_key_here
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1
```

## 核心设计模式

1. **抽象基类**: `MarkdownProcessor` 定义了处理器的基本接口
2. **具体实现**: 各种专用处理器实现具体功能
3. **批处理器**: `MarkdownBatchProcessor` 管理多个处理器并批量处理文件
4. **工厂模式**: `ProcessorFactory` 提供便捷的处理器创建方法

## 处理器详细介绍

### 1. RegexProcessor - 正则表达式处理器

用于批量执行正则表达式替换操作。

**功能**: 
- 对文件内容执行多个正则表达式替换
- 统计替换次数
- 支持复杂的正则模式

**使用示例**:
```python
# 自定义正则规则
regex_rules = [
    [r"old_pattern", r"new_replacement"],
    [r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>'],  # Markdown链接转HTML
    [r"~~([^~]+)~~", r"<del>\1</del>"]  # 删除线转HTML
]

processor = MarkdownBatchProcessor("./docs")
processor.add_processor(ProcessorFactory.create_regex_processor(regex_rules))
processor.process_all()
```

### 2. PermalinkProcessor - AI 智能 Permalink 生成器

使用 AI 模型自动为 Markdown 文件生成 SEO 友好的 permalink。

**功能**:
- 基于文件名自动生成英文 slug
- 更新 YAML front matter 中的 permalink 字段
- 支持多种 AI 模型（默认使用 Qwen2.5-7B-Instruct）

**配置参数**:
- `prefix`: permalink 前缀路径
- `provider`: API 提供商前缀（默认 "SILICONFLOW_"）
- `model`: 使用的 AI 模型

**使用示例**:
```python
processor = MarkdownBatchProcessor("./docs/notes")
processor.add_processor(
    ProcessorFactory.create_permalink_processor("/notes/computer-network/")
)
processor.process_all()
```

**处理效果**:
```yaml
# 处理前
---
title: "2.6 信道复用技术"
---

# 处理后
---
title: "2.6 信道复用技术"
permalink: /notes/computer-network/2-6-channel-multiplexing-technology/
---
```

### 3. ObsidianImageToHtmlProcessor - Obsidian 图片转换器

将 Obsidian 的图片语法转换为标准 HTML img 标签。

**功能**:
- 转换 `![[image.png]]` 为 HTML img 标签
- 支持宽度设置 `![[image.png|500]]`
- 自动添加居中样式和 alt 属性
- 智能宽度调整（Obsidian 宽度 × 1.5 适配网页显示）

**配置参数**:
- `default_width`: 默认图片宽度（默认 750px）
- `img_base_path`: 图片基础路径

**使用示例**:
```python
processor = MarkdownBatchProcessor("./docs")
processor.add_processor(
    ProcessorFactory.create_obsidian_html_processor(
        default_width=800, 
        img_base_path="./assets/images"
    )
)
processor.process_all()
```

**转换效果**:
```markdown
# 转换前
![[network-topology.png|500]]

# 转换后
<img src="./network-topology.png" alt="network-topology" width="750" style="display: block; margin: auto;">
```

### 4. DetailsWrapperProcessor - 内容折叠包装器

将指定内容区域包装到 HTML `<details>` 折叠块中，常用于隐藏题解或详细内容。

**功能**:
- 灵活的内容区域选择
- 自动跳过已包装的内容
- 自定义折叠提示文本
- 支持 YAML front matter 自动检测

**配置参数**:
- `start_marker`: 开始位置标记
  - `"auto_yaml_end"`: 自动从 YAML front matter 结束后开始
  - `None`: 从文档开头开始
  - 自定义字符串: 指定开始标记
- `end_marker`: 结束位置标记（None 表示到文档结尾）
- `summary_text`: 折叠块的提示文本

**使用示例**:
```python
# 包装题解内容
processor = MarkdownBatchProcessor("./docs/leetcode")
processor.add_processor(
    ProcessorFactory.create_details_wrapper_processor(
        start_marker="## **思路**",
        summary_text="北海啊，要多想！"
    )
)
processor.process_all()

# 包装整篇文档（除了 front matter）
processor.add_processor(
    ProcessorFactory.create_details_wrapper_processor(
        start_marker="auto_yaml_end",
        summary_text="点击展开内容"
    )
)
```

**包装效果**:

- 包装前
    ```markdown
    ---
    title: "算法题解"
    ---

    ## **思路**
    这道题需要使用动态规划...

    ## 代码实现
    ```

- 包装后
    ```markdwon
    ---
    title: "算法题解"
    ---

    <details>
    <summary>北海啊，要多想！</summary>

    ## **思路**
    这道题需要使用动态规划...

    ## 代码实现

    </details>
    ```

## 使用示例

### 基本用法
```python
from markdown_processor import MarkdownBatchProcessor, ProcessorFactory

# 创建批处理器
processor = MarkdownBatchProcessor("./docs/notes/")

# 链式添加多个处理器
processor.add_processor(
    ProcessorFactory.create_obsidian_html_processor()
).add_processor(
    ProcessorFactory.create_permalink_processor("/notes/computer-network/")
).add_processor(
    ProcessorFactory.create_details_wrapper_processor()
)

# 执行处理
processor.process_all()
```

### 只执行特定功能
```python
# 只执行图片转换
processor = MarkdownBatchProcessor("./docs/notes/")
processor.add_processor(
    ProcessorFactory.create_obsidian_html_processor(default_width=600)
)
processor.process_all()

# 只更新 permalink
processor = MarkdownBatchProcessor("./docs/notes/")
processor.add_processor(
    ProcessorFactory.create_permalink_processor("/notes/")
)
processor.process_all()
```

### 自定义文件过滤器
```python
# 只处理特定目录下的文件
processor = MarkdownBatchProcessor("./docs")
processor.set_file_filter(
    lambda filename: filename.endswith('.md') and 'draft' not in filename
)
processor.add_processor(ProcessorFactory.create_obsidian_html_processor())
processor.process_all()
```

### 复合处理流程
```python
def process_blog_content():
    """处理博客内容的完整流程"""
    
    # 第一步：转换图片格式
    step1 = MarkdownBatchProcessor("./docs")
    step1.add_processor(ProcessorFactory.create_obsidian_html_processor())
    step1.process_all()
    
    # 第二步：生成 permalinks
    step2 = MarkdownBatchProcessor("./docs/posts")
    step2.add_processor(ProcessorFactory.create_permalink_processor("/posts/"))
    step2.process_all()
    
    # 第三步：包装特定内容
    step3 = MarkdownBatchProcessor("./docs/leetcode")
    step3.add_processor(
        ProcessorFactory.create_details_wrapper_processor(
            start_marker="## 解题思路",
            summary_text="查看解题思路"
        )
    )
    step3.process_all()

if __name__ == "__main__":
    process_blog_content()
```

## 扩展新功能

要添加新功能，只需要：

### 1. 继承 `MarkdownProcessor`
```python
class MyCustomProcessor(MarkdownProcessor):
    def __init__(self, some_config):
        super().__init__("MyCustomProcessor")
        self.config = some_config
        self.custom_stats = 0
    
    def process_file(self, file_path):
        """处理单个文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 你的处理逻辑
        modified = self.do_custom_processing(content)
        
        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.processed_count += 1
            self.custom_stats += 1
            return True
        
        return False
    
    def get_stats(self):
        """获取处理统计信息"""
        stats = super().get_stats()
        stats["custom_stats"] = self.custom_stats
        return stats
    
    def do_custom_processing(self, content):
        # 实现你的自定义处理逻辑
        return content
```

### 2. 添加到工厂类
```python
@staticmethod
def create_my_custom_processor(config):
    return MyCustomProcessor(config)
```

### 3. 使用新处理器
```python
processor.add_processor(ProcessorFactory.create_my_custom_processor(config))
```

## 主要优势

- **模块化**: 每个功能独立，易于维护
- **可扩展**: 新功能只需继承基类
- **灵活组合**: 可以任意组合不同的处理器
- **统计信息**: 自动统计处理结果
- **错误处理**: 单个文件出错不影响整体处理
- **链式调用**: 支持流畅的 API 调用
