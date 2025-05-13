# 安全领域论文收集与处理项目

## 项目简介
本项目用于收集网络安全领域顶级会议论文数据，并进行结构化处理与智能标注，支持以下功能：
1. 多源网络爬虫抓取会议论文元数据
2. Excel论文数据清洗与JSON格式转换
3. 基于LLM的论文关键词提取与自动分类

## 文件结构
 ```markdown 
├── web_of_science/          # Web of Science数据处理模块  
│   ├── webofscience_paper_extract_*.py  
│   └── labels.txt           # 分类体系主文件  
├── 4_security_top_conference/  
│   ├── labels.txt           # 修改版分类体系  
│   └── paper_collect/       # Scrapy爬虫项目  
└── 输出文件：  
    ├── *.json               # 原始论文数据  
    ├── *_keywords.json      # 带关键词标注的数据  
    └── *_keywords_only.json # 仅关键词的数据快照  
```
    
## 功能模块
### 1. 网络爬虫模块
包含以下会议数据采集器：
- `css_papers.py` - DBLP平台CCS会议论文采集
- `usenix_papers.py` - USENIX安全会议论文采集
- `ndss_papers.py` - NDSS会议论文采集
- `aaai_papers.py` - AAAI会议安全相关论文采集

### 2. 数据处理模块
- `webofscience_paper_extract_*.py`
  - 支持将Web of Science导出的CCS/SP会议Excel文件转换为JSON格式
  - 提取字段：标题、作者、摘要、年份、DOI

### 3. 智能标注模块
- `llm_labels.py/llm4_labels.py`
  - 使用Qwen大模型自动生成论文关键词
  - 自动匹配网络安全分类体系（见labels.txt）
  - 支持两种模型版本：qwen-plus与qwen3

### 4. 分类体系文件
- `labels.txt` 定义9大核心安全领域及子分类：
  - 网络空间理论
  - 密码学及应用
  - 网络与系统安全
  - 信息内容安全
  - 新兴信息技术安全
  - 数据安全与隐私
  - 人工智能安全
  - 区块链安全
  - 物联网安全

## 环境依赖
```bash
pip install scrapy pandas langchain langchain-community openpyxl tqdm
```

## 使用指南
### 1. 数据采集
```bash
# 运行爬虫（示例：采集USENIX论文）
cd paper_collect
scrapy crawl usenix -o usenix_papers.json
```
或者 从web of science导出的Excel文件转换为JSON格式
```bash
# 运行数据处理脚本
python webofscience_paper_extract_ccs.py
python webofscience_paper_extract_sp.py
```

### 2. 智能标注
```bash
# 配置API密钥（修改llm_labels.py）
export TONGYI_API_KEY=your_api_key

# 执行关键词提取（需选择对应输入文件）
python llm_labels.py  # 处理SP24.json
python llm4_labels.py  # 处理usenix_papers.json
```

## 注意事项
API配置：需在llm_labels.py和llm4_labels.py中配置有效的Tongyi API密钥  
路径配置：确保输入文件路径与脚本中的INPUT_PAPERS_FILE保持一致  
模型选择：根据需求选择合适的Qwen版本（qwen-plus或qwen3） 或者修改代码用其他AI  
分类更新：如需扩展分类体系，需同步修改两个目录下的labels.txt  
数据清洗：原始爬虫数据可能需要人工校验作者字段格式  
