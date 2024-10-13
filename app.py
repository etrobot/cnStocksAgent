from fasthtml.common import Titled, Form, Group, Input, Button, Div, H3, P, Script, EventStream, sse_message, serve, fast_app, MarkdownJS, Details, Summary, Iframe, Body
from graph_reviewer import reviewAgent

# Add Tailwind CSS and DaisyUI
tlink = Script(src="https://cdn.tailwindcss.com")
sselink = Script(src="https://unpkg.com/htmx-ext-sse@2.2.1/sse.js")
mdjs = MarkdownJS()

app, rt = fast_app(hdrs=(tlink, sselink, mdjs))
messages = []

# ChatMessage component
def ChatMessage(msg_idx, **kwargs):
    msg = messages[msg_idx]
    bubble_class = "bg-teal-300 bg-opacity-20 rounded-lg p-3 max-w-5xl" if msg['role'] == 'user' else 'bg-blue-400 bg-opacity-20 rounded-lg p-3 max-w-5xl'
    chat_class = "flex justify-end mb-4" if msg['role'] == 'user' else 'flex justify-start mb-4'
    return Div(
        Div(
            Div(msg['role'], cls="text-sm text-gray-600 mb-1"),
            Div(msg['content'], id=f"chat-content-{msg_idx}", cls=f"{bubble_class}", **kwargs),
            cls="flex flex-col"
        ),
        id=f"chat-message-{msg_idx}",
        cls=f"{chat_class}",
        hx_swap="beforeend show:bottom"
    )

def get_messages():
    return []

@rt("/")
def get():    
    return Titled("A股大模型Agent",
        Body(
            H3('卧龙AI炒家(纯属娱乐)', cls="text-2xl font-bold mb-4"),
            Div(id="chatlist", cls="h-[73vh] overflow-y-auto border border-gray-300 border-opacity-50 p-2 rounded-lg"),
            Form(
                Group(
                    Input(name="user_query", placeholder="请输入您的问题", id="msg-input", cls="w-full border rounded-lg p-2"),
                    Button(
                        "发送",
                        type="submit",
                        id="send-button",
                        cls="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 whitespace-nowrap",
                    )
                ),
                method="post", action="/send-message", 
                hx_post="/send-message", 
                hx_target="#chatlist", 
                hx_swap="beforeend show:bottom",
                hx_indicator="#send-button",
                cls="flex space-x-2 mt-2"
            ),
            Div(hx_post="/send-message", hx_trigger="load", hx_vals='{"user_query": "最新复盘"}', hx_target="#chatlist", hx_swap="beforeend show:bottom"),
            cls="p-4 max-w-6xl mx-auto"
        )
    )

@rt("/send-message")
async def send_message(user_query:str):
    if not user_query:
        return

    messages.append({"role": "user", "content": user_query})
    user_msg = ChatMessage(len(messages) - 1)
    messages.append({"role": "assistant", "content": ""})
    assistant_msg = ChatMessage(
        len(messages) - 1,
        hx_ext="sse", 
        sse_connect=f"/query-stream?query={user_query}", 
        sse_swap="message",
        hx_swap="beforeend show:bottom",
        sse_close="close",
        sse_error="close"
    )
    return (
        user_msg, 
        assistant_msg,
        Div(hx_trigger="load", hx_post="/disable-button")
    )

@rt("/disable-button")
def disable_button():
    return Script("document.getElementById('send-button').disabled = true;")

async def response_generator(user_query: str):
    app = reviewAgent()
    if not user_query:
        return
    accumulated_content = ""
    accumulating = False
    try:
        async for event in app.astream_events({"messages": messages},version="v2",debug=True):
             if event["event"] == "on_chat_model_stream":
                data = event["data"]
                if data["chunk"].content:
                    if data["chunk"].content.startswith("\n\n"):
                        accumulating = True
                        accumulated_content = data["chunk"].content
                    elif accumulating:
                        accumulated_content += data["chunk"].content
                        if "\n\n" in accumulated_content:
                            parts = accumulated_content.split("\n\n")
                            to_render = "\n\n".join(parts[:-1])
                            yield sse_message(Div(to_render, id="markdown-content", cls="marked"))
                            accumulated_content = parts[-1]
                    else:
                        yield sse_message(data["chunk"].content)
             if event["event"] == "on_chain_start" and "url" in event["data"]["input"] and "messages" not in event["data"]["input"]:
                yield sse_message(Details(
                    Summary('获取数据 '+event["data"]["input"]["url"]),
                    Iframe(src=event["data"]["input"]["url"], width="100%", height="400px"),
                ))

        if accumulated_content:
            yield sse_message(Div(accumulated_content, id="markdown-content", cls="marked"))

    except Exception as e:
        yield sse_message(
            H3("错误"),
            P(f"发生错误: {str(e)}")
        )
    yield sse_message(Script("document.getElementById('send-button').disabled = false;"))  # 重新启用发送按钮    
    yield 'event: close\ndata:\n\n'
    messages[-1]['content'] = accumulated_content

@rt("/query-stream")
async def get(query: str):
    return EventStream(response_generator(query))

serve()
