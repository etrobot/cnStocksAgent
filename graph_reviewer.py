import os
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START,END
from langchain_openai import ChatOpenAI
from data_fetcher import guba_topics,uplimits
import dotenv
dotenv.load_dotenv()


class State(TypedDict):
    url: str = ''
    data: str = ''
    review: str = ''


def reviewAgent():

    llm = ChatOpenAI(
            model=os.getenv("MODEL", "gpt-4o-mini"),
            api_key=os.getenv("OPENAI_KEY"),
            base_url=os.getenv("BASE_URL", "https://api.openai.com/v1"),
        )

    graph_builder = StateGraph(State)

    def fetchDataNode(state: State):
        uplimits_data = uplimits.fetch_continuous_up_limit_data()
        return {"data": '\n## 连板统计：\n\n'+uplimits_data,'url':uplimits.REF}

    def fetchNewsNode(state: State):
        guba_topics_data = guba_topics.getTopics()
        return {"data": state['data']+'\n\n## 新闻:\n\n'+guba_topics_data,'url':guba_topics.REF}

    def reviewNode(state: State):
        messages = [
        {
            "role": "system",
            "content":"你是一个A股交易达人，请根据信息从短线交易的角度分析连板个股的题材是悲观避险导致还是整体市场推动的结果，得出复盘结论应该关注哪些方向",
        },
        {"role": "user", "content": state['data']},
        ]
        return {"review":llm.invoke(messages).content}
    
    def recommendNode(state: State):
        messages = [
        {
            "role": "system",
            "content":"你是一个A股交易达人，参考当前行情，根据你的知识储备，挑选有足够的想象空间（新科技/新药/新经济模式等）的成长股和周期股，避开基金经理喜欢的绩优股或大盘股或明星股，推荐三五个可以买入的股票, 股票必须带雪球链接，比如[中芯国际](https://xueqiu.com/S/SH688981),注意链接中6开头是/S/SH,其他是/S/SZ开头",
        },
        {"role": "user", "content": state['review']},
        ]
        return { "review":llm.invoke(messages).content}

    graph_builder.add_node("fetchDataNode", fetchDataNode)
    graph_builder.add_node("fetchNewsNode", fetchNewsNode)
    graph_builder.add_node("reviewNode", reviewNode)
    graph_builder.add_node("recommendNode", recommendNode)

    graph_builder.add_edge(START, "fetchDataNode")
    graph_builder.add_edge("fetchDataNode", "fetchNewsNode")
    graph_builder.add_edge("fetchNewsNode", "reviewNode")
    graph_builder.add_edge("reviewNode", "recommendNode")
    graph_builder.add_edge("recommendNode", END)

    app = graph_builder.compile()
    return app

if __name__ == "__main__":
    reviewAgent().invoke(input={'data':''}, debug=True)
