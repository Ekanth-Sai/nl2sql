import plotly.express as px

def generate_chart_from_instruction(df, config):
    chart_type = config["chart_type"]
    x = config["x_axis"]
    y = config["y_axis"]
    color = config.get("color")
    title = config.get("title", "My Chart")

    fig = None
    try:
        if chart_type == "bar":
            fig = px.bar(df, x=x, y=y, title=title, color_discrete_sequence=[color] if color else None)
        elif chart_type == "pie":
            fig = px.pie(df, names=x, values=y, title=title)
        elif chart_type == "line":
            fig = px.line(df, x=x, y=y, title=title)
    except Exception as e:
        print(f"Chart generation failed: {e}")
        return

    path = f"{chart_type}_chart.html"
    fig.write_html(path)
    print(f"Chart saved to: {path}")
