import json
import io
import pandas as pd
from collections import Counter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import matplotlib.pyplot as plt

def plot_chart(label, counts, color_map, title):
    fig, ax = plt.subplots(figsize=(3,3))
    keys = list(counts.keys())
    sizes = [counts[k] for k in keys]
    chart_colors = [color_map.get(k, "#888") for k in keys]
    ax.pie(sizes, labels=keys, autopct="%1.0f%%", colors=chart_colors, startangle=140)
    ax.set_title(title)
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return buf

def generate_report(results, filetype="pdf"):
    # --- DataFrame
    df = pd.DataFrame(results)
    # Ensure required columns
    required = [
        "name","description","category","risk","risk_score",
        "success","details","remediation","references","scenario"
    ]
    for col in required:
        if col not in df.columns:
            df[col] = ""
    # Clean up references
    for i in range(len(df)):
        refs = df.at[i, "references"]
        if isinstance(refs, list):
            df.at[i, "references"] = ", ".join(refs)
        elif refs is None:
            df.at[i, "references"] = ""

    # --- Summaries
    risk_counts = dict(Counter([str(x) for x in df["risk"]]))
    cat_counts = dict(Counter([str(x) for x in df["category"]]))
    plugin_counts = dict(Counter([str(x) for x in df["name"]]))
    scenario_counts = dict(Counter([str(x) for x in df["scenario"]]))
    success_rate = (df["success"]==True).sum() / len(df) if len(df)>0 else 0

    # --- JSON
    if filetype=="json":
        return df.to_json(orient="records", indent=2)

    # --- PDF Setup ---
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter, rightMargin=25, leftMargin=25, topMargin=25, bottomMargin=25)
    styles = getSampleStyleSheet()
    elements = []
    elements.append(Paragraph("AI Test Suite: Deluxe Risk & Attack Report", styles["Title"]))
    elements.append(Spacer(1, 10))

    # --- Executive Summary ---
    elements.append(Paragraph(f"<b>Total Tests:</b> {len(df)}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Success Rate:</b> {success_rate*100:.1f}%", styles["Normal"]))
    elements.append(Paragraph(f"<b>Unique Plugins:</b> {len(plugin_counts)}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Scenarios Tested:</b> {len(scenario_counts)}", styles["Normal"]))
    elements.append(Spacer(1, 6))

    # --- Charts ---
    chart_sec = []
    try:
        if risk_counts:
            chart_sec.append(Image(plot_chart("Risk", risk_counts, {"Low":"#5bc236", "Medium":"#e6e600", "High":"#f39c12", "Critical":"#c0392b"}, "Risk Distribution"), width=160, height=160))
        if cat_counts:
            chart_sec.append(Image(plot_chart("Category", cat_counts, {}, "Category Breakdown"), width=160, height=160))
        if plugin_counts:
            chart_sec.append(Image(plot_chart("Plugin", plugin_counts, {}, "Plugin Use Frequency"), width=160, height=160))
        if chart_sec:
            elements.extend(chart_sec)
            elements.append(Spacer(1,10))
    except Exception as e:
        elements.append(Paragraph(f"<font color='red'>Chart error: {e}</font>", styles["Normal"]))

    # --- Industry Benchmark/Explanation ---
    elements.append(Paragraph("<b>Benchmarks (Industry):</b>", styles["Heading4"]))
    elements.append(Paragraph(
        "Benchmarked against: OWASP LLM Top 10, LLM-attacks.org, Yair Neuman, Sutskever, NIST. "
        "Red = worse than benchmark. Green = better or no finding.",
        styles["Normal"]))
    elements.append(Spacer(1, 10))

    # --- Risk Matrix Legend ---
    risk_matrix = [
        ["Low", "Minor risk, negligible impact", "Monitor"],
        ["Medium", "Moderate risk, non-critical impact", "Mitigate"],
        ["High", "Severe risk, may cause major failure", "Urgent action"],
        ["Critical", "Extreme risk, possible catastrophic outcome", "Immediate fix"]
    ]
    elements.append(Paragraph("<b>Risk Matrix:</b>", styles["Heading4"]))
    matrix_table = Table(
        [["Level", "Definition", "Action"]] + risk_matrix,
        style=[
            ("BACKGROUND", (0,0), (-1,0), colors.darkblue),
            ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
            ("FONTNAME", (0,0),(-1,0), "Helvetica-Bold"),
            ("FONTSIZE", (0,0),(-1,0), 9),
            ("ALIGN", (0,0),(-1,-1), "CENTER"),
            ("BACKGROUND", (0,1),(-1,1), colors.lightgrey),
        ]
    )
    elements.append(matrix_table)
    elements.append(Spacer(1, 10))

    # --- Results Table ---
    table_data = [
        ["Plugin", "Scenario", "Risk", "Category", "Success", "Details", "Remediation", "References"]
    ]
    for _, row in df.iterrows():
        risk_val = str(row["risk"])
        risk_color = "#f4cccc" if risk_val.lower() in ["high","critical"] else "#fff"
        table_data.append([
            str(row["name"]),
            str(row["scenario"]),
            risk_val,
            str(row["category"]),
            "✔️" if row["success"]==True else "❌",
            str(row["details"]),
            str(row["remediation"]),
            row["references"],
        ])
    tbl = Table(table_data, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.darkblue),
        ("TEXTCOLOR",(0,0),(-1,0),colors.whitesmoke),
        ("FONTNAME", (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0),(-1,0), 9),
        ("BOTTOMPADDING", (0,0),(-1,0), 6),
        ("BACKGROUND",(0,1),(-1,-1),colors.white),
        ("FONTSIZE", (0,1),(-1,-1), 8),
        ("BOX", (0,0), (-1,-1), 0.3, colors.black),
        ("GRID", (0,0), (-1,-1), 0.25, colors.grey),
    ]))
    elements.append(tbl)
    elements.append(Spacer(1, 12))

    # --- Remediation summary for high/critical ---
    risky = df[df["risk"].str.lower().isin(["high","critical"])]
    if len(risky):
        elements.append(Paragraph("<b>Remediation Advice:</b>", styles["Heading4"]))
        for _, row in risky.iterrows():
            elements.append(Paragraph(f"<b>{row['name']}:</b> {row.get('remediation','No fix given')}", styles["Normal"]))

    elements.append(Spacer(1,12))
    elements.append(Paragraph("Report generated by AI Test Suite v2. For methodology see: owasp.org/www-project-llm. All rights reserved.", styles["Italic"]))

    doc.build(elements)
    buf.seek(0)
    return buf.read()
