
## 核心设计模式

1. **抽象基类**: `MarkdownProcessor` 定义了处理器的基本接口
2. **具体实现**: `RegexProcessor` 和 `PermalinkProcessor` 实现具体功能
3. **批处理器**: `MarkdownBatchProcessor` 管理多个处理器并批量处理文件
4. **工厂模式**: `ProcessorFactory` 提供便捷的处理器创建方法

## 使用示例

### 基本用法
```python
# 创建批处理器
processor = MarkdownBatchProcessor("./docs/notes/")

# 添加处理器
processor.add_processor(
    ProcessorFactory.create_obsidian_regex_processor()
).add_processor(
    ProcessorFactory.create_permalink_processor("/notes/computer-network/")
)

# 执行处理
processor.process_all()
```

### 只执行特定功能
```python
# 只执行正则替换
processor = MarkdownBatchProcessor("./docs/notes/")
processor.add_processor(ProcessorFactory.create_regex_processor())
processor.process_all()

# 只更新 permalink
processor = MarkdownBatchProcessor("./docs/notes/")
processor.add_processor(ProcessorFactory.create_permalink_processor("/notes/"))
processor.process_all()
```

### 自定义正则规则
```python
custom_regex = [
    [r"old_pattern", r"new_replacement"],
    [r"another_pattern", r"another_replacement"]
]

processor = MarkdownBatchProcessor("./docs/notes/")
processor.add_processor(ProcessorFactory.create_regex_processor(custom_regex))
processor.process_all()
```

## 扩展新功能

要添加新功能，只需要：

1. **继承 `MarkdownProcessor`**:
```python
class MyCustomProcessor(MarkdownProcessor):
    def __init__(self, some_config):
        super().__init__("MyCustomProcessor")
        self.config = some_config
    
    def process_file(self, file_path):
        # 你的处理逻辑
        # 记得更新 self.processed_count
        pass
```

2. **添加到工厂类**:
```python
@staticmethod
def create_my_custom_processor(config):
    return MyCustomProcessor(config)
```

3. **使用新处理器**:
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
