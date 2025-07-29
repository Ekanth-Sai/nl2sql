import json
import google.generativeai as genai 
from .config import GOOGLE_API_KEY
from .db_manager import execute_query

genai.configure(api_key = GOOGLE_API_KEY)
model = genai.GenerativeModel('model/gemini-2.5-pro')

def determine_chart_type(query_results, user_intent = ""):
    if not query_results or len(query_results) == 0:
        return None
    
    columns = list(query_results[0].keys())
    num_columns = len(columns)
    num_rows = len(query_results)

    if user_intent.lower() in ['pie', 'pie chart', 'donut']:
        return 'pie'
    elif user_intent.lower() in ['bar', 'bar chart', 'column']:
        return 'bar'
    elif user_intent.lower() in ['histogram', 'distribution']:
        return 'histogram'
    
    if num_columns == 2:
        second_col = columns[1]
        if all(isinstance(row[second_col], (int, float)) for row in query_results):
            if num_rows <= 10:
                return 'pie'
            else:
                return 'bar'
    return 'bar'

def generate_chart_config(query_results, chart_type, title = "Data Visualization"):
    if not query_results:
        return None
    
    columns = list(query_results[0].keys())

    if chart_type == 'pie':
        return generate_pie_chart_config(query_results, columns, title)
    elif chart_type == 'bar':
        return generate_bar_chart_config(query_results, columns, title)
    elif chart_type == 'histogram':
        return generate_histogram_config(query_results, columns, title)
    
    return None

def generate_pie_chart_config(query_results, columns, title):
    if len(columns) < 2:
        return None
    
    name_col = columns[0]
    value_col = columns[1]

    data = []

    for row in query_results:
        data.append({
            'name': str(row[name_col]),
            'y': float(row[value_col]) if row[value_col] is not None else 0
        })

        config = {
        'chart': {
            'type': 'pie',
            'backgroundColor': '#2b2b2b'
        },
        'title': {
            'text': title,
            'style': {
                'color': '#ffffff'
            }
        },
        'plotOptions': {
            'pie': {
                'innerSize': '50%',
                'dataLabels': {
                    'color': '#ffffff'
                }
            }
        },
        'series': [{
            'name': value_col,
            'data': data,
            'showInLegend': True
        }],
        'tooltip': {
            'pointFormat': f'<b>{{point.name}}: {{point.y}}</b>'
        },
        'credits': {
            'enabled': False
        }
    }
        
        return config

def generate_bar_chart_config(query_results, columns, title):
    """Generate bar chart configuration"""
    if len(columns) < 2:
        return None
    
    name_col = columns[0]
    value_col = columns[1]
    
    categories = [str(row[name_col]) for row in query_results]
    data = [float(row[value_col]) if row[value_col] is not None else 0 for row in query_results]
    
    config = {
        'chart': {
            'type': 'column',
            'backgroundColor': '#2b2b2b'
        },
        'title': {
            'text': title,
            'style': {
                'color': '#ffffff'
            }
        },
        'xAxis': {
            'categories': categories,
            'labels': {
                'style': {
                    'color': '#ffffff'
                }
            }
        },
        'yAxis': {
            'title': {
                'text': value_col,
                'style': {
                    'color': '#ffffff'
                }
            },
            'labels': {
                'style': {
                    'color': '#ffffff'
                }
            }
        },
        'series': [{
            'name': value_col,
            'data': data,
            'color': '#7cb5ec'
        }],
        'tooltip': {
            'pointFormat': f'<b>{{series.name}}: {{point.y}}</b>'
        },
        'credits': {
            'enabled': False
        }
    }
    
    return config

def generate_histogram_config(query_results, columns, title):
    """Generate histogram configuration"""
    if len(columns) < 1:
        return None
    
    # For histogram, we'll use the first numeric column
    numeric_col = None
    for col in columns:
        if all(isinstance(row[col], (int, float)) for row in query_results if row[col] is not None):
            numeric_col = col
            break
    
    if not numeric_col:
        return None
    
    # Create bins for histogram
    values = [float(row[numeric_col]) for row in query_results if row[numeric_col] is not None]
    
    # Simple binning logic
    min_val = min(values)
    max_val = max(values)
    num_bins = min(10, len(values) // 2)  # Reasonable number of bins
    
    if num_bins < 2:
        num_bins = 2
    
    bin_width = (max_val - min_val) / num_bins
    bins = []
    
    for i in range(num_bins):
        bin_start = min_val + i * bin_width
        bin_end = min_val + (i + 1) * bin_width
        bin_center = (bin_start + bin_end) / 2
        
        count = sum(1 for val in values if bin_start <= val < bin_end)
        if i == num_bins - 1:  # Include max value in last bin
            count = sum(1 for val in values if bin_start <= val <= bin_end)
        
        bins.append({
            'name': f'{bin_start:.1f}-{bin_end:.1f}',
            'x': bin_center,
            'y': count
        })
    
    config = {
        'chart': {
            'type': 'column',
            'backgroundColor': '#2b2b2b'
        },
        'title': {
            'text': f'{title} - Distribution of {numeric_col}',
            'style': {
                'color': '#ffffff'
            }
        },
        'xAxis': {
            'title': {
                'text': numeric_col,
                'style': {
                    'color': '#ffffff'
                }
            },
            'labels': {
                'style': {
                    'color': '#ffffff'
                }
            }
        },
        'yAxis': {
            'title': {
                'text': 'Frequency',
                'style': {
                    'color': '#ffffff'
                }
            },
            'labels': {
                'style': {
                    'color': '#ffffff'
                }
            }
        },
        'series': [{
            'name': 'Frequency',
            'data': [bin_data['y'] for bin_data in bins],
            'color': '#90ed7d'
        }],
        'tooltip': {
            'pointFormat': '<b>Count: {point.y}</b>'
        },
        'credits': {
            'enabled': False
        }
    }
    
    return config

def generate_chart_from_query(sql_query, chart_type = None, user_intenr = "", title = "Data Visualization"):
    results = execute_query(sql_query, fetch_results=True)
    
    if not results or results is False:
        print("No data retrieved from query or query failed")
        return None
    
    # Determine chart type if not specified
    if not chart_type:
        chart_type = determine_chart_type(results, user_intent)
    
    if not chart_type:
        print("Could not determine appropriate chart type")
        return None
    
    # Generate chart configuration
    chart_config = generate_chart_config(results, chart_type, title)
    
    return chart_config

def generate_html_with_chart(chart_config, filename="chart.html"):
    """
    Generate HTML file with Highcharts visualization
    """
    if not chart_config:
        return False
    
    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Data Visualization</title>
    <script src="https://code.highcharts.com/highcharts.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #1a1a1a;
        }}
        #container {{
            width: 100%;
            height: 500px;
        }}
    </style>
</head>
<body>
    <div id="container"></div>
    
    <script>
        Highcharts.chart('container', {json.dumps(chart_config, indent=2)});
    </script>
</body>
</html>
"""
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_template)
        print(f"Chart saved as {filename}")
        return True
    except Exception as e:
        print(f"Error saving HTML file: {e}")
        return False

def smart_chart_suggestion(natural_language_query, query_results):
    """
    Use Gemini to suggest the best chart type and title based on the natural language query and results
    """
    if not GOOGLE_API_KEY or not query_results:
        return None, None
    
    columns = list(query_results[0].keys())
    sample_data = query_results[:3]  # First 3 rows as sample
    
    prompt = f"""
    Based on the following natural language query and the SQL results structure, suggest:
    1. The best chart type (pie, bar, or histogram)
    2. An appropriate chart title
    
    Natural Language Query: "{natural_language_query}"
    
    Data Structure:
    Columns: {columns}
    Sample Data: {sample_data}
    Total Rows: {len(query_results)}
    
    Respond in this exact format:
    Chart Type: [pie/bar/histogram]
    Title: [suggested title]
    """
    
    try:
        response = model.generate_content(prompt)
        lines = response.text.strip().split('\n')
        
        chart_type = None
        title = None
        
        for line in lines:
            if line.startswith('Chart Type:'):
                chart_type = line.split(':', 1)[1].strip().lower()
            elif line.startswith('Title:'):
                title = line.split(':', 1)[1].strip()
        
        return chart_type, title
    except Exception as e:
        print(f"Error getting chart suggestions: {e}")
        return None, None