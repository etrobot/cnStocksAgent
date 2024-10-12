from fasthtml.common import Titled, Form, Group, Input, Button, Div, H3, P, Script, EventStream, sse_message, Details, Summary, serve, fast_app, Iframe, Template, Style
from fasthtml.components import Zero_md
from graph_reviewer import reviewAgent
from asyncio import sleep

hdrs = (
    Script(src="https://unpkg.com/htmx-ext-sse@2.2.1/sse.js"),
    Script(type="module", src="https://cdn.jsdelivr.net/npm/zero-md@3?register")
)
app, rt = fast_app(hdrs=hdrs)
messages = []
@rt("/")
def get():
    return Titled("AI短线复盘(纯属娱乐)",
        Form(method="post", action="/query", hx_post="/query", hx_target="#response-container")(
            Group(
                Input(name="user_query", placeholder="For example, how many 'r' are in the word 'strawberry'?"),
                Button("Go", type="submit")
            )
        ),
        Div(id="response-container")
    )

@rt("/query")
def post(user_query: str):
    return Div(id="response-container", 
            hx_ext="sse", 
            sse_connect=f"/query-stream?query={user_query}", 
            sse_close="close",
            hx_swap="innerHTML",
            sse_swap="message"
        )

async def response_generator(user_query: str):
    app = reviewAgent()
    if not user_query:
        messages=[{"role": "user", "content": ''}]
    reply = ""
    try:
        async for event in app.astream_events({"messages": messages},version="v2"):
             if event["event"] == "on_chat_model_stream":
                data = event["data"]
                if data["chunk"].content:
                    reply+=data["chunk"].content
                    yield sse_message(render_md(reply))
             if event["event"] == "on_chain_start" and "url" in event["data"]["input"] and "messages" not in event["data"]["input"]:
                yield sse_message(Details(
                    Summary('获取数据 '+event["data"]["input"]["url"]),
                    Iframe(src=event["data"]["input"]["url"], width="100%", height="400px"),
                ))

    except Exception as e:
        yield sse_message(
            H3("错误"),
            P(f"发生错误: {str(e)}")
        )
    
    yield 'event: close\ndata:\n\n'

def render_md(md, css='.markdown-body {background-color: unset !important; color: unset !important;}'):
    css_template = Template(Style(css), data_append=True)
    return Zero_md(css_template, Script(md, type="text/markdown"))

@rt("/query-stream")
async def get(query: str):
    return EventStream(response_generator(query))

serve()
