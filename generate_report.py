from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, 
                                 Image, Table, TableStyle, PageBreak, HRFlowable)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
import numpy as np

def generate_report(readings, t_msa, h_msa, warmup_subgroups=15,
                    output_file="DHT11_Quality_Report.pdf"):

    doc = SimpleDocTemplate(
        output_file, pagesize=letter,
        rightMargin=0.75*inch, leftMargin=0.75*inch,
        topMargin=0.75*inch,   bottomMargin=0.75*inch
    )

    # ── Styles ───────────────────────────────────────────────────────────────
    styles = getSampleStyleSheet()
    style_title    = ParagraphStyle("ReportTitle", fontSize=20, alignment=TA_CENTER,
                                     spaceAfter=6, fontName="Helvetica-Bold", textColor=colors.HexColor("#1a1a2e"))
    style_subtitle = ParagraphStyle("Subtitle",    fontSize=11, alignment=TA_CENTER,
                                     spaceAfter=4, fontName="Helvetica",      textColor=colors.HexColor("#555555"))
    style_h1       = ParagraphStyle("H1", fontSize=14, fontName="Helvetica-Bold",
                                     spaceBefore=14, spaceAfter=6, textColor=colors.HexColor("#1a1a2e"),
                                     borderPad=4)
    style_h2       = ParagraphStyle("H2", fontSize=11, fontName="Helvetica-Bold",
                                     spaceBefore=10, spaceAfter=4, textColor=colors.HexColor("#333333"))
    style_body     = ParagraphStyle("Body", fontSize=10, fontName="Helvetica",
                                     spaceAfter=6, leading=15, alignment=TA_JUSTIFY)
    style_caption  = ParagraphStyle("Caption", fontSize=8, fontName="Helvetica-Oblique",
                                     alignment=TA_CENTER, textColor=colors.grey, spaceAfter=8)

    def divider():
        return HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cccccc"), spaceAfter=8)

    def section(title):
        return [Paragraph(title, style_h1), divider()]

    # Compute summary stats 
    stable_start = warmup_subgroups * 5
    stable       = readings[stable_start:]
    all_temps    = [r[1] for r in readings]
    all_hums     = [r[2] for r in readings]
    s_temps      = [r[1] for r in stable]
    s_hums       = [r[2] for r in stable]

    date_str = datetime.now().strftime("%B %d, %Y")


    story = []

    # Cover
    story.append(Spacer(1, 0.6*inch))
    story.append(Paragraph("DHT11 Environmental Monitoring", style_title))
    story.append(Paragraph("Quality Engineering Report", style_title))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph(f"Generated: {date_str}", style_subtitle))
    story.append(Paragraph("Arduino Mega 2560 &amp; DHT11 Sensor | Statistical Process Control &amp; MSA", style_subtitle))
    story.append(Spacer(1, 0.3*inch))
    story.append(divider())

    # 1. Executive Summary
    story += section("1. Executive Summary")
    story.append(Paragraph(
        f"This report presents a quality engineering analysis of an environmental monitoring system "
        f"built using an Arduino Mega 2560 microcontroller and a DHT11 temperature and humidity sensor. "
        f"A total of <b>200 measurements</b> were collected at 3second intervals. "
        f"The first {warmup_subgroups * 5} readings were identified as a warm-up phase and excluded from "
        f"control limit calculations, leaving <b>{len(stable)} stable readings</b> for analysis. "
        f"Statistical Process Control (SPC) X-bar and R charts were applied across 40 subgroups of size 5. "
        f"A Measurement System Analysis (MSA) was conducted to assess sensor repeatability, yielding a "
        f"Gauge R&amp;R of <b>{t_msa['gauge_rr_pct']:.1f}%</b> for temperature ({t_msa['verdict'].split()[0]}) "
        f"and <b>{h_msa['gauge_rr_pct']:.1f}%</b> for humidity ({h_msa['verdict'].split()[0]}). "
        f"Key findings indicate the DHT11's 1-degree resolution limits its precision for high-accuracy "
        f"manufacturing applications, and a higher-resolution sensor is recommended for tighter process control.",
        style_body))

    # 2. System Description
    story += section("2. System Description")

    story.append(Paragraph("2.1 Hardware", style_h2))
    hw_data = [
        ["Component",        "Specification"],
        ["Microcontroller",  "Arduino Mega 2560"],
        ["Sensor",           "DHT11 Temperature & Humidity"],
        ["Temp Accuracy",    "±2°C"],
        ["Humidity Accuracy","±5% RH"],
        ["Resolution",       "1°C / 1% RH"],
        ["Data Pin",         "Digital Pin 2"],
        ["Baud Rate",        "9600"],
    ]
    hw_table = Table(hw_data, colWidths=[2.5*inch, 3.5*inch])
    hw_table.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,0), colors.HexColor("#1a1a2e")),
        ("TEXTCOLOR",   (0,0), (-1,0), colors.white),
        ("FONTNAME",    (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",    (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.HexColor("#f5f5f5"), colors.white]),
        ("GRID",        (0,0), (-1,-1), 0.4, colors.HexColor("#cccccc")),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("RIGHTPADDING",(0,0), (-1,-1), 8),
        ("TOPPADDING",  (0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1), 5),
    ]))
    story.append(hw_table)
    story.append(Spacer(1, 0.1*inch))

    story.append(Paragraph("2.2 Data Collection Methodology", style_h2))
    story.append(Paragraph(
        "The Arduino sketch used the DHT_nonblocking library to poll the sensor every 3 seconds "
        "in a non-blocking state machine, preventing microcontroller lockup during measurement. "
        "Readings were transmitted over USB serial at 9600 baud in CSV format (index, temperature, humidity) "
        "and captured in Python using PySerial. A total of 200 measurements were saved to sensor_data.csv "
        "for offline analysis.",
        style_body))

    # 3. Raw Data Summary
    story += section("3. Raw Data Summary")

    raw_data = [["Reading #", "Temperature (C)", "Humidity (%)"]]
    for r in readings[:10]:
        raw_data.append([str(r[0]), f"{r[1]:.1f}", f"{r[2]:.1f}"])
    raw_data.append(["...", "...", "..."])
    raw_data.append([str(readings[-1][0]), f"{readings[-1][1]:.1f}", f"{readings[-1][2]:.1f}"])

    raw_table = Table(raw_data, colWidths=[1.5*inch, 2.5*inch, 2.5*inch])
    raw_table.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,0), colors.HexColor("#1a1a2e")),
        ("TEXTCOLOR",   (0,0), (-1,0), colors.white),
        ("FONTNAME",    (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",    (0,0), (-1,-1), 9),
        ("ALIGN",       (0,0), (-1,-1), "CENTER"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.HexColor("#f5f5f5"), colors.white]),
        ("GRID",        (0,0), (-1,-1), 0.4, colors.HexColor("#cccccc")),
        ("TOPPADDING",  (0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1), 5),
    ]))
    story.append(raw_table)
    story.append(Paragraph("Table 1: First 10 and last readings from sensor_data.csv", style_caption))

    story.append(Paragraph(
        f"Upon inspection, a clear warm-up drift was identified in the first {warmup_subgroups*5} readings. "
        f"Temperature dropped from {all_temps[0]:.1f}C at reading 1 to a stable {np.mean(s_temps):.1f}C, "
        f"and humidity settled from {all_hums[0]:.1f}% to a stable mean of {np.mean(s_hums):.1f}%. "
        f"This is consistent with known DHT11 warm-up characteristics and was excluded from control limit calculations.",
        style_body))

    # 4. SPC Charts
    story.append(PageBreak())
    story += section("4. Statistical Process Control (SPC)")

    story.append(Paragraph(
        "X-bar (X) and Range (R) control charts were constructed using subgroups of n=5, "
        "producing 40 subgroups from 200 readings. Standard SPC constants for n=5 were applied: "
        "A2=0.577, D3=0.0, D4=2.114. Control limits were calculated exclusively from the stable "
        "region (subgroups 16-40) to avoid inflation from warm-up variation. "
        "The grey shaded region in the charts denotes the excluded warm-up phase.",
        style_body))

    try:
        spc_img = Image("spc_charts.png", width=6.5*inch, height=9*inch)
        story.append(spc_img)
        story.append(Paragraph("Figure 1: X-bar and R Control Charts for Temperature and Humidity", style_caption))
    except:
        story.append(Paragraph("[spc_charts.png not found — run plot_data() first]", style_body))

    story.append(Paragraph(
        "Note: The humidity X-bar chart shows out-of-control signals in the stable region "
        "due to the DHT11's 1% resolution causing discrete stepping between 45% and 46%, "
        "rather than true process instability. A higher resolution sensor such as the DHT22 "
        "(0.1% RH resolution) would eliminate this artifact.",
        style_body))

    # SPC stats table
    def subgroup_stats(data, n=5):
        groups = [data[i:i+n] for i in range(0, len(data) - len(data)%n, n)]
        means  = [np.mean(g) for g in groups]
        ranges = [max(g)-min(g) for g in groups]
        return means, ranges

    t_means, t_ranges = subgroup_stats(s_temps)
    h_means, h_ranges = subgroup_stats(s_hums)
    A2, D3, D4 = 0.577, 0.0, 2.114
    xbar_t = np.mean(t_means); rbar_t = np.mean(t_ranges)
    xbar_h = np.mean(h_means); rbar_h = np.mean(h_ranges)

    spc_summary = [
        ["Parameter",           "Temperature", "Humidity"],
        ["Process Mean (X-bar)",f"{xbar_t:.2f} C",  f"{xbar_h:.2f} %"],
        ["Avg Range (R-bar)",   f"{rbar_t:.3f}",      f"{rbar_h:.3f}"],
        ["UCL (X-bar chart)",   f"{xbar_t + A2*rbar_t:.2f}", f"{xbar_h + A2*rbar_h:.2f}"],
        ["LCL (X-bar chart)",   f"{xbar_t - A2*rbar_t:.2f}", f"{xbar_h - A2*rbar_h:.2f}"],
        ["UCL (R chart)",       f"{D4*rbar_t:.3f}",   f"{D4*rbar_h:.3f}"],
        ["Subgroups analyzed",  "25 (stable)",         "25 (stable)"],
    ]
    spc_table = Table(spc_summary, colWidths=[2.5*inch, 2*inch, 2*inch])
    spc_table.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,0), colors.HexColor("#1a1a2e")),
        ("TEXTCOLOR",   (0,0), (-1,0), colors.white),
        ("FONTNAME",    (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",    (0,0), (-1,-1), 9),
        ("ALIGN",       (1,0), (-1,-1), "CENTER"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.HexColor("#f5f5f5"), colors.white]),
        ("GRID",        (0,0), (-1,-1), 0.4, colors.HexColor("#cccccc")),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("TOPPADDING",  (0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1), 5),
    ]))
    story.append(Spacer(1, 0.1*inch))
    story.append(spc_table)
    story.append(Paragraph("Table 2: SPC Control Limit Summary (stable region only)", style_caption))

    # 5. MSA 
    story.append(PageBreak())
    story += section("5. Measurement System Analysis (MSA)")

    story.append(Paragraph(
        "A Gauge Repeatability and Reproducibility (R&amp;R) study was conducted on the stable "
        "region of the data to assess whether the DHT11 sensor is a capable measurement instrument. "
        "% Gauge R&amp;R quantifies how much of the total observed variation is due to the measurement "
        "system itself rather than actual process variation. A result below 10% is considered excellent, "
        "10-30% acceptable, and above 30% unacceptable for manufacturing applications.",
        style_body))

    try:
        msa_img = Image("msa_analysis.png", width=6.5*inch, height=4.5*inch)
        story.append(msa_img)
        story.append(Paragraph("Figure 2: MSA Run Charts, Distributions, and Gauge R&R Summary", style_caption))
    except:
        story.append(Paragraph("[msa_analysis.png not found — run run_msa() first]", style_body))

    msa_summary = [
        ["Metric",              "Temperature",                    "Humidity"],
        ["Mean (stable)",       f"{t_msa['mean']:.2f} C",        f"{h_msa['mean']:.2f} %"],
        ["Std Dev",             f"{t_msa['std']:.4f}",            f"{h_msa['std']:.4f}"],
        ["% Gauge R&R",        f"{t_msa['gauge_rr_pct']:.1f}%",  f"{h_msa['gauge_rr_pct']:.1f}%"],
        ["NDC",                 f"{t_msa['ndc']:.1f}",            f"{h_msa['ndc']:.1f}"],
        ["Cp",                  f"{t_msa['cp']:.2f}",             f"{h_msa['cp']:.2f}"],
        ["Cpk",                 f"{t_msa['cpk']:.2f}",            f"{h_msa['cpk']:.2f}"],
        ["Verdict",             t_msa['verdict'],                  h_msa['verdict']],
    ]
    msa_table = Table(msa_summary, colWidths=[2.5*inch, 2*inch, 2*inch])
    msa_table.setStyle(TableStyle([
        ("BACKGROUND",   (0,0),  (-1,0),  colors.HexColor("#1a1a2e")),
        ("TEXTCOLOR",    (0,0),  (-1,0),  colors.white),
        ("FONTNAME",     (0,0),  (-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",     (0,0),  (-1,-1), 9),
        ("ALIGN",        (1,0),  (-1,-1), "CENTER"),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [colors.HexColor("#f5f5f5"), colors.white]),
        ("GRID",         (0,0),  (-1,-1), 0.4, colors.HexColor("#cccccc")),
        ("LEFTPADDING",  (0,0),  (-1,-1), 8),
        ("TOPPADDING",   (0,0),  (-1,-1), 5),
        ("BOTTOMPADDING",(0,0),  (-1,-1), 5),
        # color verdict row
        ("TEXTCOLOR",    (1,7),  (1,7),
            colors.green if t_msa['gauge_rr_pct'] < 10 else
            colors.orange if t_msa['gauge_rr_pct'] < 30 else colors.red),
        ("TEXTCOLOR",    (2,7),  (2,7),
            colors.green if h_msa['gauge_rr_pct'] < 10 else
            colors.orange if h_msa['gauge_rr_pct'] < 30 else colors.red),
        ("FONTNAME",     (0,7),  (-1,7),  "Helvetica-Bold"),
    ]))
    story.append(Spacer(1, 0.1*inch))
    story.append(msa_table)
    story.append(Paragraph("Table 3: MSA Gauge R&R Results", style_caption))

    #6. Conclusions
    story.append(PageBreak())
    story += section("6. Conclusions & Recommendations")

    story.append(Paragraph("6.1 Key Findings", style_h2))
    story.append(Paragraph(
        "The DHT11 sensor demonstrated stable, repeatable measurements after an initial warm-up period "
        f"of approximately {warmup_subgroups*5} readings (~{warmup_subgroups*15} seconds). "
        f"In the stable region, temperature held at {t_msa['mean']:.1f}C and humidity at {h_msa['mean']:.1f}% "
        f"with minimal variation. The SPC X-bar chart confirmed the process remained in statistical control "
        f"after warm-up, with no out-of-control signals detected in the stable region.",
        style_body))

    story.append(Paragraph("6.2 Sensor Limitations", style_h2))
    story.append(Paragraph(
        "The DHT11's 1-degree resolution causes readings to be discretized, meaning true continuous "
        "variation cannot be captured. This is evident in the humidity X-bar chart, where "
        "out-of-control signals appear in the stable region due to discrete stepping between "
        "45% and 46% — not because the process is actually unstable, but because the sensor "
        "cannot resolve values between whole numbers. Similarly, temperature in stable conditions "
        "reads exactly 24.0C every time, making standard deviation appear as zero and Gauge R&amp;R "
        "artificially excellent. For high-precision manufacturing environments such as satellite "
        "assembly, this resolution is insufficient. The DHT22 sensor offers 0.1C and 0.1% RH "
        "resolution and would be a direct drop-in replacement for more accurate process monitoring.",
        style_body))

    story.append(Paragraph("6.3 Recommendations", style_h2))
    rec_data = [
        ["#", "Recommendation",                          "Justification"],
        ["1", "Upgrade to DHT22 sensor",                 "0.1C resolution vs 1C on DHT11"],
        ["2", "Extend warm-up exclusion detection",      "Auto-detect stabilization point algorithmically"],
        ["3", "Add multiple sensor positions",           "Enables reproducibility study (full Gauge R&R)"],
        ["4", "Increase sampling rate",                  "More data points improve SPC sensitivity"],
        ["5", "Add humidity calibration reference",      "Validate sensor against known humidity standard"],
    ]
    rec_table = Table(rec_data, colWidths=[0.3*inch, 2.8*inch, 3.4*inch])
    rec_table.setStyle(TableStyle([
        ("BACKGROUND",   (0,0),  (-1,0),  colors.HexColor("#1a1a2e")),
        ("TEXTCOLOR",    (0,0),  (-1,0),  colors.white),
        ("FONTNAME",     (0,0),  (-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",     (0,0),  (-1,-1), 9),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [colors.HexColor("#f5f5f5"), colors.white]),
        ("GRID",         (0,0),  (-1,-1), 0.4, colors.HexColor("#cccccc")),
        ("LEFTPADDING",  (0,0),  (-1,-1), 8),
        ("TOPPADDING",   (0,0),  (-1,-1), 5),
        ("BOTTOMPADDING",(0,0),  (-1,-1), 5),
        ("VALIGN",       (0,0),  (-1,-1), "MIDDLE"),
    ]))
    story.append(rec_table)
    story.append(Paragraph("Table 4: Recommendations for Future Improvement", style_caption))

    # 7. Appendix
    story += section("7. Appendix — Tools & Methods")
    story.append(Paragraph(
        "<b>Hardware:</b> Arduino Mega 2560, DHT11 sensor, USB Serial connection.<br/>"
        "<b>Firmware:</b> Arduino IDE, DHT_nonblocking library, 9600 baud serial output.<br/>"
        "<b>Data capture:</b> Python 3, PySerial library, CSV file export.<br/>"
        "<b>Analysis:</b> NumPy, SciPy (Shapiro-Wilk normality test), Matplotlib.<br/>"
        "<b>SPC constants (n=5):</b> A2=0.577, D3=0.000, D4=2.114.<br/>"
        "<b>Gauge R&amp;R formula:</b> % GRR = (sigma_measurement / sigma_total) x 100.<br/>"
        "<b>NDC formula:</b> NDC = 1.41 x (sigma_total / sigma_measurement).<br/>"
        "<b>Cp/Cpk:</b> Calculated using assumed specification limits of Mean +- 2 units.",
        style_body))

    # Build
    doc.build(story)
    print(f"Report saved to '{output_file}'")

# Run it
generate_report(readings, t_msa, h_msa, warmup_subgroups=15)