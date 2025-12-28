from streamlit_echarts import st_echarts

def render_tech_stack():
    nodes = [
        {"name": "CONFLUENT\nKAFKA + FLINK", "x": 100, "y": 100, "symbolSize": 100, "itemStyle": {"color": "#4ECDC4", "shadowBlur": 20, "shadowColor": "rgba(78, 205, 196, 0.4)"}},
        {"name": "ADK AGENT\nSWARM", "x": 400, "y": 100, "symbolSize": 130, "itemStyle": {"color": "#FF6B6B", "shadowBlur": 30, "shadowColor": "rgba(255, 107, 107, 0.5)"}},
        {"name": "GOOGLE\nBIGQUERY", "x": 700, "y": 100, "symbolSize": 100, "itemStyle": {"color": "#58A6FF", "shadowBlur": 20, "shadowColor": "rgba(88, 166, 255, 0.4)"}},
    ]
    links = [
        {"source": "CONFLUENT\nKAFKA + FLINK", "target": "ADK AGENT\nSWARM", "label": {"show": True, "formatter": "REAL-TIME\nSIGNALS", "color": "#FAFAFA", "fontSize": 11, "fontWeight": "bold"}, "lineStyle": {"width": 4, "curveness": 0.1, "color": "rgba(255,255,255,0.2)"}},
        {"source": "ADK AGENT\nSWARM", "target": "GOOGLE\nBIGQUERY", "label": {"show": True, "formatter": "AUDIT\nTRAIL", "color": "#FAFAFA", "fontSize": 11, "fontWeight": "bold"}, "lineStyle": {"width": 4, "curveness": 0.1, "color": "rgba(255,255,255,0.2)"}},
    ]
    
    option = {
        "backgroundColor": "transparent",
        "series": [{
            "type": "graph",
            "layout": "none",
            "roam": False,
            "label": {"show": True, "position": "inside", "fontSize": 11, "fontWeight": "900", "color": "#0E1117", "lineHeight": 16},
            "edgeSymbol": ["circle", "arrow"],
            "edgeSymbolSize": [6, 12],
            "data": nodes,
            "links": links,
            "lineStyle": {"opacity": 1.0, "width": 3}
        }]
    }
    st_echarts(option, height="250px")

def render_infrastructure_flow():
    nodes = [
        {"name": "Betty's Account", "x": 50, "y": 100, "symbol": "roundRect", "itemStyle": {"color": "#FAFAFA", "borderColor": "#8B949E", "borderWidth": 2}},
        {"name": "Flink Router", "x": 300, "y": 100, "symbol": "roundRect", "itemStyle": {"color": "#4ECDC4", "shadowBlur": 10, "shadowColor": "rgba(78, 205, 196, 0.3)"}},
        {"name": "Quarantine Topic", "x": 550, "y": 100, "symbol": "roundRect", "itemStyle": {"color": "#FF6B6B", "shadowBlur": 10, "shadowColor": "rgba(255, 107, 107, 0.3)"}},
        {"name": "BigQuery Sink", "x": 800, "y": 100, "symbol": "roundRect", "itemStyle": {"color": "#58A6FF", "shadowBlur": 10, "shadowColor": "rgba(88, 166, 255, 0.3)"}},
    ]
    links = [
        {"source": "Betty's Account", "target": "Flink Router"},
        {"source": "Flink Router", "target": "Quarantine Topic", "label": {"show": True, "formatter": "Rerouted", "color": "#FF6B6B"}},
        {"source": "Quarantine Topic", "target": "BigQuery Sink"},
    ]
    
    option = {
        "backgroundColor": "transparent",
        "series": [{
            "type": "graph",
            "layout": "none",
            "symbolSize": [130, 50],
            "label": {"show": True, "color": "#0E1117", "fontWeight": "bold", "fontSize": 12},
            "edgeSymbol": ["none", "arrow"],
            "edgeSymbolSize": [0, 10],
            "data": nodes,
            "links": links,
            "lineStyle": {"width": 4, "color": "#4A5568", "opacity": 0.6}
        }]
    }
    st_echarts(option, height="200px")
