colors = {
    "primary":   "#1a4d24",
    "secondary": "#2f9e41",
    "accent":    "#44ad66",
    "alert":     "#cd191e",
    "background": "#f6f6f6",
    "card":      "#FFFFFF",
}

card_style_base = {
    "background": colors["card"],
    "padding": 20,
    "borderRadius": 8,
    "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
    "border": f"1px solid {colors['accent']}"
}

tab_style = {
    "padding": "10px",
    "fontWeight": "bold",
    "border": "1px solid #ddd",
    "background": "#e8f2ec",
    "color": colors["alert"],
}

tab_selected_style = {
    "padding": "10px",
    "fontWeight": "bold",
    "border": f"2px solid {colors['primary']}",
    "background": "#ffffff",
    "color": colors["alert"],
}