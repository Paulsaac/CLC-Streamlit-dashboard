import os
import smtplib
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import streamlit as st


def enviar_reporte_email(ruta_pdf: str, destinatario: str) -> bool:
    """
    Envía un reporte PDF adjunto por correo electrónico a través del servidor SMTP de Gmail.

    Parámetros:
    -----------
    ruta_pdf : str
        Ruta local del archivo PDF a adjuntar (ej. 'reporte_semanal_clc.pdf').
    destinatario : str
        Correo electrónico del destinatario (ej. 'cliente@empresa.com').

    Retorna:
    --------
    bool
        True si el correo fue enviado exitosamente, False si ocurrió algún error.
    """
    # 1. Leer credenciales de forma segura desde st.secrets
    try:
        remitente = st.secrets["EMAIL_USER"]
        password = st.secrets["EMAIL_PASSWORD"]
    except KeyError as e:
        print(f"❌ [EMAIL_ERROR] Clave de secreto faltante en .streamlit/secrets.toml: {e}")
        return False
    except Exception as e:
        print(f"❌ [EMAIL_ERROR] No se pudieron cargar las credenciales desde st.secrets: {e}")
        return False

    # 2. Validar existencia del archivo PDF
    pdf_path = Path(ruta_pdf)
    if not pdf_path.exists() or not pdf_path.is_file():
        print(f"❌ [EMAIL_ERROR] El archivo PDF no existe en la ruta especificada: '{ruta_pdf}'")
        return False

    try:
        # 3. Configuración del servidor SMTP (Gmail)
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        asunto = "Reporte Semanal CLC - Mercado Libre & Performance"

        # 4. Construcción del mensaje MIME
        mensaje = MIMEMultipart()
        mensaje["From"] = f"CLC Reportes <{remitente}>"
        mensaje["To"] = destinatario
        mensaje["Subject"] = asunto

        # Cuerpo del correo en formato HTML
        cuerpo_html = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
        </head>
        <body style="font-family: 'Segoe UI', Arial, sans-serif; color: #222222; margin: 0; padding: 20px; background-color: #F8FAF9;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #FFFFFF; border: 1px solid #E0E4E8; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 6px rgba(0,0,0,0.05);">
                
                <div style="background-color: #124E3F; padding: 20px 24px; color: #FFFFFF;">
                    <h2 style="margin: 0; font-size: 1.3rem;">CLC Mercado Libre</h2>
                    <p style="margin: 4px 0 0 0; font-size: 0.85rem; color: #A5D6A7;">Reporte Ejecutivo de Rendimiento & Performance</p>
                </div>

                <div style="padding: 24px;">
                    <p style="margin-top: 0; font-size: 1rem;">Estimado/a,</p>
                    
                    <p style="line-height: 1.5; color: #333333;">
                        Adjunto a este correo encontrarás el <strong>Reporte Semanal de Rendimiento</strong> en formato PDF, con el resumen de métricas clave, evolución de ventas y diagnóstico de Mercado Ads.
                    </p>
                    
                    <div style="background-color: #F0F7F4; border-left: 4px solid #25D366; padding: 12px 16px; margin: 18px 0; border-radius: 4px;">
                        <p style="margin: 0; font-size: 0.9rem; color: #124E3F;">
                            📎 <strong>Archivo adjunto:</strong> <span style="color: #222222; font-weight: 600;">{pdf_path.name}</span>
                        </p>
                    </div>

                    <p style="font-size: 0.9rem; color: #555555; line-height: 1.5;">
                        Quedamos a tu disposición ante cualquier duda o requerimiento sobre la información presentada.
                    </p>

                    <p style="margin-bottom: 0; color: #222222; font-size: 0.95rem;">
                        Saludos cordiales,<br>
                        <strong>Equipo de Analítica & Operaciones - CLC</strong>
                    </p>
                </div>

                <div style="background-color: #F8FAF9; padding: 12px 24px; border-top: 1px solid #EAEAEA; text-align: center;">
                    <p style="margin: 0; font-size: 0.75rem; color: #888888;">
                        Mensaje generado automáticamente por el sistema de reportes de CLC.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        mensaje.attach(MIMEText(cuerpo_html, "html", "utf-8"))

        # 5. Adjuntar el archivo PDF
        with open(pdf_path, "rb") as archivo:
            adjunto = MIMEApplication(archivo.read(), _subtype="pdf")
            adjunto.add_header(
                "Content-Disposition",
                "attachment",
                filename=pdf_path.name
            )
            mensaje.attach(adjunto)

        # 6. Conexión SMTP y envío con autenticación TLS
        print(f"🔄 Conectando al servidor SMTP ({smtp_server}:{smtp_port})...")
        with smtplib.SMTP(smtp_server, smtp_port, timeout=25) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(remitente, password)
            server.sendmail(remitente, [destinatario], mensaje.as_string())

        print(f"✅ [EMAIL_SUCCESS] Reporte enviado exitosamente a: {destinatario}")
        return True

    except Exception as e:
        print(f"❌ [EMAIL_ERROR] Error durante el envío del correo: {e}")
        return False
