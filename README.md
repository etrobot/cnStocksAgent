# 卧龙AI炒家

这是一个基于LangGraph和FastHTML的A股大模型Agent
<img width="819" alt="Screenshot 2024-10-13 at 11 30 29 PM" src="https://github.com/user-attachments/assets/f18758a9-e3c5-4f6d-ace5-5f6eef7624e3">

```mermaid
graph TD;
        __start__([<p>__start__</p>]):::first
        fetchDataNode(获取同花顺连板)
        fetchNewsNode(获取股吧热门话题)
        reviewNode(市场分析)
        recommendNode(推荐个股)
        chatNode(唠嗑)
        __end__([<p>__end__</p>]):::last
        chatNode --> __end__;
        fetchDataNode --> fetchNewsNode;
        fetchNewsNode --> reviewNode;
        recommendNode --> __end__;
        reviewNode --> recommendNode;
        __start__ -.-> fetchDataNode;
        __start__ -.-> chatNode;
```
## 快速开始

1. 重命名`.env_example`为`.env`并填写必要信息。具体说明如下：
   - `BASE_URL`: 填入兼容OpenAI API的大模型URL
   - `OPENAI_KEY`: 填入兼容OpenAI API格式的模型密钥
   - `MODEL`: 指定要使用的模型名称（例如：gpt-3.5-turbo）

2. 创建并激活虚拟环境：
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

3. 安装依赖：
   ```
   pip3 install -r requirements.txt
   ```

4. 运行应用：
   ```
   python app.py
   ```

## 功能特点

- 获取同花顺连板和东财股吧话题
- 支持显示数据源iframe
- 实时流式响应
- Markdown渲染支持
- 自动加载初始问题"最新复盘"

## 项目结构

- `app.py`: 主应用文件，包含FastAPI路由和UI组件
- `graph_reviewer.py`: 包含`reviewAgent`类，负责处理用户查询和生成响应

## 支持

如果您觉得这个项目有帮助，可以考虑给我买杯咖啡：

[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-ffdd00?style=flat&logo=buy-me-a-coffee&logoColor=black)](https://www.paypal.com/paypalme/franklin755)
