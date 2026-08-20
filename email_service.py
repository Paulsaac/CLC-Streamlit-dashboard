import os
import smtplib
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import streamlit as st


def obtener_configuracion_email():
    """
    Obtiene la configuración del servicio de correo buscando primero en st.secrets
    y luego en variables de entorno como fallback.
    """
    # Función auxiliar para leer desde secrets o env
    def get_val(key, default=None):
        try:
            if key in st.secrets:
                return st.secrets[key]
        except Exception:
            pass
        return os.getenv(key, default)

    email_user = get_val("EMAIL_USER")
    smtp_user = get_val("SMTP_USER")
    smtp_server = get_val("SMTP_HOST") or get_val("EMAIL_HOST", "smtp.gmail.com")
    password = get_val("EMAIL_PASSWORD") or get_val("SMTP_PASSWORD") or get_val("RESEND_API_KEY")

    # Si se utiliza Resend, el usuario SMTP de autenticación siempre es 'resend'
    if "resend" in smtp_server.lower() or (password and str(password).startswith("re_")):
        if not get_val("SMTP_HOST"):
            smtp_server = "smtp.resend.com"
        auth_user = smtp_user or "resend"
        from_email = get_val("EMAIL_FROM") or email_user or "onboarding@resend.dev"
    else:
        auth_user = smtp_user or email_user
        from_email = get_val("EMAIL_FROM") or email_user

    smtp_port = int(get_val("SMTP_PORT", get_val("EMAIL_PORT", 465 if "resend" in smtp_server.lower() else 587)))
    sender_name = get_val("EMAIL_SENDER_NAME", "CLC Reportes - Mercado Libre")
    use_ssl = get_val("SMTP_USE_SSL", False)

    # Si el puerto es 465, activar SSL por defecto
    if smtp_port == 465 or str(use_ssl).lower() in ("true", "1", "yes"):
        use_ssl = True

    return {
        "auth_user": auth_user,
        "from_email": from_email,
        "password": password,
        "smtp_server": smtp_server,
        "smtp_port": smtp_port,
        "sender_name": sender_name,
        "use_ssl": use_ssl
    }



def enviar_reporte_email(ruta_pdf: str, destinatario: str) -> bool:
    """
    Envía un reporte PDF adjunto por correo electrónico a través de un servidor SMTP configurable
    (soporta Gmail, Cloudflare, servidores corporativos de leveraweb.com, Resend, etc.).

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
    # 1. Obtener credenciales y configuración
    config = obtener_configuracion_email()
    auth_user = config["auth_user"]
    from_email = config["from_email"]
    password = config["password"]
    smtp_server = config["smtp_server"]
    smtp_port = config["smtp_port"]
    sender_name = config["sender_name"]
    use_ssl = config["use_ssl"]

    if not auth_user or not password:
        print("❌ [EMAIL_ERROR] Credenciales de autenticación no encontradas en configuración.")
        return False

    # 2. Validar existencia del archivo PDF
    pdf_path = Path(ruta_pdf)
    if not pdf_path.exists() or not pdf_path.is_file():
        print(f"❌ [EMAIL_ERROR] El archivo PDF no existe en la ruta especificada: '{ruta_pdf}'")
        return False

    try:
        asunto = "Reporte Semanal CLC - Mercado Libre & Performance"

        # 3. Construcción del mensaje MIME
        mensaje = MIMEMultipart()
        mensaje["From"] = f"{sender_name} <{from_email}>"
        mensaje["To"] = destinatario
        mensaje["Subject"] = asunto

        # Cuerpo del correo en formato HTML profesional
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
                        Mensaje generado automáticamente por el sistema de reportes de CLC Maderas ({from_email}).
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        mensaje.attach(MIMEText(cuerpo_html, "html", "utf-8"))

        # 4. Adjuntar el archivo PDF
        with open(pdf_path, "rb") as archivo:
            adjunto = MIMEApplication(archivo.read(), _subtype="pdf")
            adjunto.add_header(
                "Content-Disposition",
                "attachment",
                filename=pdf_path.name
            )
            mensaje.attach(adjunto)

        # 5. Conexión SMTP y envío (soporta SSL en puerto 465 o STARTTLS en puerto 587)
        print(f"🔄 Conectando al servidor SMTP ({smtp_server}:{smtp_port}, SSL={use_ssl})...")
        
        if use_ssl:
            with smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=30) as server:
                server.login(auth_user, password)
                server.sendmail(from_email, [destinatario], mensaje.as_string())
        else:
            with smtplib.SMTP(smtp_server, smtp_port, timeout=30) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(auth_user, password)
                server.sendmail(from_email, [destinatario], mensaje.as_string())

        print(f"✅ [EMAIL_SUCCESS] Reporte enviado exitosamente desde {from_email} a: {destinatario}")
        return True

    except Exception as e:
        print(f"❌ [EMAIL_ERROR] Error durante el envío del correo: {e}")
        return False

