from fasthtml.common import Titled, Form, Group, Input, Button, Div, H3, P, Script, EventStream, sse_message, Details, Summary, serve, fast_app, Iframe, Template, Style
from fasthtml.components import Zero_md
from graph_reviewer import reviewAgent
from asyncio import sleep

hdrs = (
    Script(src="https://unpkg.com/htmx-ext-sse@2.2.1/sse.js"),
    Script(type="module", src="https://cdn.jsdelivr.net/npm/zero-md@3?register")
)
app, rt = fast_app(hdrs=hdrs)

@rt("/")
def get():
    return Titled("AI短线复盘(纯属娱乐)",
        Form(method="post", action="/query", hx_post="/query", hx_target="#response-container")(
            Group(
                Input(name="user_query", placeholder="For example, how many 'r' are in the word 'strawberry'?"),
                Button("Go", type="submit")
            )
        ),
        Div(id="response-container", 
                             hx_ext="sse", 
                             sse_connect="",  # SSE connection path will be dynamically set
                             sse_close="close",
                             hx_swap="beforeend", 
                             sse_swap="message")
    )

@rt("/query")
def post(user_query: str):
    return Div(id="response-container", 
            hx_ext="sse", 
            sse_connect=f"/query-stream?query={user_query}", 
            sse_close="close",
            hx_swap="beforeend",
            sse_swap="message"
        )

async def response_generator(user_query: str):
    app = reviewAgent()
    if not user_query:
        yield 'event: close\ndata:\n\n'
        return
        
    try:
        for node in app.stream({"data": user_query}):
            result = list(node.values())[0]
            if 'review' in result:
                yield sse_message(Details(
                    Summary("Review"),
                    render_md(result['review']),
                    open=True
                ))
            
            await sleep(0.1)
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
