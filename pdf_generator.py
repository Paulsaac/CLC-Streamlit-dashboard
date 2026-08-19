import datetime
import io
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
from fpdf import FPDF


def sanitize_text(text: str) -> str:
    """Sanitiza texto para codificación compatible con fuentes estándar de fpdf (latin-1)."""
    if text is None:
        return ""
    s = str(text)
    replacements = {
        "—": "-",
        "–": "-",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "•": "*",
        "…": "...",
        "↗": "+",
        "↘": "-",
        "→": "->",
        "⭐": "*",
        "✅": "[OK]",
        "⚠️": "[!]",
        "❌": "[X]",
        "🟡": "",
        "📈": "",
        "🛍️": "",
        "📦": "",
        "📣": "",
        "🎯": "",
        "📥": "",
        "📄": "",
        "💡": "",
        "🗓️": "",
        "⚖️": "",
        "📅": "",
    }
    for orig, rep in replacements.items():
        s = s.replace(orig, rep)
    return s.encode("latin-1", "replace").decode("latin-1")


# ==========================================
# FORMATEADORES NUMÉRICOS EN ESPAÑOL
# ==========================================

def fmt_monto(val: float) -> str:
    """Formatea valores monetarios enteros con '.' de miles: $1.250.000"""
    try:
        return f"${float(val):,.0f}".replace(",", ".")
    except (ValueError, TypeError):
        return "$0"


def fmt_entero(val) -> str:
    """Formatea cantidades enteras con '.' de miles: 1.000"""
    try:
        return f"{int(val):,}".replace(",", ".")
    except (ValueError, TypeError):
        return "0"


def fmt_decimal(val: float, dec: int = 2) -> str:
    """Formatea números decimales con ',' decimal y '.' de miles: 1.234,56"""
    try:
        formatted = f"{float(val):,.{dec}f}"
        return formatted.replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return "0,00"


def fmt_roas(val: float) -> str:
    """Formatea ROAS con ',' decimal: 2,15x"""
    try:
        return f"{float(val):.2f}x".replace(".", ",")
    except (ValueError, TypeError):
        return "0,00x"


def fmt_porcentaje(val: float, dec: int = 1) -> str:
    """Formatea porcentajes con ',' decimal: 12,5%"""
    try:
        return f"{float(val):.{dec}f}%".replace(".", ",")
    except (ValueError, TypeError):
        return "0,0%"


def format_currency_es(val, pos=None):
    """Formatea valores monetarios: miles con 'm' y millones con 'M' sin decimales y punto de miles."""
    abs_val = abs(val)
    sign = "-" if val < 0 else ""
    if abs_val >= 1_000_000:
        num_str = f"{abs_val / 1_000_000:.0f}".replace(",", ".")
        return f"{sign}${num_str}M"
    elif abs_val >= 1_000:
        num_str = f"{abs_val / 1_000:.0f}".replace(",", ".")
        return f"{sign}${num_str}m"
    else:
        return f"{sign}${abs_val:,.0f}".replace(",", ".")


def format_number_es(val, pos=None):
    """Formatea cantidades numéricas: miles con 'm' y millones con 'M' sin decimales y punto de miles."""
    abs_val = abs(val)
    sign = "-" if val < 0 else ""
    if abs_val >= 1_000_000:
        num_str = f"{abs_val / 1_000_000:.0f}".replace(",", ".")
        return f"{sign}{num_str}M"
    elif abs_val >= 1_000:
        num_str = f"{abs_val / 1_000:.0f}".replace(",", ".")
        return f"{sign}{num_str}m"
    else:
        return f"{sign}{abs_val:,.0f}".replace(",", ".")


# ==========================================
# FUNCIONES GENERADORAS DE GRÁFICOS (MATPLOTLIB)
# ==========================================

def fig_to_bytes(fig) -> io.BytesIO:
    """Convierte una figura de matplotlib en un buffer de bytes PNG optimizado."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=180, bbox_inches="tight", facecolor="white", edgecolor="none")
    plt.close(fig)
    buf.seek(0)
    return buf


def make_weekly_revenue_chart(df_semana: pd.DataFrame) -> io.BytesIO:
    """Gráfico de evolución de ingresos semanales ($)."""
    fig, ax = plt.subplots(figsize=(6.2, 2.7))
    df_plot = df_semana.tail(12).copy()
    x_labels = [str(p) for p in df_plot["Periodo"]]
    y_vals = df_plot["Ingresos Generados"]

    ax.plot(x_labels, y_vals, marker="o", color="#124E3F", linewidth=2.2, markersize=5, label="Ingresos ($)")
    ax.fill_between(x_labels, y_vals, color="#E8F5E9", alpha=0.6)

    ax.set_title("Evolución de Ingresos Semanales ($)", fontsize=9.5, fontweight="bold", color="#124E3F", pad=8)
    ax.set_ylabel("Ingresos ($)", fontsize=8, color="#222222")
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(format_currency_es))
    ax.tick_params(axis="x", rotation=40, labelsize=7, colors="#222222")
    ax.tick_params(axis="y", labelsize=7.5, colors="#222222")
    ax.grid(True, linestyle="--", alpha=0.35, color="#CCCCCC")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#E0E0E0")
    ax.spines["bottom"].set_color("#E0E0E0")

    return fig_to_bytes(fig)


def make_visitas_ops_chart(df_semana: pd.DataFrame) -> io.BytesIO:
    """Gráfico dual: Visitas Totales (Barras) vs Operaciones Concretadas (Línea)."""
    fig, ax1 = plt.subplots(figsize=(6.2, 2.7))
    df_plot = df_semana.tail(12).copy()
    x_labels = [str(p) for p in df_plot["Periodo"]]

    # Barras de visitas (Verde Principal con transparencia)
    ax1.bar(x_labels, df_plot["Visitas Totales"], color="#124E3F", alpha=0.4, label="Visitas Totales", width=0.55)
    ax1.set_ylabel("Visitas", fontsize=8, color="#124E3F")
    ax1.yaxis.set_major_formatter(ticker.FuncFormatter(format_number_es))
    ax1.tick_params(axis="x", rotation=40, labelsize=7, colors="#222222")
    ax1.tick_params(axis="y", labelsize=7.5, colors="#124E3F")
    ax1.grid(True, linestyle="--", alpha=0.35, color="#CCCCCC")

    # Línea de operaciones (Verde Acento vibrante)
    ax2 = ax1.twinx()
    ax2.plot(x_labels, df_plot["Cantidad de Operaciones"], color="#25D366", linewidth=2.2, marker="s", markersize=4, label="Operaciones")
    ax2.set_ylabel("Operaciones", fontsize=8, color="#124E3F")
    ax2.tick_params(axis="y", labelsize=7.5, colors="#124E3F")
    ax2.spines["top"].set_visible(False)

    ax1.set_title("Relación Visitas vs. Operaciones", fontsize=9.5, fontweight="bold", color="#124E3F", pad=8)
    ax1.spines["top"].set_visible(False)
    ax1.spines["left"].set_color("#E0E0E0")
    ax1.spines["bottom"].set_color("#E0E0E0")

    return fig_to_bytes(fig)


def make_ads_vs_revenue_chart(df_semana: pd.DataFrame) -> io.BytesIO:
    """Gráfico de barras agrupadas: Inversión Publicitaria vs Ingresos por Ads."""
    fig, ax = plt.subplots(figsize=(6.2, 2.7))
    df_plot = df_semana.tail(10).copy()
    x = np.arange(len(df_plot))
    width = 0.35

    gasto = df_plot["Gasto Publicitario"]
    ing_ads = df_plot["Ingresos por Ads"]

    ax.bar(x - width/2, gasto, width, label="Gasto Publicitario", color="#A5D6A7", alpha=0.9)
    ax.bar(x + width/2, ing_ads, width, label="Ingresos por Ads", color="#124E3F", alpha=0.95)

    ax.set_title("Gasto Publicitario vs. Ingresos por Ads ($)", fontsize=9.5, fontweight="bold", color="#124E3F", pad=8)
    ax.set_xticks(x)
    ax.set_xticklabels([str(p) for p in df_plot["Periodo"]], rotation=40, fontsize=7, color="#222222")
    ax.set_ylabel("Monto ($)", fontsize=8, color="#222222")
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(format_currency_es))
    ax.tick_params(axis="y", labelsize=7.5, colors="#222222")
    ax.legend(fontsize=7.5, loc="upper left", frameon=True)
    ax.grid(True, linestyle="--", alpha=0.35, color="#CCCCCC")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    return fig_to_bytes(fig)


def make_roas_trend_chart(df_semana: pd.DataFrame) -> io.BytesIO:
    """Gráfico de tendencia de ROAS semanal."""
    fig, ax = plt.subplots(figsize=(6.2, 2.7))
    df_plot = df_semana.tail(10).copy()
    x_labels = [str(p) for p in df_plot["Periodo"]]
    roas_vals = df_plot["ROAS"]

    ax.plot(x_labels, roas_vals, marker="^", color="#25D366", linewidth=2.2, markersize=5.5)
    mean_roas_str = f"{roas_vals.mean():.2f}x".replace(".", ",")
    ax.axhline(roas_vals.mean(), color="#124E3F", linestyle=":", linewidth=1.3, label=f"Media: {mean_roas_str}")

    for i, txt in enumerate(roas_vals):
        lbl_roas = f"{txt:.1f}x".replace(".", ",")
        ax.annotate(lbl_roas, (i, roas_vals.iloc[i]), textcoords="offset points", xytext=(0, 6), ha="center", fontsize=6.8, color="#124E3F", fontweight="bold")

    ax.set_title("Evolución del ROAS Semanal (Multiplicador)", fontsize=9.5, fontweight="bold", color="#124E3F", pad=8)
    ax.set_ylabel("ROAS (x)", fontsize=8, color="#222222")
    ax.tick_params(axis="x", rotation=40, labelsize=7, colors="#222222")
    ax.tick_params(axis="y", labelsize=7.5, colors="#222222")
    ax.legend(fontsize=7.5, loc="upper right")
    ax.grid(True, linestyle="--", alpha=0.35, color="#CCCCCC")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    return fig_to_bytes(fig)


def make_daily_sales_bar_chart(df_ord_week: pd.DataFrame, periodo_str: str) -> io.BytesIO:
    """Gráfico de ventas diarias de la semana (Lunes a Domingo completo) con formato numérico en español."""
    fig, ax = plt.subplots(figsize=(6.2, 2.8))

    dias_orden = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    dias_map_es = {
        "Monday": "Lun", "Tuesday": "Mar", "Wednesday": "Mié",
        "Thursday": "Jue", "Friday": "Vie", "Saturday": "Sáb", "Sunday": "Dom"
    }

    # Dataframe base con los 7 días completos de la semana
    df_base = pd.DataFrame({
        "Dia Semana": dias_orden,
        "Dia_ES": [dias_map_es[d] for d in dias_orden],
        "Total": 0.0,
        "Order": range(7)
    })

    if not df_ord_week.empty and "Dia Semana" in df_ord_week.columns and "Total" in df_ord_week.columns:
        v_dia = df_ord_week.groupby("Dia Semana")["Total"].sum().reset_index()
        merged = df_base.merge(v_dia, on="Dia Semana", how="left", suffixes=("_base", ""))
        merged["Total"] = merged["Total"].fillna(0.0)
        v_dia = merged.sort_values(by="Order")
    else:
        v_dia = df_base

    bars = ax.bar(v_dia["Dia_ES"], v_dia["Total"], color="#124E3F", alpha=0.9, width=0.55)
    for bar in bars:
        yval = bar.get_height()
        if yval > 0:
            label_fmt = format_currency_es(yval)
            ax.text(bar.get_x() + bar.get_width()/2.0, yval + (yval * 0.02), label_fmt, ha="center", va="bottom", fontsize=6.8, fontweight="bold", color="#222222")

    ax.set_title(f"Ingresos por Día de la Semana ({periodo_str})", fontsize=9.5, fontweight="bold", color="#124E3F", pad=8)
    ax.set_ylabel("Monto ($)", fontsize=8, color="#222222")
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(format_currency_es))
    ax.tick_params(axis="x", labelsize=7.5, colors="#222222")
    ax.tick_params(axis="y", labelsize=7.5, colors="#222222")
    ax.grid(True, linestyle="--", alpha=0.35, color="#CCCCCC")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    return fig_to_bytes(fig)


def make_monthly_revenue_bar_chart(df_mensual: pd.DataFrame) -> io.BytesIO:
    """Gráfico de barras: Facturación mensual consolidada (12 meses)."""
    fig, ax = plt.subplots(figsize=(6.2, 2.7))
    x_labels = df_mensual["Mes_Label"].tolist() if "Mes_Label" in df_mensual.columns else [f"M{i+1}" for i in range(len(df_mensual))]
    y_vals = df_mensual["Ingresos"].tolist() if "Ingresos" in df_mensual.columns else [0] * len(x_labels)

    bars = ax.bar(x_labels, y_vals, color="#124E3F", alpha=0.9, width=0.55)
    for bar in bars:
        yval = bar.get_height()
        if yval > 0:
            label_fmt = format_currency_es(yval)
            ax.text(bar.get_x() + bar.get_width()/2.0, yval + (yval * 0.02), label_fmt, ha="center", va="bottom", fontsize=6.5, fontweight="bold", color="#222222")

    ax.set_title("Facturación Mensual Consolidada ($)", fontsize=9.5, fontweight="bold", color="#124E3F", pad=8)
    ax.set_ylabel("Monto ($)", fontsize=8, color="#222222")
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(format_currency_es))
    ax.tick_params(axis="x", rotation=30, labelsize=7, colors="#222222")
    ax.tick_params(axis="y", labelsize=7.5, colors="#222222")
    ax.grid(True, linestyle="--", alpha=0.35, color="#CCCCCC")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    return fig_to_bytes(fig)


def make_monthly_visitas_ops_chart(df_mensual: pd.DataFrame) -> io.BytesIO:
    """Gráfico dual: Visitas Totales Mensuales (Barras) vs Operaciones Concretadas (Línea)."""
    fig, ax1 = plt.subplots(figsize=(6.2, 2.7))
    x_labels = df_mensual["Mes_Label"].tolist() if "Mes_Label" in df_mensual.columns else [f"M{i+1}" for i in range(len(df_mensual))]
    vis_vals = df_mensual["Visitas"].tolist() if "Visitas" in df_mensual.columns else [0] * len(x_labels)
    ops_vals = df_mensual["Operaciones"].tolist() if "Operaciones" in df_mensual.columns else [0] * len(x_labels)

    ax1.bar(x_labels, vis_vals, color="#124E3F", alpha=0.35, label="Visitas Totales", width=0.55)
    ax1.set_ylabel("Visitas", fontsize=8, color="#124E3F")
    ax1.yaxis.set_major_formatter(ticker.FuncFormatter(format_number_es))
    ax1.tick_params(axis="x", rotation=30, labelsize=7, colors="#222222")
    ax1.tick_params(axis="y", labelsize=7.5, colors="#124E3F")
    ax1.grid(True, linestyle="--", alpha=0.35, color="#CCCCCC")

    ax2 = ax1.twinx()
    ax2.plot(x_labels, ops_vals, color="#25D366", linewidth=2.2, marker="s", markersize=4, label="Operaciones")
    ax2.set_ylabel("Operaciones", fontsize=8, color="#124E3F")
    ax2.yaxis.set_major_formatter(ticker.FuncFormatter(format_number_es))
    ax2.tick_params(axis="y", labelsize=7.5, colors="#124E3F")
    ax2.spines["top"].set_visible(False)

    ax1.set_title("Tráfico vs. Operaciones Mensuales", fontsize=9.5, fontweight="bold", color="#124E3F", pad=8)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)

    return fig_to_bytes(fig)


def make_revenue_mix_donut_chart(ing_ads: float, ing_org: float, periodo_str: str) -> io.BytesIO:
    """Gráfico de dona: Mix de ingresos Mercado Ads vs Orgánico con anillo extra grueso y porcentajes sin decimales."""
    fig, ax = plt.subplots(figsize=(4.8, 2.8))

    labels = ["Mercado Ads", "Ventas Orgánicas"]
    sizes = [max(0.0, ing_ads), max(0.0, ing_org)]
    # Tonos verdes sólidos corporativos para máximo contraste con texto blanco
    colors = ["#1E824C", "#124E3F"]

    if sum(sizes) > 0:
        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            autopct="%1.0f%%",
            startangle=90,
            colors=colors,
            pctdistance=0.60,
            wedgeprops=dict(width=0.72, edgecolor="white", linewidth=2.5),
            textprops=dict(fontsize=8.5, color="#222222", weight="bold")
        )
        # Porcentajes en blanco puro (#FFFFFF) destacados sobre el anillo extra grueso
        for autotext in autotexts:
            autotext.set_color("#FFFFFF")
            autotext.set_fontsize(10.0)
            autotext.set_weight("bold")
        for text in texts:
            text.set_color("#222222")
            text.set_fontsize(8.2)
            text.set_weight("bold")
    else:
        ax.text(0.5, 0.5, "Sin datos de pauta", ha="center", va="center", fontsize=8.5, color="#222222")

    ax.set_title(f"Mix de Ingresos ({periodo_str})", fontsize=9.5, fontweight="bold", color="#124E3F", pad=6)

    return fig_to_bytes(fig)


# ==========================================
# CLASE PRINCIPAL DEL REPORTE PDF
# ==========================================

class CLCPDFReport(FPDF):
    def __init__(self, period_str="", report_type="Reporte Mensual Ejecutivo"):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.period_str = period_str
        self.report_type = report_type
        self.set_auto_page_break(auto=True, margin=14)
        self.alias_nb_pages()

    def header(self):
        # Franja superior corporativa con Verde Principal #124E3F
        self.set_fill_color(18, 78, 63)
        self.rect(0, 0, 210, 23, "F")

        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 12)
        self.set_xy(12, 4.5)
        self.cell(115, 6, sanitize_text("CLC MERCADO LIBRE & PERFORMANCE"), 0, 0, "L")

        self.set_font("Helvetica", "I", 8.5)
        self.set_xy(12, 11.5)
        periodo_text = f"{self.report_type} | Período: {self.period_str}" if self.period_str else self.report_type
        self.cell(115, 6, sanitize_text(periodo_text), 0, 1, "L")

        # Logo del cliente en la esquina superior derecha (logo-white.png)
        import os
        logo_pdf_path = "logo-white.png" if os.path.exists("logo-white.png") else ("logo.png" if os.path.exists("logo.png") else None)
        if logo_pdf_path:
            try:
                self.image(logo_pdf_path, x=168, y=3.0, h=17)
            except Exception:
                now_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
                self.set_font("Helvetica", "", 7.5)
                self.set_xy(135, 4.5)
                self.cell(63, 6, sanitize_text(f"Emisión: {now_str}"), 0, 1, "R")
        else:
            now_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
            self.set_font("Helvetica", "", 7.5)
            self.set_xy(135, 4.5)
            self.cell(63, 6, sanitize_text(f"Emisión: {now_str}"), 0, 1, "R")

        self.set_text_color(34, 34, 34)  # Gris Oscuro #222222
        self.set_y(26)

    def footer(self):
        self.set_y(-11)
        self.set_draw_color(220, 224, 230)
        self.set_line_width(0.3)
        self.line(12, 286, 198, 286)

        self.set_font("Helvetica", "", 7.5)
        self.set_text_color(100, 100, 100)
        self.set_xy(12, -9)
        self.cell(100, 5, sanitize_text("CLC - Dashboard de Ventas y Rendimiento"), 0, 0, "L")
        self.set_xy(140, -9)
        self.cell(58, 5, sanitize_text(f"Página {self.page_no()} de {{nb}}"), 0, 0, "R")

    def section_heading(self, title: str, subtitle: str = ""):
        self.ln(2)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(18, 78, 63)  # Verde Principal #124E3F
        
        # Barra lateral decorativa con Verde Principal
        self.set_fill_color(18, 78, 63)
        self.rect(self.get_x(), self.get_y(), 2.8, 5.5, "F")
        self.set_x(self.get_x() + 4.5)
        
        self.cell(181, 5.5, sanitize_text(title), 0, 1, "L")
        self.set_text_color(34, 34, 34)  # Gris Oscuro #222222

        if subtitle:
            self.set_font("Helvetica", "I", 7.5)
            self.set_text_color(80, 80, 80)
            self.set_x(self.get_x() + 4.5)
            self.cell(181, 3.5, sanitize_text(subtitle), 0, 1, "L")
            self.set_text_color(34, 34, 34)
        self.ln(1.5)

    def render_kpi_cards(self, kpi_list):
        """Renderiza tarjetas KPI estilizadas en una cuadrícula uniforme fija (3 columnas x N filas)."""
        card_w = 58
        card_h = 16.5
        gap_x = 6
        gap_y = 3.5
        start_x = 12
        base_y = self.get_y()

        for idx, (label, val_str, desc) in enumerate(kpi_list):
            col = idx % 3
            row = idx // 3
            x = start_x + col * (card_w + gap_x)
            y = base_y + row * (card_h + gap_y)

            # Fondo tarjeta blanco #FFFFFF con borde gris suave
            self.set_fill_color(255, 255, 255)
            self.set_draw_color(220, 225, 230)
            self.set_line_width(0.3)
            self.rect(x, y, card_w, card_h, "DF")

            # Borde decorativo superior con Verde Acento #25D366
            self.set_fill_color(37, 211, 102)
            self.rect(x, y, card_w, 1.2, "F")

            # Etiqueta (Fila 1)
            self.set_xy(x + 2.5, y + 2.0)
            self.set_font("Helvetica", "B", 6.8)
            self.set_text_color(18, 78, 63)  # Verde Principal #124E3F
            self.cell(card_w - 5, 3.2, sanitize_text(label.upper()), 0, 0, "L")

            # Valor destacado (Fila 2)
            self.set_xy(x + 2.5, y + 5.5)
            self.set_font("Helvetica", "B", 10.5)
            self.set_text_color(34, 34, 34)  # Gris Oscuro #222222
            self.cell(card_w - 5, 5.5, sanitize_text(val_str), 0, 0, "L")

            # Descripción / Subtítulo / Delta (Fila 3)
            self.set_xy(x + 2.5, y + 11.2)
            self.set_font("Helvetica", "", 6.2)
            self.set_text_color(80, 80, 80)
            self.cell(card_w - 5, 3.2, sanitize_text(desc), 0, 0, "L")

        num_rows = (len(kpi_list) + 2) // 3
        self.set_y(base_y + num_rows * (card_h + gap_y) + 2.5)
        self.set_x(start_x)

    def render_table(self, headers, rows, col_widths, alignments=None, total_row=None, font_size=8.2):
        """Renderiza una tabla con formato corporativo, encabezado Verde Principal #124E3F, texto Gris Oscuro y tamaño de letra optimizado."""
        if alignments is None:
            alignments = ["L"] + ["R"] * (len(headers) - 1)

        header_font_size = font_size + 0.3
        row_font_size = font_size
        row_height = 5.2

        # Encabezado Verde Principal #124E3F
        self.set_font("Helvetica", "B", header_font_size)
        self.set_fill_color(18, 78, 63)
        self.set_text_color(255, 255, 255)
        self.set_draw_color(200, 200, 200)
        self.set_line_width(0.2)

        for i, header in enumerate(headers):
            self.cell(col_widths[i], 5.5, sanitize_text(header), 1, 0, alignments[i], fill=True)
        self.ln()

        # Filas
        self.set_font("Helvetica", "", row_font_size)
        self.set_text_color(34, 34, 34)  # Gris Oscuro #222222

        for row_idx, row_data in enumerate(rows):
            # Comprobar salto de página
            if self.get_y() > 268:
                self.add_page()
                # Reimprimir encabezado
                self.set_font("Helvetica", "B", header_font_size)
                self.set_fill_color(18, 78, 63)
                self.set_text_color(255, 255, 255)
                for i, header in enumerate(headers):
                    self.cell(col_widths[i], 5.5, sanitize_text(header), 1, 0, alignments[i], fill=True)
                self.ln()
                self.set_font("Helvetica", "", row_font_size)
                self.set_text_color(34, 34, 34)

            # Fondo alternado
            if row_idx % 2 == 0:
                self.set_fill_color(255, 255, 255)
            else:
                self.set_fill_color(245, 248, 246)

            for i, val in enumerate(row_data):
                self.cell(col_widths[i], row_height, sanitize_text(str(val)), 1, 0, alignments[i], fill=True)
            self.ln()

        # Fila de totales
        if total_row:
            self.set_font("Helvetica", "B", header_font_size)
            self.set_fill_color(232, 245, 240)
            self.set_text_color(18, 78, 63)
            for i, val in enumerate(total_row):
                self.cell(col_widths[i], 5.5, sanitize_text(str(val)), 1, 0, alignments[i], fill=True)
            self.ln()

        self.ln(2.5)


# ==========================================
# EXPORTADOR REPORTE MENSUAL (CON GRÁFICOS)
# ==========================================

def generate_monthly_pdf_report(
    df_ordenes_filt: pd.DataFrame,
    df_semana: pd.DataFrame,
    df_catalogo: pd.DataFrame,
    start_date=None,
    end_date=None,
    report_type: str = "Reporte Mensual Ejecutivo",
) -> bytes:
    """Genera el reporte mensual consolidado en formato PDF con gráficos y métricas integradas."""

    # 1. Periodo de análisis
    if start_date and end_date:
        period_str = f"{start_date.strftime('%d/%m/%Y')} al {end_date.strftime('%d/%m/%Y')}"
    elif not df_ordenes_filt.empty and "Fecha" in df_ordenes_filt.columns:
        valid_dates = df_ordenes_filt["Fecha"].dropna()
        if not valid_dates.empty:
            period_str = f"{valid_dates.min().strftime('%d/%m/%Y')} al {valid_dates.max().strftime('%d/%m/%Y')}"
        else:
            period_str = "Histórico Consolidado"
    else:
        period_str = "Histórico Consolidado"

    pdf = CLCPDFReport(period_str=period_str, report_type=report_type)
    
    # --- PÁGINA 1: RESUMEN EJECUTIVO & GRÁFICOS PRINCIPALES ---
    pdf.add_page()

    # Cálculos de KPIs
    tot_ingresos = df_ordenes_filt["Total"].sum() if not df_ordenes_filt.empty and "Total" in df_ordenes_filt.columns else 0.0
    tot_ordenes = len(df_ordenes_filt) if not df_ordenes_filt.empty else 0
    tot_unidades = int(df_ordenes_filt["Cantidad Total"].sum()) if not df_ordenes_filt.empty and "Cantidad Total" in df_ordenes_filt.columns else 0
    ticket_prom = tot_ingresos / tot_ordenes if tot_ordenes > 0 else 0.0

    roas_prom = 0.0
    tot_visitas = 0
    gasto_ads_total = 0.0
    ingresos_ads_total = 0.0
    if not df_semana.empty:
        if "ROAS" in df_semana.columns:
            roas_vals = df_semana["ROAS"].replace([np.inf, -np.inf], np.nan).dropna()
            if not roas_vals.empty:
                roas_prom = roas_vals.mean()
        if "Visitas Totales" in df_semana.columns:
            tot_visitas = int(df_semana["Visitas Totales"].sum())
        if "Gasto Publicitario" in df_semana.columns:
            gasto_ads_total = df_semana["Gasto Publicitario"].sum()
        if "Ingresos por Ads" in df_semana.columns:
            ingresos_ads_total = df_semana["Ingresos por Ads"].sum()

    kpi_cards = [
        ("Ingresos Totales", fmt_monto(tot_ingresos), "Facturación acumulada"),
        ("Total de Órdenes", fmt_entero(tot_ordenes), "Transacciones concretadas"),
        ("Unidades Vendidas", fmt_entero(tot_unidades), "Volumen de artículos"),
        ("Ticket Promedio", fmt_monto(ticket_prom), "Ingreso promedio por orden"),
        ("ROAS Promedio Ads", fmt_roas(roas_prom), "Retorno sobre inversión"),
        ("Visitas Totales", fmt_entero(tot_visitas), "Tráfico global acumulado"),
    ]

    pdf.section_heading("1. Resumen Ejecutivo & Indicadores Clave (KPIs)", "Principales métricas consolidadas del período")
    pdf.render_kpi_cards(kpi_cards)

    # Gráficos ejecutivos lado a lado
    if not df_semana.empty and len(df_semana) > 1:
        pdf.section_heading("2. Evolución Histórica de Ingresos y Conversión de Tráfico", "Comportamiento semanal de ventas e interacción de visitas")
        
        y_pos = pdf.get_y()
        chart_ing = make_weekly_revenue_chart(df_semana)
        chart_vis = make_visitas_ops_chart(df_semana)

        pdf.image(chart_ing, x=12, y=y_pos, w=90)
        pdf.image(chart_vis, x=106, y=y_pos, w=90)
        pdf.set_y(y_pos + 48)

    # Atribución por canales (Tabla)
    pdf.section_heading("3. Rendimiento por Canales & Atribución de Ventas", "Desglose entre Canal Publicitario (Mercado Ads) y Canal Orgánico")

    ingresos_organicos_total = max(0.0, tot_ingresos - ingresos_ads_total)
    pct_ads = (ingresos_ads_total / tot_ingresos * 100) if tot_ingresos > 0 else 0.0
    pct_org = (ingresos_organicos_total / tot_ingresos * 100) if tot_ingresos > 0 else 0.0

    channel_headers = ["Canal / Fuente", "Ingresos ($)", "% Total", "Gasto Ads ($)", "ROAS"]
    channel_widths = [50, 35, 25, 40, 36]
    channel_aligns = ["L", "R", "R", "R", "R"]

    roas_ads_calc = fmt_roas(ingresos_ads_total / gasto_ads_total) if gasto_ads_total > 0 else "0,00x"

    channel_rows = [
        [
            "Canal Publicitario (Mercado Ads)",
            fmt_monto(ingresos_ads_total),
            fmt_porcentaje(pct_ads),
            fmt_monto(gasto_ads_total),
            roas_ads_calc,
        ],
        [
            "Canal Orgánico & Directo",
            fmt_monto(ingresos_organicos_total),
            fmt_porcentaje(pct_org),
            "$0",
            "N/A",
        ],
    ]
    channel_totals = [
        "Total Consolidado",
        fmt_monto(tot_ingresos),
        "100,0%",
        fmt_monto(gasto_ads_total),
        fmt_roas(roas_prom),
    ]
    pdf.render_table(channel_headers, channel_rows, channel_widths, channel_aligns, channel_totals)

    # --- PÁGINA 2: PUBLICIDAD, HISTÓRICO Y CATÁLOGO ---
    pdf.add_page()

    if not df_semana.empty and len(df_semana) > 1:
        pdf.section_heading("4. Diagnóstico de Mercado Ads (Inversión vs. Retorno)", "Eficiencia presupuestaria y evolución del ROAS")
        
        y_pos2 = pdf.get_y()
        chart_ads = make_ads_vs_revenue_chart(df_semana)
        chart_roas = make_roas_trend_chart(df_semana)

        pdf.image(chart_ads, x=12, y=y_pos2, w=90)
        pdf.image(chart_roas, x=106, y=y_pos2, w=90)
        pdf.set_y(y_pos2 + 48)

    # Tabla Semanal
    if not df_semana.empty:
        pdf.section_heading("5. Detalle Histórico Semanal", "Últimas semanas de actividad registradas")
        sem_headers = ["Semana", "Visitas", "Operac.", "Ingresos ($)", "Gasto Ads ($)", "Ing. Ads ($)", "ROAS"]
        sem_widths = [26, 24, 20, 34, 30, 30, 22]
        sem_aligns = ["L", "R", "R", "R", "R", "R", "R"]

        sem_rows = []
        df_sem_display = df_semana.tail(8)
        for _, row in df_sem_display.iterrows():
            periodo = str(row.get("Periodo", ""))
            visitas = int(row.get("Visitas Totales", 0))
            operaciones = int(row.get("Cantidad de Operaciones", 0))
            ingresos = float(row.get("Ingresos Generados", 0.0))
            gasto_ads = float(row.get("Gasto Publicitario", 0.0))
            ing_ads = float(row.get("Ingresos por Ads", 0.0))
            roas_val = float(row.get("ROAS", 0.0))

            sem_rows.append([
                periodo,
                fmt_entero(visitas),
                fmt_entero(operaciones),
                fmt_monto(ingresos),
                fmt_monto(gasto_ads),
                fmt_monto(ing_ads),
                fmt_roas(roas_val),
            ])

        total_vis_sem = df_sem_display["Visitas Totales"].sum() if "Visitas Totales" in df_sem_display.columns else 0
        total_ops_sem = df_sem_display["Cantidad de Operaciones"].sum() if "Cantidad de Operaciones" in df_sem_display.columns else 0
        total_ing_sem = df_sem_display["Ingresos Generados"].sum() if "Ingresos Generados" in df_sem_display.columns else 0.0
        total_gasto_sem = df_sem_display["Gasto Publicitario"].sum() if "Gasto Publicitario" in df_sem_display.columns else 0.0
        total_ing_ads_sem = df_sem_display["Ingresos por Ads"].sum() if "Ingresos por Ads" in df_sem_display.columns else 0.0
        roas_calc_sem = (total_ing_ads_sem / total_gasto_sem) if total_gasto_sem > 0 else 0.0

        sem_totals = [
            "Total Muestra",
            fmt_entero(total_vis_sem),
            fmt_entero(total_ops_sem),
            fmt_monto(total_ing_sem),
            fmt_monto(total_gasto_sem),
            fmt_monto(total_ing_ads_sem),
            fmt_roas(roas_calc_sem),
        ]
        pdf.render_table(sem_headers, sem_rows, sem_widths, sem_aligns, sem_totals)

    # Catálogo
    if not df_catalogo.empty and "Categoria MeLi" in df_catalogo.columns and "Visitas Totales" in df_catalogo.columns:
        pdf.section_heading("6. Distribución de Catálogo por Categorías", "Resumen de publicaciones y tráfico por categoría MeLi")

        cat_summary = (
            df_catalogo.groupby("Categoria MeLi")
            .agg(
                Publicaciones=("Item ID", "count"),
                Visitas=("Visitas Totales", "sum"),
            )
            .reset_index()
            .sort_values(by="Visitas", ascending=False)
            .head(6)
        )

        cat_headers = ["Categoría MeLi", "Publicaciones", "Visitas Totales", "% Visitas"]
        cat_widths = [86, 32, 38, 30]
        cat_aligns = ["L", "R", "R", "R"]

        tot_cat_visitas = df_catalogo["Visitas Totales"].sum()
        cat_rows = []
        for _, r in cat_summary.iterrows():
            vis = int(r["Visitas"])
            pct = (vis / tot_cat_visitas * 100) if tot_cat_visitas > 0 else 0.0
            cat_rows.append([
                str(r["Categoria MeLi"])[:45],
                fmt_entero(r["Publicaciones"]),
                fmt_entero(vis),
                fmt_porcentaje(pct),
            ])

        cat_totals = [
            "Total Catálogo General",
            fmt_entero(len(df_catalogo)),
            fmt_entero(tot_cat_visitas),
            "100,0%",
        ]
        pdf.render_table(cat_headers, cat_rows, cat_widths, cat_aligns, cat_totals)

    return bytes(pdf.output())


# ==========================================
# EXPORTADOR REPORTE ANUAL (CONSOLIDADO 12 MESES)
# ==========================================

def generate_annual_pdf_report(
    df_semana: pd.DataFrame,
    df_ordenes: pd.DataFrame,
    df_catalogo: pd.DataFrame,
    start_date=None,
    end_date=None,
) -> bytes:
    """Genera el reporte ejecutivo anual / histórico consolidado en formato PDF basado en la compilación de 12 meses."""

    # 1. Rango de 12 meses (Agosto 2025 a Agosto 2026 o rango provisto)
    if start_date and end_date:
        start_12m = pd.to_datetime(start_date)
        end_12m = pd.to_datetime(end_date)
        period_str = f"{start_12m.strftime('%d/%m/%Y')} al {end_12m.strftime('%d/%m/%Y')}"
    else:
        start_12m = pd.Timestamp("2025-08-01")
        end_12m = pd.Timestamp("2026-08-31 23:59:59")
        period_str = "Agosto 2025 al Agosto 2026 (12 Meses)"

    # Filtrar df_semana
    if not df_semana.empty and "Fecha Inicio Semana" in df_semana.columns:
        df_sem_12m = df_semana[
            (df_semana['Fecha Inicio Semana'] >= start_12m) & 
            (df_semana['Fecha Inicio Semana'] <= end_12m)
        ].copy()
        if df_sem_12m.empty:
            max_dt = df_semana['Fecha Inicio Semana'].max()
            if pd.notna(max_dt):
                min_dt = max_dt - pd.DateOffset(months=12)
                df_sem_12m = df_semana[df_semana['Fecha Inicio Semana'] >= min_dt].copy()
            else:
                df_sem_12m = df_semana.copy()
    else:
        df_sem_12m = df_semana.copy()

    # Filtrar df_ordenes
    if not df_ordenes.empty and "Fecha" in df_ordenes.columns:
        df_ord_12m = df_ordenes[
            (df_ordenes['Fecha'] >= start_12m) & 
            (df_ordenes['Fecha'] <= end_12m)
        ].copy()
        if df_ord_12m.empty:
            max_dt_ord = df_ordenes['Fecha'].max()
            if pd.notna(max_dt_ord):
                min_dt_ord = max_dt_ord - pd.DateOffset(months=12)
                df_ord_12m = df_ordenes[df_ordenes['Fecha'] >= min_dt_ord].copy()
            else:
                df_ord_12m = df_ordenes.copy()
    else:
        df_ord_12m = df_ordenes.copy()

    pdf = CLCPDFReport(period_str=period_str, report_type="Reporte Anual / Historico Mensual")
    pdf.add_page()

    if df_sem_12m.empty:
        pdf.section_heading("Sin Informacion Disponible", "No se encontraron registros en el periodo de 12 meses.")
        return bytes(pdf.output())

    # 2. Agrupación mensual con Pandas
    df_sem_12m['Mes_Periodo'] = df_sem_12m['Fecha Inicio Semana'].dt.to_period('M')
    df_sem_12m['Mes_Inicio'] = df_sem_12m['Fecha Inicio Semana'].dt.to_period('M').dt.to_timestamp()

    meses_es = {1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr", 5: "May", 6: "Jun", 7: "Jul", 8: "Ago", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic"}
    df_sem_12m['Mes_Label'] = df_sem_12m['Mes_Inicio'].apply(lambda d: f"{meses_es.get(d.month, '')} {str(d.year)[2:]}" if pd.notna(d) else "")

    df_mensual = df_sem_12m.groupby(['Mes_Periodo', 'Mes_Inicio', 'Mes_Label']).agg(
        Ingresos=('Ingresos Generados', 'sum'),
        Operaciones=('Cantidad de Operaciones', 'sum'),
        Unidades=('Total de Unidades Vendidas', 'sum'),
        Visitas=('Visitas Totales', 'sum'),
        Gasto_Ads=('Gasto Publicitario', 'sum'),
        Ingresos_Ads=('Ingresos por Ads', 'sum'),
        Ingresos_Org=('Ingresos Organicos', 'sum'),
        Ventas_Ads=('Ventas Ads', 'sum')
    ).reset_index().sort_values(by='Mes_Inicio')

    df_mensual['ROAS'] = np.where(
        df_mensual['Gasto_Ads'] > 0,
        df_mensual['Ingresos_Ads'] / df_mensual['Gasto_Ads'],
        0.0
    )

    # 3. KPIs del Período
    tot_ing = df_mensual['Ingresos'].sum()
    tot_ops = int(df_mensual['Operaciones'].sum())
    tot_uni = int(df_mensual['Unidades'].sum())
    tot_vis = int(df_mensual['Visitas'].sum())
    tot_ads = df_mensual['Gasto_Ads'].sum()
    tot_ads_ing = df_mensual['Ingresos_Ads'].sum()
    roas_avg = (tot_ads_ing / tot_ads) if tot_ads > 0 else 0.0

    kpi_cards = [
        ("Ingresos Totales", fmt_monto(tot_ing), "Facturacion 12 meses"),
        ("Total Operaciones", fmt_entero(tot_ops), "Transacciones concretadas"),
        ("Unidades Vendidas", fmt_entero(tot_uni), "Articulos despachados"),
        ("Visitas Totales", fmt_entero(tot_vis), "Trafico global consolidado"),
        ("Gasto Publicitario", fmt_monto(tot_ads), "Inversion en Ads"),
        ("ROAS Promedio", fmt_roas(roas_avg), "Retorno sobre inversion"),
    ]

    pdf.section_heading("1. Resumen Ejecutivo Anual (12 Meses Acumulados)", "Consolidado historico de indicadores clave de rendimiento")
    pdf.render_kpi_cards(kpi_cards)

    # 4. Gráficos Ejecutivos Mensuales
    pdf.section_heading("2. Evolucion Mensual de Facturacion y Trafico", "Comportamiento mes a mes de los ingresos y operaciones")
    y_pos = pdf.get_y()
    chart_ing_m = make_monthly_revenue_bar_chart(df_mensual)
    chart_vis_m = make_monthly_visitas_ops_chart(df_mensual)
    pdf.image(chart_ing_m, x=12, y=y_pos, w=90)
    pdf.image(chart_vis_m, x=106, y=y_pos, w=90)
    pdf.set_y(y_pos + 48)

    # 5. Tabla de Desglose Mensual
    pdf.section_heading("3. Detalle Mensual Consolidado", "Desglose financiero y operativo por cada mes del periodo")
    m_headers = ["Mes", "Ingresos ($)", "Operaciones", "Unidades", "Gasto Ads ($)", "ROAS"]
    m_widths = [32, 36, 28, 28, 36, 26]
    m_aligns = ["L", "R", "R", "R", "R", "R"]

    m_rows = []
    for _, r in df_mensual.iterrows():
        m_rows.append([
            str(r["Mes_Label"]),
            fmt_monto(r["Ingresos"]),
            fmt_entero(r["Operaciones"]),
            fmt_entero(r["Unidades"]),
            fmt_monto(r["Gasto_Ads"]),
            fmt_roas(r["ROAS"]),
        ])

    m_totals = [
        "Total 12 Meses",
        fmt_monto(tot_ing),
        fmt_entero(tot_ops),
        fmt_entero(tot_uni),
        fmt_monto(tot_ads),
        fmt_roas(roas_avg),
    ]
    pdf.render_table(m_headers, m_rows, m_widths, m_aligns, m_totals)

    # 6. Top 10 Artículos Más Vendidos en 12 Meses
    if not df_ord_12m.empty and "Producto(s)" in df_ord_12m.columns:
        pdf.section_heading("4. Top 10 Articulos Mas Vendidos (12 Meses)", "Ranking de productos por facturacion acumulada en el periodo")
        top_art = (
            df_ord_12m.groupby("Producto(s)")
            .agg(
                Unidades=("Cantidad Total", "sum") if "Cantidad Total" in df_ord_12m.columns else ("Order ID", "count"),
                Total=("Total", "sum") if "Total" in df_ord_12m.columns else ("Order ID", "count"),
            )
            .reset_index()
            .sort_values(by="Total", ascending=False)
            .head(10)
        )

        art_headers = ["Producto / Publicacion", "Unidades", "Facturacion ($)", "% del Total"]
        art_widths = [96, 26, 36, 28]
        art_aligns = ["L", "R", "R", "R"]

        art_rows = []
        for _, r in top_art.iterrows():
            tot_p = float(r["Total"])
            pct_p = (tot_p / tot_ing * 100) if tot_ing > 0 else 0.0
            art_rows.append([
                str(r["Producto(s)"])[:50],
                fmt_entero(r["Unidades"]),
                fmt_monto(tot_p),
                fmt_porcentaje(pct_p),
            ])

        art_totals = [
            "Total Top 10",
            fmt_entero(top_art["Unidades"].sum()),
            fmt_monto(top_art["Total"].sum()),
            fmt_porcentaje(top_art["Total"].sum() / tot_ing * 100) if tot_ing > 0 else "0,0%",
        ]
        pdf.render_table(art_headers, art_rows, art_widths, art_aligns, art_totals)

    # 7. Marcas Más Vendidas en 12 Meses
    if not df_ord_12m.empty and not df_catalogo.empty and "Item ID" in df_ord_12m.columns and "Marca" in df_catalogo.columns:
        pdf.section_heading("5. Marcas Mas Vendidas (12 Meses)", "Distribucion de ventas por marca en el ciclo consolidado")
        df_ord_m = df_ord_12m.merge(df_catalogo[["Item ID", "Marca"]].drop_duplicates(subset=["Item ID"]), on="Item ID", how="left")
        df_ord_m["Marca"] = df_ord_m["Marca"].fillna("Sin Marca / Otra")

        top_marcas = (
            df_ord_m.groupby("Marca")
            .agg(
                Unidades=("Cantidad Total", "sum") if "Cantidad Total" in df_ord_m.columns else ("Order ID", "count"),
                Total=("Total", "sum") if "Total" in df_ord_m.columns else ("Order ID", "count"),
            )
            .reset_index()
            .sort_values(by="Total", ascending=False)
        )

        marca_headers = ["Marca", "Unidades", "Facturacion ($)", "% del Total"]
        marca_widths = [96, 26, 36, 28]
        marca_aligns = ["L", "R", "R", "R"]

        marca_rows = []
        for _, r in top_marcas.iterrows():
            tot_m = float(r["Total"])
            pct_m = (tot_m / tot_ing * 100) if tot_ing > 0 else 0.0
            marca_rows.append([
                str(r["Marca"])[:50],
                fmt_entero(r["Unidades"]),
                fmt_monto(tot_m),
                fmt_porcentaje(pct_m),
            ])

        marca_totals = [
            "Total Marcas",
            fmt_entero(top_marcas["Unidades"].sum()),
            fmt_monto(top_marcas["Total"].sum()),
            fmt_porcentaje(top_marcas["Total"].sum() / tot_ing * 100) if tot_ing > 0 else "0,0%",
        ]
        pdf.render_table(marca_headers, marca_rows, marca_widths, marca_aligns, marca_totals)

    return bytes(pdf.output())


# ==========================================
# EXPORTADOR REPORTE SEMANAL (CON GRÁFICOS)
# ==========================================

def generate_weekly_pdf_report(
    df_semana: pd.DataFrame,
    df_ordenes: pd.DataFrame,
    df_catalogo: pd.DataFrame,
    week_index: int = -1,
) -> bytes:
    """Genera el reporte ejecutivo semanal enfocado en la última semana registrada con métricas vs. semana anterior y gráficos."""
    if df_semana.empty:
        pdf = CLCPDFReport(period_str="Sin Datos", report_type="Reporte Semanal Ejecutivo")
        pdf.add_page()
        pdf.section_heading("Sin Información Disponible", "No se encontraron registros semanales.")
        return bytes(pdf.output())

    df_sem_sorted = df_semana.sort_values(by="Fecha Inicio Semana") if "Fecha Inicio Semana" in df_semana.columns else df_semana
    last_row = df_sem_sorted.iloc[week_index]
    prev_row = df_sem_sorted.iloc[week_index - 1] if len(df_sem_sorted) > 1 and (week_index == -1 or week_index > 0) else None

    periodo_actual = str(last_row.get("Periodo", "Última Semana"))
    fecha_inicio = last_row.get("Fecha Inicio Semana")
    
    if pd.notna(fecha_inicio):
        fecha_fin = fecha_inicio + pd.Timedelta(days=6)
        period_str = f"{periodo_actual} ({fecha_inicio.strftime('%d/%m/%Y')} al {fecha_fin.strftime('%d/%m/%Y')})"
    else:
        period_str = periodo_actual

    pdf = CLCPDFReport(period_str=period_str, report_type="Reporte Semanal Ejecutivo")
    pdf.add_page()

    # 1. KPIs con Variación vs. Semana Anterior (reemplazo de WoW)
    ing_act = float(last_row.get("Ingresos Generados", 0.0))
    ing_prev = float(prev_row.get("Ingresos Generados", 0.0)) if prev_row is not None else 0.0
    delta_ing = f"{((ing_act - ing_prev) / ing_prev * 100):+.0f}% vs. semana anterior" if ing_prev > 0 else "vs. semana anterior N/A"

    ops_act = int(last_row.get("Cantidad de Operaciones", 0))
    ops_prev = int(prev_row.get("Cantidad de Operaciones", 0)) if prev_row is not None else 0
    delta_ops = f"{((ops_act - ops_prev) / ops_prev * 100):+.0f}% vs. semana anterior" if ops_prev > 0 else "vs. semana anterior N/A"

    uni_act = int(last_row.get("Total de Unidades Vendidas", 0))
    uni_prev = int(prev_row.get("Total de Unidades Vendidas", 0)) if prev_row is not None else 0
    delta_uni = f"{((uni_act - uni_prev) / uni_prev * 100):+.0f}% vs. semana anterior" if uni_prev > 0 else "vs. semana anterior N/A"

    vis_act = int(last_row.get("Visitas Totales", 0))
    vis_prev = int(prev_row.get("Visitas Totales", 0)) if prev_row is not None else 0
    delta_vis = f"{((vis_act - vis_prev) / vis_prev * 100):+.0f}% vs. semana anterior" if vis_prev > 0 else "vs. semana anterior N/A"

    roas_act = float(last_row.get("ROAS", 0.0))
    roas_prev = float(prev_row.get("ROAS", 0.0)) if prev_row is not None else 0.0
    delta_roas = f"{(roas_act - roas_prev):+.2f}x".replace(".", ",") + " vs. semana anterior" if prev_row is not None else "vs. semana anterior N/A"

    gasto_act = float(last_row.get("Gasto Publicitario", 0.0))
    gasto_prev = float(prev_row.get("Gasto Publicitario", 0.0)) if prev_row is not None else 0.0
    delta_gasto = f"{((gasto_act - gasto_prev) / gasto_prev * 100):+.0f}% vs. semana anterior" if gasto_prev > 0 else "vs. semana anterior N/A"

    kpi_cards = [
        ("Ingresos Totales", fmt_monto(ing_act), f"Var: {delta_ing}"),
        ("Operaciones Concretadas", fmt_entero(ops_act), f"Var: {delta_ops}"),
        ("Unidades Vendidas", fmt_entero(uni_act), f"Var: {delta_uni}"),
        ("Visitas Totales", fmt_entero(vis_act), f"Var: {delta_vis}"),
        ("ROAS Mercado Ads", fmt_roas(roas_act), f"Var: {delta_roas}"),
        ("Gasto Publicitario", fmt_monto(gasto_act), f"Var: {delta_gasto}"),
    ]

    # --- SECCIÓN 1: RESUMEN DE KPIS DE LA SEMANA ---
    pdf.section_heading("1. Indicadores Clave de la Semana", "Comparativa directa contra la semana anterior inmediata")
    pdf.render_kpi_cards(kpi_cards)

    # --- FILTRAR ÓRDENES DE LA SEMANA ---
    df_ord_last = pd.DataFrame()
    if not df_ordenes.empty and "Fecha" in df_ordenes.columns and pd.notna(fecha_inicio):
        fecha_fin_dt = fecha_inicio + pd.Timedelta(days=6)
        df_ord_last = df_ordenes[
            (df_ordenes["Fecha"].dt.date >= fecha_inicio.date()) & 
            (df_ordenes["Fecha"].dt.date <= fecha_fin_dt.date())
        ]

    # --- SECCIÓN 2: GRÁFICOS DE LA SEMANA (VENTAS DIARIAS & MIX ADS VS ORGÁNICO) ---
    pdf.section_heading("2. Gráficos de Rendimiento y Mix Semanal", "Evolución cronológica diaria y proporción de ventas")

    ing_ads = float(last_row.get("Ingresos por Ads", 0.0))
    ing_org = float(last_row.get("Ingresos Organicos", max(0.0, ing_act - ing_ads)))

    y_pos_w = pdf.get_y()
    chart_daily = make_daily_sales_bar_chart(df_ord_last, periodo_actual)
    chart_donut = make_revenue_mix_donut_chart(ing_ads, ing_org, periodo_actual)

    pdf.image(chart_daily, x=12, y=y_pos_w, w=106)
    pdf.image(chart_donut, x=120, y=y_pos_w, w=78)
    # Margen vertical inferior generoso
    pdf.set_y(y_pos_w + 54)

    # --- SECCIÓN 3: ATRIBUCIÓN Y CANALES SEMANAL ---
    pdf.section_heading("3. Mix de Ventas & Rendimiento de Canales", "Atribución entre Canal Publicitario (Mercado Ads) y Canal Orgánico")

    pct_ads = (ing_ads / ing_act * 100) if ing_act > 0 else 0.0
    pct_org = (ing_org / ing_act * 100) if ing_act > 0 else 0.0

    ch_headers = ["Canal / Fuente", "Ingresos Semanales ($)", "% Mix", "Gasto Ads ($)", "ROAS"]
    ch_widths = [55, 38, 25, 36, 32]
    ch_aligns = ["L", "R", "R", "R", "R"]

    roas_ads_sem_calc = fmt_roas(ing_ads / gasto_act) if gasto_act > 0 else "0,00x"

    ch_rows = [
        [
            "Canal Publicitario (Mercado Ads)",
            fmt_monto(ing_ads),
            fmt_porcentaje(pct_ads),
            fmt_monto(gasto_act),
            roas_ads_sem_calc,
        ],
        [
            "Canal Orgánico & Directo",
            fmt_monto(ing_org),
            fmt_porcentaje(pct_org),
            "$0",
            "N/A",
        ],
    ]
    ch_totals = [
        "Total Semana",
        fmt_monto(ing_act),
        "100,0%",
        fmt_monto(gasto_act),
        fmt_roas(roas_act),
    ]
    pdf.render_table(ch_headers, ch_rows, ch_widths, ch_aligns, ch_totals)

    # --- PÁGINA 2: DESGLOSE DIARIO Y ARTÍCULOS VENDIDOS (SALTO DE PÁGINA FORZADO) ---
    pdf.add_page()

    # --- SECCIÓN 4: DESGLOSE DIARIO DE LA SEMANA ---
    pdf.section_heading("4. Evolución Diaria de Ventas", "Comportamiento y recaudación por día de la semana (Lunes a Domingo)")

    dias_orden = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    dias_map_es = {
        "Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles",
        "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo"
    }

    df_base_tab = pd.DataFrame({
        "Dia Semana": dias_orden,
        "Dia_ES": [dias_map_es[d] for d in dias_orden],
        "Transacciones": 0,
        "Unidades": 0,
        "Ingresos": 0.0,
        "Sort_Order": range(7)
    })

    if not df_ord_last.empty and "Dia Semana" in df_ord_last.columns and "Total" in df_ord_last.columns:
        v_agg = (
            df_ord_last.groupby("Dia Semana")
            .agg(
                Transacciones=("Order ID", "count"),
                Unidades=("Cantidad Total", "sum") if "Cantidad Total" in df_ord_last.columns else ("Order ID", "count"),
                Ingresos=("Total", "sum"),
            )
            .reset_index()
        )
        merged_tab = df_base_tab.merge(v_agg, on="Dia Semana", how="left", suffixes=("_base", ""))
        merged_tab["Transacciones"] = merged_tab["Transacciones"].fillna(0).astype(int)
        merged_tab["Unidades"] = merged_tab["Unidades"].fillna(0).astype(int)
        merged_tab["Ingresos"] = merged_tab["Ingresos"].fillna(0.0)
        ventas_dia = merged_tab.sort_values(by="Sort_Order")
    else:
        ventas_dia = df_base_tab

    dia_headers = ["Día", "Órdenes", "Unidades", "Ingresos ($)", "% Total Semana"]
    dia_widths = [46, 30, 30, 42, 38]
    dia_aligns = ["L", "R", "R", "R", "R"]

    dia_rows = []
    tot_dia_ing = ventas_dia["Ingresos"].sum()
    for _, r in ventas_dia.iterrows():
        ing_d = float(r["Ingresos"])
        pct_d = (ing_d / tot_dia_ing * 100) if tot_dia_ing > 0 else 0.0
        dia_rows.append([
            str(r["Dia_ES"]),
            fmt_entero(r['Transacciones']),
            fmt_entero(r['Unidades']),
            fmt_monto(ing_d),
            fmt_porcentaje(pct_d),
        ])

    dia_totals = [
        "Total Semanal",
        fmt_entero(ventas_dia['Transacciones'].sum()),
        fmt_entero(ventas_dia['Unidades'].sum()),
        fmt_monto(tot_dia_ing),
        "100,0%",
    ]
    pdf.render_table(dia_headers, dia_rows, dia_widths, dia_aligns, dia_totals)

    # --- SECCIÓN 5: TOP 10 PRODUCTOS VENDIDOS EN LA SEMANA ---
    if not df_ord_last.empty and "Producto(s)" in df_ord_last.columns:
        pdf.section_heading("5. Top 10 Artículos Más Vendidos en la Semana", "Ranking de productos por facturación acumulada")

        top_prod = (
            df_ord_last.groupby("Producto(s)")
            .agg(
                Unidades=("Cantidad Total", "sum") if "Cantidad Total" in df_ord_last.columns else ("Order ID", "count"),
                Total=("Total", "sum"),
            )
            .reset_index()
            .sort_values(by="Total", ascending=False)
            .head(10)
        )

        prod_headers = ["Producto / Publicación", "Unidades Vendidas", "Facturación ($)", "% de la Semana"]
        prod_widths = [96, 30, 32, 28]
        prod_aligns = ["L", "R", "R", "R"]

        prod_rows = []
        for _, r in top_prod.iterrows():
            tot_p = float(r["Total"])
            pct_p = (tot_p / ing_act * 100) if ing_act > 0 else 0.0
            prod_rows.append([
                str(r["Producto(s)"])[:50],
                fmt_entero(r['Unidades']),
                fmt_monto(tot_p),
                fmt_porcentaje(pct_p),
            ])

        prod_totals = [
            "Total Top Productos",
            fmt_entero(top_prod['Unidades'].sum()),
            fmt_monto(top_prod['Total'].sum()),
            fmt_porcentaje(top_prod['Total'].sum() / ing_act * 100) if ing_act > 0 else "0,0%",
        ]
        pdf.render_table(prod_headers, prod_rows, prod_widths, prod_aligns, prod_totals)

    # --- SECCIÓN 6: MARCAS MÁS VENDIDAS EN LA SEMANA ---
    if not df_ord_last.empty and not df_catalogo.empty and "Item ID" in df_ord_last.columns and "Marca" in df_catalogo.columns:
        pdf.section_heading("6. Marcas Más Vendidas en la Semana", "Distribución de ventas y unidades por marca")

        df_ord_marca = df_ord_last.merge(df_catalogo[["Item ID", "Marca"]].drop_duplicates(subset=["Item ID"]), on="Item ID", how="left")
        df_ord_marca["Marca"] = df_ord_marca["Marca"].fillna("Sin Marca / Otra")

        top_marcas = (
            df_ord_marca.groupby("Marca")
            .agg(
                Unidades=("Cantidad Total", "sum") if "Cantidad Total" in df_ord_marca.columns else ("Order ID", "count"),
                Total=("Total", "sum"),
            )
            .reset_index()
            .sort_values(by="Total", ascending=False)
        )

        marca_headers = ["Marca", "Unidades Vendidas", "Facturación ($)", "% de la Semana"]
        marca_widths = [96, 30, 32, 28]
        marca_aligns = ["L", "R", "R", "R"]

        marca_rows = []
        for _, r in top_marcas.iterrows():
            tot_m = float(r["Total"])
            pct_m = (tot_m / ing_act * 100) if ing_act > 0 else 0.0
            marca_rows.append([
                str(r["Marca"])[:50],
                fmt_entero(r['Unidades']),
                fmt_monto(tot_m),
                fmt_porcentaje(pct_m),
            ])

        marca_totals = [
            "Total Marcas",
            fmt_entero(top_marcas['Unidades'].sum()),
            fmt_monto(top_marcas['Total'].sum()),
            fmt_porcentaje(top_marcas['Total'].sum() / ing_act * 100) if ing_act > 0 else "0,0%",
        ]
        pdf.render_table(marca_headers, marca_rows, marca_widths, marca_aligns, marca_totals)

    return bytes(pdf.output())
