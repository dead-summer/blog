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


class MarkdownBatchProcessor:
    """Markdown 批处理器主类"""
    
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.processors = []
        self.file_filter = lambda filename: filename.lower().endswith('.md') and filename != "README.md"
    
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
    def create_regex_processor(regex_list):
        """创建正则处理器"""
        return RegexProcessor(regex_list)
    
    @staticmethod
    def create_permalink_processor(prefix):
        """创建 permalink 处理器"""
        return PermalinkProcessor(prefix)
    

def main():
    """主函数示例"""
    if len(sys.argv) >= 2:
        directory = sys.argv[1]
    else:
        directory = "./docs/notes/湖科大计算机网络"
    
    # 创建批处理器
    batch_processor = MarkdownBatchProcessor(directory)

    regex_list = [
            # ------------ 查询 ------------ 匹配 ------------
            [r"!\[\[([^|\]]+)(?:\|[^\]]+)?\]\]", r"![](\1)"],  # Obsidian 图片链接转 Markdown
            [r"(?<=!\[[^\]]*\]\([^)]*)\s(?=[^)]*\))", r"%20"]  # 将图片链接中的空格替换为 URL 字符
        ]
    
    # 添加处理器
    batch_processor.add_processor(
        ProcessorFactory.create_regex_processor(regex_list)
    ).add_processor(
        ProcessorFactory.create_permalink_processor("/notes/HNUSTComputerNetwork/")
    )
    
    # 执行处理
    batch_processor.process_all()


if __name__ == "__main__":
    main()