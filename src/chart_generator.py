import plotly.express as px
import plotly.graph_objects as go
import os

def generate_chart_from_instruction(df, config):
    """Generate Plotly chart from dataframe and configuration"""
    
    if df.empty:
        print("❌ No data to chart")
        return
    
    chart_type = config.get("chart_type", "bar")
    x = config.get("x_axis")
    y = config.get("y_axis") 
    color = config.get("color")
    title = config.get("title", "My Chart")

    # Validate columns exist
    if x and x not in df.columns:
        print(f"❌ Column '{x}' not found in data")
        return
    if y and y not in df.columns:
        print(f"❌ Column '{y}' not found in data")
        return

    fig = None
    try:
        if chart_type == "bar":
            fig = px.bar(
                df, 
                x=x, 
                y=y, 
                title=title,
                color_discrete_sequence=[color] if color else None
            )
        elif chart_type == "pie":
            fig = px.pie(
                df, 
                names=x, 
                values=y, 
                title=title
            )
        elif chart_type == "line":
            fig = px.line(
                df, 
                x=x, 
                y=y, 
                title=title,
                color_discrete_sequence=[color] if color else None
            )
        elif chart_type == "histogram":
            fig = px.histogram(
                df,
                x=x,
                title=title,
                color_discrete_sequence=[color] if color else None
            )
        elif chart_type == "scatter":
            fig = px.scatter(
                df,
                x=x,
                y=y,
                title=title,
                color_discrete_sequence=[color] if color else None
            )
        else:
            print(f"❌ Unsupported chart type: {chart_type}")
            return

        if fig is None:
            print("❌ Failed to create chart")
            return

        # Enhance the chart appearance
        fig.update_layout(
            template="plotly_dark",
            title_font_size=20,
            title_x=0.5,
            showlegend=True
        )

        # Save the chart
        filename = f"{chart_type}_chart.html"
        fig.write_html(filename)
        print(f"✅ Chart saved to: {os.path.abspath(filename)}")

    except Exception as e:
        print(f"❌ Chart generation failed: {e}")
        print(f"Chart config: {config}")
        print(f"Data columns: {list(df.columns)}")
        print(f"Data shape: {df.shape}")

def generate_quick_chart(df, chart_type="bar", title="Quick Chart"):
    """Generate a quick chart with automatic column detection"""
    
    if df.empty:
        print("❌ No data to chart")
        return
    
    columns = list(df.columns)
    
    if len(columns) < 1:
        print("❌ No columns found")
        return
    
    # Auto-detect best columns
    if len(columns) >= 2:
        x_col = columns[0]  # First column for x-axis
        y_col = columns[1]  # Second column for y-axis
        
        # Try to find a numeric column for y-axis
        for col in columns[1:]:
            if df[col].dtype in ['int64', 'float64']:
                y_col = col
                break
    else:
        x_col = columns[0]
        y_col = None
    
    config = {
        "chart_type": chart_type,
        "x_axis": x_col,
        "y_axis": y_col,
        "title": title
    }
    
    generate_chart_from_instruction(df, config)
