import json
import io
import pandas as pd
from collections import Counter
from reportlab.lib.pagesizes import landscape, letter
from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus.flowables import PageBreak
import matplotlib.pyplot as plt

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

def generate_report(results, filetype="pdf"):
    df = pd.DataFrame(results)
    required = ["name","description","category","risk","risk_score","success","details","remediation","references","scenario"]
    for col in required:
        if col not in df.columns:
            df[col] = ""
    # Summaries
    risk_counts = dict(Counter(df["risk"]))
    cat_counts = dict(Counter(df["category"]))
    plugin_counts = dict(Counter(df["name"]))
    success_rate = (df["success"]==True).sum() / len(df) if len(df)>0 else 0

    if filetype=="json":
        return df.to_json(orient="records", indent=2)
    if filetype=="csv":
        return df.to_csv(index=False)

    # PDF output
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=landscape(letter),
        rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20
    )
    styles = getSampleStyleSheet()
    para_style = ParagraphStyle(
        name='TableCell',
        fontSize=7,
        leading=9,
        alignment=0,
        wordWrap='CJK',
    )
    elements = []
    elements.append(Paragraph("AI Test Suite: Full Risk & Attack Report", styles["Title"]))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(f"<b>Total Tests:</b> {len(df)}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Success Rate:</b> {success_rate*100:.1f}%", styles["Normal"]))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph("<b>Risk Level Distribution:</b> "+", ".join(f"{k}: {v}" for k,v in risk_counts.items()), styles["Normal"]))
    elements.append(Paragraph("<b>Category Breakdown:</b> "+", ".join(f"{k}: {v}" for k,v in cat_counts.items()), styles["Normal"]))
    elements.append(Paragraph("<b>Plugins Used:</b> "+", ".join(f"{k}: {v}" for k,v in plugin_counts.items()), styles["Normal"]))
    elements.append(Spacer(1, 8))

    # Chart
    try:
        if risk_counts:
            risk_chart = plot_risk_chart(risk_counts)
            from reportlab.platypus import Image
            elements.append(Image(risk_chart, width=160, height=160))
            elements.append(Spacer(1, 4))
    except Exception as e:
        elements.append(Paragraph(f"<font color='red'>Risk chart error: {e}</font>", styles["Normal"]))

    # Main compact table: only vital info
    compact_table_data = [
        ["Plugin", "Scenario", "Risk", "Category", "Success"]
    ]
    for _, row in df.iterrows():
        risk_color = "#f4cccc" if str(row["risk"]).lower() in ["high","critical"] else "#fff"
        compact_table_data.append([
            str(row["name"]),
            str(row.get("scenario","")),
            str(row["risk"]),
            str(row["category"]),
            "✔️" if row["success"]==True else "❌",
        ])
    tbl = Table(compact_table_data, repeatRows=1, colWidths=[90, 90, 60, 90, 40])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.darkblue),
        ("TEXTCOLOR",(0,0),(-1,0),colors.whitesmoke),
        ("FONTNAME", (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0),(-1,0), 8),
        ("BOTTOMPADDING", (0,0),(-1,0), 6),
        ("BACKGROUND",(0,1),(-1,-1),colors.white),
        ("FONTSIZE", (0,1),(-1,-1), 7),
        ("BOX", (0,0), (-1,-1), 0.3, colors.black),
        ("GRID", (0,0), (-1,-1), 0.25, colors.grey),
    ]))
    elements.append(tbl)
    elements.append(PageBreak())

    # Per-result long details (appendix-style, one row per page)
    elements.append(Paragraph("Detailed Findings", styles["Heading2"]))
    for i, row in df.iterrows():
        elements.append(Paragraph(f"<b>Plugin:</b> {row['name']}", para_style))
        elements.append(Paragraph(f"<b>Scenario:</b> {row.get('scenario','')}", para_style))
        elements.append(Paragraph(f"<b>Risk:</b> {row['risk']}", para_style))
        elements.append(Paragraph(f"<b>Category:</b> {row['category']}", para_style))
        elements.append(Paragraph(f"<b>Success:</b> {'✔️' if row['success']==True else '❌'}", para_style))
        elements.append(Paragraph(f"<b>Description:</b> {row['description']}", para_style))
        elements.append(Paragraph(f"<b>Details:</b> {row['details']}", para_style))
        elements.append(Paragraph(f"<b>Remediation:</b> {row['remediation']}", para_style))
        refs = row['references']
        if isinstance(refs, list): refs = ", ".join(refs)
        elements.append(Paragraph(f"<b>References:</b> {refs}", para_style))
        elements.append(Spacer(1, 7))
        if i % 2 == 1:
            elements.append(PageBreak())

    elements.append(Spacer(1,10))
    elements.append(Paragraph("Report generated by AI Test Suite v2. All rights reserved.", styles["Italic"]))

    doc.build(elements)
    buf.seek(0)
    return buf.read()
