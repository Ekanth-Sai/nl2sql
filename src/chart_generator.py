import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os

def get_chart_suggestions(df):
    if df.empty:
        return []
    
    suggestions = []
    columns = list(df.columns)
    
    numeric_cols = [col for col in columns if pd.api.types.is_numeric_dtype(df[col])]
    
    categorical_cols = []
    for col in columns:
        if not pd.api.types.is_numeric_dtype(df[col]):
            unique_count = df[col].nunique()
            if unique_count <= 20:  
                categorical_cols.append(col)
    
    date_cols = []
    for col in columns:
        if not pd.api.types.is_numeric_dtype(df[col]):
            try:
                sample_val = str(df[col].dropna().iloc[0]) if not df[col].dropna().empty else ""
                if any(char.isdigit() for char in sample_val) and ('-' in sample_val or '/' in sample_val):
                    pd.to_datetime(sample_val)
                    date_cols.append(col)
            except:
                pass
    
    if categorical_cols and numeric_cols:
        suggestions.append({
            'type': 'bar',
            'x': categorical_cols[0],
            'y': numeric_cols[0],
            'reason': f'Categories vs numeric values'
        })

        if df[categorical_cols[0]].nunique() <= 8:
            suggestions.append({
                'type': 'pie',
                'x': categorical_cols[0],
                'y': numeric_cols[0],
                'reason': f'Proportional distribution'
            })
    
    if len(numeric_cols) >= 2:
        suggestions.append({
            'type': 'scatter',
            'x': numeric_cols[0],
            'y': numeric_cols[1],
            'reason': f'Correlation analysis'
        })

    if date_cols and numeric_cols:
        suggestions.append({
            'type': 'line',
            'x': date_cols[0],
            'y': numeric_cols[0],
            'reason': f'Time series trend'
        })
    
    if numeric_cols:
        suggestions.append({
            'type': 'histogram',
            'x': numeric_cols[0],
            'y': None,
            'reason': f'Data distribution'
        })

    if not suggestions and len(columns) >= 2:
        suggestions.append({
            'type': 'bar',
            'x': columns[0],
            'y': columns[1],
            'reason': 'Basic comparison'
        })
    
    return suggestions[:4]  

def generate_chart_from_instruction(df, config):

    if df.empty:
        print("No data to chart")
        return False
    
    chart_type = config.get("chart_type", "bar")
    x = config.get("x_axis")
    y = config.get("y_axis") 
    color = config.get("color")
    title = config.get("title", "My Chart")

    if x and x not in df.columns:
        print(f"Column '{x}' not found in data")
        print(f"Available columns: {list(df.columns)}")
        return False
    
    if y and y not in df.columns and chart_type != "histogram":
        print(f"Column '{y}' not found in data")
        print(f"Available columns: {list(df.columns)}")
        return False

    try:
        if x and y:
            df_clean = df.dropna(subset=[x, y])
        elif x:
            df_clean = df.dropna(subset=[x])
        else:
            df_clean = df.dropna()
        
        if df_clean.empty:
            print("No data remaining after removing missing values")
            return False

        if len(df_clean) > 1000:
            df_clean = df_clean.head(1000)
            print(f"Limited to first 1000 rows for performance")
        
        if chart_type == "pie" and y:
            try:
                df_clean[y] = pd.to_numeric(df_clean[y], errors='coerce')
                df_clean = df_clean.dropna(subset=[y])
            except:
                pass
        
    except Exception as e:
        print(f"Data preprocessing failed: {e}")
        return False

    fig = None
    try:
        if chart_type == "bar":
            fig = px.bar(
                df_clean, 
                x=x, 
                y=y, 
                title=title,
                color_discrete_sequence=['#3498db'] if not color else [color]
            )
            
        elif chart_type == "pie":
            if df_clean[x].nunique() > 15:
                top_categories = df_clean.groupby(x)[y].sum().nlargest(10)
                others_sum = df_clean.groupby(x)[y].sum().drop(top_categories.index).sum()
                
                pie_data = top_categories.to_dict()
                if others_sum > 0:
                    pie_data['Others'] = others_sum
                
                pie_df = pd.DataFrame(list(pie_data.items()), columns=[x, y])
                fig = px.pie(pie_df, names=x, values=y, title=title)
            else:
                fig = px.pie(df_clean, names=x, values=y, title=title)
            
        elif chart_type == "line":
            fig = px.line(
                df_clean, 
                x=x, 
                y=y, 
                title=title,
                color_discrete_sequence=['#e74c3c'] if not color else [color]
            )
            
        elif chart_type == "histogram":
            fig = px.histogram(
                df_clean,
                x=x,
                title=title,
                color_discrete_sequence=['#2ecc71'] if not color else [color],
                nbins=20
            )
            
        elif chart_type == "scatter":
            fig = px.scatter(
                df_clean,
                x=x,
                y=y,
                title=title,
                color_discrete_sequence=['#f39c12'] if not color else [color]
            )
            
        else:
            print(f"Unsupported chart type: {chart_type}")
            return False

        if fig is None:
            print("Failed to create chart")
            return False

        fig.update_layout(
            template="plotly_white",
            title={
                'text': title,
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18}
            },
            font=dict(size=12),
            margin=dict(l=60, r=60, t=80, b=60),
            showlegend=True if chart_type == "pie" else False
        )
        
        if x and chart_type != "pie":
            fig.update_xaxes(title_font_size=14, tickangle=45 if len(str(df_clean[x].iloc[0])) > 10 else 0)
        if y and chart_type not in ["pie", "histogram"]:
            fig.update_yaxes(title_font_size=14)

        if chart_type in ["bar", "scatter", "line"]:
            fig.update_traces(
                hovertemplate=f"<b>{x}</b>: %{{x}}<br><b>{y}</b>: %{{y}}<extra></extra>"
            )
        filename = f"{chart_type}_chart.html"
        fig.write_html(filename)
        
        try:
            png_filename = f"{chart_type}_chart.png"
            fig.write_image(png_filename, width=1200, height=800, scale=2)
            print(f"Chart saved as: {os.path.abspath(filename)}")
            print(f"PNG saved as: {os.path.abspath(png_filename)}")
        except Exception:
            print(f"Chart saved as: {os.path.abspath(filename)}")
            print("Install kaleido for PNG export: pip install kaleido")
        
        return True

    except Exception as e:
        print(f"Chart generation failed: {e}")
        print(f"Debug info:")
        print(f"  Chart type: {chart_type}")
        print(f"  X column: {x}")
        print(f"  Y column: {y}")
        print(f"  Data shape: {df.shape}")
        print(f"  Available columns: {list(df.columns)}")
        
        return False

def generate_quick_chart(df, chart_type="bar", title="Quick Chart"):
    """Generate a quick chart with automatic column detection"""
    
    if df.empty:
        print("No data to chart")
        return False
    
    columns = list(df.columns)
    
    if len(columns) < 1:
        print("No columns found")
        return False
    
    numeric_cols = [col for col in columns if pd.api.types.is_numeric_dtype(df[col])]
    categorical_cols = [col for col in columns if not pd.api.types.is_numeric_dtype(df[col])]
    
    if len(columns) >= 2:
        if categorical_cols and numeric_cols:
            x_col = categorical_cols[0]
            y_col = numeric_cols[0]
        elif len(numeric_cols) >= 2:
            x_col = numeric_cols[0]
            y_col = numeric_cols[1]
        else:
            x_col = columns[0]
            y_col = columns[1]
    else:
        x_col = columns[0]
        y_col = None
    
    config = {
        "chart_type": chart_type,
        "x_axis": x_col,
        "y_axis": y_col,
        "title": title
    }
    
    return generate_chart_from_instruction(df, config)