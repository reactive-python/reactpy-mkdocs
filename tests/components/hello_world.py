from reactpy import component, html, run


@component
def hello_world():
    return html.h1({"id": "hello-world"}, "Hello World!")


run(hello_world)
