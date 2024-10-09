from fasthtml.common import *
from graph import generate_response_graph
import time
from asyncio import sleep

# 添加SSE相关的脚本
hdrs = (Script(src="https://unpkg.com/htmx-ext-sse@2.2.1/sse.js"),)
app, rt = fast_app(hdrs=hdrs)

# 在文件顶部添加全局变量声明
current_query = None

@rt("/")
def get():
    response_container = Div(id="response-container")
    return Titled("o1graph: 使用Langgraph创建o1类推理链",
        # ... 保持原有内容不变 ...
        Form(method="post", action="/query", hx_post="/query", hx_target="#response-container")(
            Group(
                Input(name="user_query", placeholder="例如,单词'strawberry'中有多少个'r'?"),
                Button("Go", type="submit")
            )
        ),
        response_container
    )

@rt("/query")
def post(user_query: str):
    global current_query
    current_query = user_query
    return Div(id="response-container", 
            hx_ext="sse", 
            sse_connect="/query-stream", 
            sse_close="close",
            hx_swap="beforeend",
            sse_swap="message"
        )

async def response_generator():
    global current_query
    app = generate_response_graph()
    if not current_query:
        yield 'event: close\ndata:\n\n'
        return
    
    rendered_steps = set()  # 用于跟踪已渲染的步骤
    
    for result in app.stream({"message": current_query}):
        current_node = list(result.keys())[0]
        if 'initialize' in result:
            continue
        elif 'process_step' in result or ('condition_node' in result and 'Final Answer' in result['condition_node']['steps'][-1]):
            steps = result.get('process_step', {}).get('steps') or result['condition_node']['steps']
            for step in steps:
                title, content, thinking_time = step
                step_key = f"{title}:{content[:50]}"  # 创建一个唯一的步骤标识符
                if step_key not in rendered_steps:
                    yield sse_message(
                        Details(
                            Summary(f"{title} ({thinking_time:.2f} 秒)"),
                            P(content)
                        )
                    )
                    rendered_steps.add(step_key)
                    await sleep(0.1)  # 添加小延迟以模拟逐步更新
            
            if 'condition_node' in result:
                final_step = steps[-1]
                yield sse_message(
                    H3("最终答案"),
                    P(final_step[1])
                )
                total_thinking_time = result['condition_node']['total_thinking_time']
                yield sse_message(P(f"总思考时间: {total_thinking_time:.2f} 秒"))
    yield 'event: close\ndata:\n\n'

@rt("/query-stream")
async def get():
    return EventStream(response_generator())

serve()