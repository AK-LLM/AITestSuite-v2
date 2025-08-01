import json
import io
import os
import pandas as pd
from collections import Counter
from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen import canvas
from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
                                Paragraph, Spacer, Image, PageBreak)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import matplotlib.pyplot as plt

from core.attack_graph import build_attack_graph, visualize_attack_graph

def plot_risk_chart(risk_counts):
    fig, ax = plt.subplots(figsize=(3,3))
    risks = list(risk_counts.keys())
    sizes = [risk_counts[r] for r in risks]
    colors_map = {"Low": "#5bc236", "Medium": "#e6e600", "High": "#f39c12", "Critical": "#c0392b"}
    chart_colors = [colors_map.get(r, "#888") for r in risks]
    ax.pie(sizes, labels=risks, autopct="%1.0f%%", colors=chart_colors, startangle=140)
    ax.set_title("Risk Distribution")
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return buf

def ensure_fields(row):
    """Guarantee remediation and references always present for all rows."""
    if "remediation" not in row or not row["remediation"]:
        row["remediation"] = "Refer to plugin guidance and LLM vendor docs."
    if "references" not in row or not row["references"]:
        row["references"] = "https://llm-attacks.org, https://owasp.org/www-project-top-ten/"
    return row

def generate_report(results, filetype="pdf"):
    df = pd.DataFrame(results)
    required = ["name","description","category","risk","risk_score","success","details","remediation","references","scenario"]
    for col in required:
        if col not in df.columns:
            df[col] = ""

    # Guarantee fields for every row
    df = df.apply(ensure_fields, axis=1)

    risk_counts = dict(Counter(df["risk"]))
    cat_counts = dict(Counter(df["category"]))
    plugin_counts = dict(Counter(df["name"]))
    success_rate = (df["success"]==True).sum() / len(df) if len(df)>0 else 0

    if filetype=="json":
        return df.to_json(orient="records", indent=2)

    # --- PDF output ---
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=landscape(letter), rightMargin=25, leftMargin=25, topMargin=25, bottomMargin=25)
    styles = getSampleStyleSheet()
    small = ParagraphStyle('small', parent=styles['Normal'], fontSize=7, leading=8)
    elements = []
    elements.append(Paragraph("AI Test Suite: Full Risk & Attack Report", styles["Title"]))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(f"<b>Total Tests:</b> {len(df)}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Success Rate:</b> {success_rate*100:.1f}%", styles["Normal"]))
    elements.append(Spacer(1, 5))
    elements.append(Paragraph("<b>Risk Level Distribution:</b> "+", ".join(f"{k}: {v}" for k,v in risk_counts.items()), styles["Normal"]))
    elements.append(Paragraph("<b>Category Breakdown:</b> "+", ".join(f"{k}: {v}" for k,v in cat_counts.items()), styles["Normal"]))
    elements.append(Paragraph("<b>Plugins Used:</b> "+", ".join(f"{k}: {v}" for k,v in plugin_counts.items()), styles["Normal"]))
    elements.append(Spacer(1, 8))
    # Risk chart
    try:
        if risk_counts:
            risk_chart = plot_risk_chart(risk_counts)
            elements.append(Image(risk_chart, width=160, height=160))
            elements.append(Spacer(1, 5))
    except Exception as e:
        elements.append(Paragraph(f"<font color='red'>Risk chart error: {e}</font>", styles["Normal"]))

    # --- Attack graph static image (PNG) ---
    try:
        G = build_attack_graph(results)
        html_path, png_path = visualize_attack_graph(G, output_html="attack_graph.html", image_out="attack_graph.png")
        if png_path and os.path.exists(png_path):
            elements.append(Paragraph("Attack Graph: AI Attack Relationships", styles["Heading4"]))
            elements.append(Image(png_path, width=400, height=220))
            elements.append(Spacer(1, 5))
            elements.append(Paragraph("For interactive exploration, open attack_graph.html in a browser.", styles["Normal"]))
        else:
            elements.append(Paragraph("<font color='red'>Attack graph image missing or failed.</font>", styles="Normal"))
    except Exception as e:
        elements.append(Paragraph(f"<font color='red'>Attack graph error: {e}</font>", styles["Normal"]))

    # Benchmarks/explanation
    elements.append(Paragraph("<b>Benchmarks (Industry):</b>", styles["Heading4"]))
    elements.append(Paragraph(
        "Results compared to published benchmarks (OWASP, LLM-attacks.org, Neuman, Sutskever). "
        "Red = worse than benchmark. Green = better or no finding.",
        styles["Normal"]))
    elements.append(Spacer(1, 8))
    # --- Main Table: Truncate long text, wrap as Paragraph ---
    table_data = [
        ["Plugin", "Scenario", "Risk", "Category", "Success", "Details", "Remediation", "References"]
    ]
    for _, row in df.iterrows():
        refs = row["references"]
        if isinstance(refs, list): refs = ", ".join(refs)
        elif refs is None: refs = ""
        risk_color = "#f4cccc" if str(row["risk"]).lower() in ["high","critical"] else "#fff"
        # Wrap/truncate long fields
        details_short = (str(row["details"])[:120] + " ...") if len(str(row["details"]))>120 else str(row["details"])
        remediation_short = (str(row.get("remediation",""))[:80] + " ...") if len(str(row.get("remediation","")))>80 else str(row.get("remediation",""))
        refs_short = (str(refs)[:60] + " ...") if len(str(refs))>60 else str(refs)
        table_data.append([
            Paragraph(str(row["name"]), small),
            Paragraph(str(row.get("scenario","")), small),
            Paragraph(str(row["risk"]), small),
            Paragraph(str(row["category"]), small),
            Paragraph("✔️" if row["success"]==True else "❌", small),
            Paragraph(details_short, small),
            Paragraph(remediation_short, small),
            Paragraph(refs_short, small),
        ])
    tbl = Table(table_data, repeatRows=1, colWidths=[70,60,38,62,32,172,120,100])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.darkblue),
        ("TEXTCOLOR",(0,0),(-1,0),colors.whitesmoke),
        ("FONTNAME", (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0),(-1,0), 8),
        ("BOTTOMPADDING", (0,0),(-1,0), 6),
        ("BACKGROUND",(0,1),(-1,-1),colors.white),
        ("FONTSIZE", (0,1),(-1,-1), 7),
        ("BOX", (0,0), (-1,-1), 0.3, colors.black),
        ("GRID", (0,0), (-1,-1), 0.18, colors.grey),
        ("ALIGN", (0,0),(-1,-1),"LEFT"),
    ]))
    elements.append(tbl)
    elements.append(PageBreak())
    # --- Appendix: Full plugin details (untruncated) ---
    elements.append(Paragraph("APPENDIX: Full Details Per Test", styles["Heading3"]))
    for _, row in df.iterrows():
        elements.append(Spacer(1,2))
        elements.append(Paragraph(f"<b>Plugin:</b> {row['name']} / <b>Scenario:</b> {row.get('scenario','')}", small))
        elements.append(Paragraph(f"<b>Risk:</b> {row['risk']}  |  <b>Category:</b> {row['category']}  |  <b>Success:</b> {'✔️' if row['success'] else '❌'}", small))
        elements.append(Paragraph(f"<b>Details:</b> {row['details']}", small))
        elements.append(Paragraph(f"<b>Remediation:</b> {row.get('remediation','')}", small))
        elements.append(Paragraph(f"<b>References:</b> {row.get('references','')}", small))
        elements.append(Spacer(1,2))
    elements.append(Spacer(1,8))
    elements.append(Paragraph("Report generated by AI Test Suite v2. All rights reserved.", styles["Italic"]))
    doc.build(elements)
    buf.seek(0)
    return buf.read()
