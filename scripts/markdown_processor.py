# -*- coding: utf-8 -*-

import os
import re
import regex
import yaml
from openai import OpenAI
from dotenv import load_dotenv
import sys
from abc import ABC, abstractmethod


class MarkdownProcessor(ABC):
    """Markdown 处理器抽象基类"""
    
    def __init__(self, name):
        self.name = name
        self.processed_count = 0
    
    @abstractmethod
    def process_file(self, file_path):
        """处理单个文件的抽象方法"""
        pass
    
    def get_stats(self):
        """获取处理统计信息"""
        return {"processor": self.name, "processed_count": self.processed_count}


class RegexProcessor(MarkdownProcessor):
    """正则表达式处理器"""
    
    def __init__(self, regex_list):
        super().__init__("RegexProcessor")
        self.regex_list = regex_list
        self.total_replacements = 0
    
    def process_file(self, file_path):
        """对单个文件应用正则替换"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        file_replacements = 0
        for pattern, replacement in self.regex_list:
            content, num = regex.subn(pattern, replacement, content)
            file_replacements += num
        
        print(f'{file_path}: 替换 {file_replacements} 处')
        
        if file_replacements > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.processed_count += 1
            self.total_replacements += file_replacements
        
        return file_replacements > 0
    
    def get_stats(self):
        """获取处理统计信息"""
        stats = super().get_stats()
        stats["total_replacements"] = self.total_replacements
        return stats


class PermalinkProcessor(MarkdownProcessor):
    """Permalink 处理器"""
    
    def __init__(self, prefix, provider="SILICONFLOW_", model="Qwen/Qwen2.5-7B-Instruct"):
        super().__init__("PermalinkProcessor")
        self.prefix = prefix
        self.provider = provider
        self.model = model
        self.client = self._setup_client()
    
    def _setup_client(self):
        """设置 OpenAI 客户端"""
        load_dotenv()
        api_key = os.getenv(self.provider + 'API_KEY')
        base_url = os.getenv(self.provider + 'BASE_URL', None)
        
        if not api_key:
            raise ValueError(f"请在 .env 文件中设置 {self.provider}API_KEY")
        
        return OpenAI(api_key=api_key, base_url=base_url)
    
    def _generate_slug(self, title):
        """从标题生成 URL 友好的 slug"""
        prompt = (
            "Generate an English URL slug from the following title. "
            "The slug must contain only lowercase letters, digits and hyphens; "
            "replace any dots (.) in the title with hyphens. "
            "An example for \"2.6 信道复用技术\" is 2-6-channel-multiplexing-technology."
            "For this example, your answer should be \"2-6-channel-multiplexing-technology\"."
            "Please respond in English only and return **only** the slug without any extra text.\n\n"
            f"Title: {title}\n\n"
            "Slug:"
        )
        
        response = self.client.completions.create(
            model=self.model,
            prompt=prompt,
            max_tokens=512,
            temperature=0.3,
            n=1,
            stop=["\n"]
        )
        return response.choices[0].text.strip()
    
    def process_file(self, file_path):
        """更新单个文件的 permalink"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 匹配文件开头的 YAML 前置元数据
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if not match:
            return False  # 无 YAML 前置，跳过
        
        yaml_content = match.group(1)
        md_body = content[match.end():]
        
        # 解析 YAML
        meta = yaml.safe_load(yaml_content)
        title = os.path.basename(file_path)[:-3]
        if not title:
            return False  # 无 title，则无法生成 slug
        
        # 生成 slug 并更新 permalink
        slug = self._generate_slug(title)
        new_permalink = self.prefix.rstrip('/') + '/' + slug + '/'
        meta['permalink'] = new_permalink
        
        # 重建文件内容
        new_yaml = yaml.dump(meta, allow_unicode=True, sort_keys=False).strip()
        new_content = f"---\n{new_yaml}\n---\n\n{md_body}"
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"已更新 {file_path} 的 permalink -> {new_permalink}")
        self.processed_count += 1
        return True
    

class ObsidianImageToHtmlProcessor(MarkdownProcessor):
    """Obsidian 图片格式转 HTML 处理器"""
    
    def __init__(self, default_width=750, img_base_path=""):
        super().__init__("ObsidianImageToHtmlProcessor")
        self.default_width = default_width
        self.img_base_path = img_base_path.rstrip('/')
        self.total_replacements = 0
        # 正则表达式：匹配 ![[path|width]] 或 ![[path]]
        self.pattern = re.compile(r'!\[\[([^|\]]+)(\|(\d+))?\]\]')
    
    def _convert_to_html(self, match):
        """将匹配的Obsidian图片格式转换为HTML"""
        image_path = match.group(1)
        width = match.group(3)        # 宽度数字
        
        # 确定宽度(在 Obsidian 中 500 宽度刚好，但是部署到网页后略小，因此获取到的 Obsidian 图片宽度 * 1.5)
        img_width = float(width) * 1.5 if width else str(self.default_width)
        
        # 提取文件名作为alt属性（去掉路径和扩展名）
        alt_text = os.path.splitext(os.path.basename(image_path))[0]
        
        # 生成HTML标签
        html_img = f'<img src="./{image_path}" alt="{alt_text}" width="{img_width}" style="display: block; margin: auto;">'
        
        return html_img
    
    def process_file(self, file_path):
        """处理单个文件，将Obsidian图片格式转换为HTML"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 统计替换次数
            original_content = content
            content = self.pattern.sub(self._convert_to_html, content)
            
            # 计算实际替换次数
            file_replacements = len(self.pattern.findall(original_content))
            
            if file_replacements > 0:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f'{file_path}: 转换 {file_replacements} 个Obsidian图片为HTML格式')
                self.processed_count += 1
                self.total_replacements += file_replacements
                return True
            
            return False
            
        except Exception as e:
            print(f"处理文件 {file_path} 时出错：{e}")
            return False
    
    def get_stats(self):
        """获取处理统计信息"""
        stats = super().get_stats()
        stats["total_replacements"] = self.total_replacements
        return stats

class DetailsWrapperProcessor(MarkdownProcessor):
    """将指定内容包装到 details 块中的处理器"""
    
    def __init__(self, start_marker="auto_yaml_end", end_marker=None, summary_text="北海啊，要多想！"):
        super().__init__("DetailsWrapperProcessor")
        self.start_marker = start_marker  # 开始位置标记，"auto_yaml_end"表示自动从YAML结束后开始，None表示文档开头
        self.end_marker = end_marker      # 结束位置标记，None表示文档结束  
        self.summary_text = summary_text  # 提示词
        self.total_wraps = 0
    
    def process_file(self, file_path):
        """处理单个文件，将指定区域包装到 details 块中"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 如果文件为空，跳过
            if not content.strip():
                return False
            
            # 查找开始和结束位置
            start_pos = 0
            end_pos = len(content)
            
            if self.start_marker == "auto_yaml_end":
                # 自动查找YAML front matter结束位置（第二个---之后）
                first_dash_pos = content.find("---")
                if first_dash_pos == 0:  # 文档确实以---开头
                    # 查找第二个---
                    second_dash_pos = content.find("---", first_dash_pos + 3)
                    if second_dash_pos != -1:
                        # 找到第二个---，从其后的内容开始
                        # 跳过---后的换行符
                        start_pos = second_dash_pos + 3
                        while start_pos < len(content) and content[start_pos] in ['\n', '\r']:
                            start_pos += 1
                    else:
                        print(f"在 {file_path} 中找到YAML开始标记但未找到结束标记，从文档开头开始")
                        start_pos = 0
                else:
                    # 没有YAML front matter，从文档开头开始
                    start_pos = 0
            elif self.start_marker is None:
                start_pos = 0
            elif self.start_marker:
                start_index = content.find(self.start_marker)
                if start_index != -1:
                    # # 以start_marker为开始位置，从start_index开始
                    # start_pos = start_index
                    # 以 start_marker 下一行为开始位置
                    start_pos = content.find("\n", start_index) + 1
                else:
                    print(f"在 {file_path} 中未找到开始标记: {self.start_marker}")
                    return False
            
            if self.end_marker:
                end_index = content.find(self.end_marker, start_pos)
                if end_index != -1:
                    end_pos = end_index + len(self.end_marker)
                else:
                    print(f"在 {file_path} 中未找到结束标记: {self.end_marker}")
                    return False
            
            # 提取要包装的内容
            before_content = content[:start_pos]
            wrap_content = content[start_pos:end_pos]
            after_content = content[end_pos:]
            
            # 检查是否已经被 details 包装过（简单检查）
            if '<details>' in wrap_content or '</details>' in wrap_content:
                print(f"{file_path}: 内容可能已经包含 details 块，跳过")
                return False
            
            # 去除包装内容两端的空白，但保留内部格式
            wrap_content = wrap_content.strip()
            
            # 如果包装内容为空，跳过
            if not wrap_content:
                print(f"{file_path}: 没有找到需要包装的内容")
                return False
            
            # 创建 details 块
            details_content = f"""<details>
<summary>{self.summary_text}</summary>

{wrap_content}

</details>"""
            
            # 重新组合内容
            new_content = before_content + details_content + after_content
            
            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"{file_path}: 已将内容包装到 details 块中")
            self.processed_count += 1
            self.total_wraps += 1
            return True
            
        except Exception as e:
            print(f"处理文件 {file_path} 时出错：{e}")
            return False
    
    def get_stats(self):
        """获取处理统计信息"""
        stats = super().get_stats()
        stats["total_wraps"] = self.total_wraps
        return stats

class MarkdownBatchProcessor:
    """Markdown 批处理器主类"""
    
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.processors = []
        self.file_filter = lambda filename: filename.lower().endswith('.md')
    
    def add_processor(self, processor):
        """添加处理器"""
        if not isinstance(processor, MarkdownProcessor):
            raise TypeError("处理器必须继承自 MarkdownProcessor")
        self.processors.append(processor)
        return self
    
    def set_file_filter(self, filter_func):
        """设置文件过滤器"""
        self.file_filter = filter_func
        return self
    
    def process_all(self):
        """处理所有文件"""
        if not self.processors:
            print("没有配置任何处理器")
            return
        
        processed_files = 0
        
        for dirpath, _, filenames in os.walk(self.root_dir):
            for filename in filenames:
                if self.file_filter(filename):
                    file_path = os.path.join(dirpath, filename)
                    try:
                        for processor in self.processors:
                            processor.process_file(file_path)
                        processed_files += 1
                    except Exception as e:
                        print(f"处理文件 {file_path} 时出错：{e}")
        
        # 输出统计信息
        print(f"\n处理完成! 共处理 {processed_files} 个文件")
        for processor in self.processors:
            stats = processor.get_stats()
            print(f"- {stats['processor']}: 处理了 {stats['processed_count']} 个文件")
            if 'total_replacements' in stats:
                print(f"  总替换次数: {stats['total_replacements']}")


# 便捷的工厂函数和预设配置
class ProcessorFactory:
    """处理器工厂类"""

    @staticmethod
    def create_obsidian_html_processor(default_width, img_base_path):
        """创建 Obsidian 图片转 HTML 处理器"""
        return ObsidianImageToHtmlProcessor(default_width, img_base_path)
    
    @staticmethod
    def create_regex_processor(regex_list):
        """创建正则处理器"""
        return RegexProcessor(regex_list)
    
    @staticmethod
    def create_permalink_processor(prefix):
        """创建 permalink 处理器"""
        return PermalinkProcessor(prefix)

    @staticmethod
    def create_details_wrapper_processor(start_marker, end_marker, summary_text):
        """创建 details 包装处理器
        
        Args:
            start_marker: 开始位置标记
                - "auto_yaml_end": (默认) 自动从YAML front matter结束后开始
                - None: 从文档开头开始
                - 字符串: 自定义开始标记文本
            end_marker: 结束位置标记文本，None表示到文档结尾结束
            summary_text: details 块的提示词
        """
        return DetailsWrapperProcessor(start_marker, end_marker, summary_text)
    

def main():
    """主函数示例"""
    
    # 创建批处理器
    batch_processor = MarkdownBatchProcessor("./docs")

    # 添加处理器
    batch_processor.add_processor(
        ProcessorFactory.create_obsidian_html_processor(default_width=750, img_base_path="./docs")
    )
    
    # 执行处理
    batch_processor.process_all()

    # 创建第二个批处理器
    batch_processor2 = MarkdownBatchProcessor("./docs/notes/Leetcode代码微光集")
    batch_processor2.add_processor(
        ProcessorFactory.create_details_wrapper_processor(
            start_marker="## **思路**",
            end_marker=None,
            summary_text="北海啊，要多想！"
        )
    )
    batch_processor2.process_all()

if __name__ == "__main__":
    main()