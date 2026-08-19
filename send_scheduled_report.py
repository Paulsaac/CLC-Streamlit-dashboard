import os
import sys
from data_loader import load_all_data
from pdf_generator import generate_weekly_pdf_report
from email_service import enviar_reporte_email

# Destinatarios por defecto si no se especifican por variable de entorno
DESTINATARIOS_DEFAULT = ["paulsaac@gmail.com", "franco@leveraweb.com"]


def main():
    print("🚀 [CRON] Iniciando proceso automático de reporte...")

    # 1. Cargar datos desde Google Sheets
    print("📥 [CRON] Descargando datos desde Google Sheets...")
    try:
        df_semana, df_catalogo, df_ordenes = load_all_data()
    except Exception as e:
        print(f"❌ [CRON_ERROR] Fallo al conectar con Google Sheets: {e}")
        sys.exit(1)

    if df_semana.empty:
        print("❌ [CRON_ERROR] No se encontraron registros en la hoja 'Semana'.")
        sys.exit(1)

    # 2. Generar PDF semanal
    print("📄 [CRON] Generando reporte semanal en formato PDF...")
    try:
        pdf_bytes = generate_weekly_pdf_report(
            df_semana=df_semana,
            df_ordenes=df_ordenes,
            df_catalogo=df_catalogo
        )
    except Exception as e:
        print(f"❌ [CRON_ERROR] Fallo al compilar el PDF: {e}")
        sys.exit(1)

    pdf_path = "reporte_semanal_clc.pdf"
    with open(pdf_path, "wb") as f:
        f.write(pdf_bytes)
    print(f"✅ [CRON] PDF compilado y guardado en: {pdf_path}")

    # 3. Determinar lista de destinatarios
    destinatarios_env = os.getenv("REPORT_RECIPIENTS")
    if destinatarios_env:
        destinatarios = [d.strip() for d in destinatarios_env.split(",") if d.strip()]
    else:
        destinatarios = DESTINATARIOS_DEFAULT

    print(f"📧 [CRON] Enviando reporte a: {destinatarios}...")
    exito_total = True
    for email in destinatarios:
        ok = enviar_reporte_email(pdf_path, email)
        if ok:
            print(f"   ✅ Reporte enviado a: {email}")
        else:
            print(f"   ❌ Error al enviar reporte a: {email}")
            exito_total = False

    # 4. Limpieza del archivo temporal
    if os.path.exists(pdf_path):
        os.remove(pdf_path)

    if not exito_total:
        print("⚠️ [CRON] Hubo errores en el envío de uno o más correos.")
        sys.exit(1)

    print("🎉 [CRON] Proceso finalizado exitosamente.")


if __name__ == "__main__":
    main()
