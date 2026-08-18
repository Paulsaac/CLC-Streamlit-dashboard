import os
import smtplib
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# Importación condicional de streamlit para compatibilidad con st.secrets
try:
    import streamlit as st
except ImportError:
    st = None


def obtener_credenciales():
    """
    Obtiene las credenciales del remitente SMTP de forma segura.
    Prioriza st.secrets (entorno Streamlit) y realiza fallback a variables de entorno (os.environ).
    """
    user = None
    password = None
    server = "smtp.gmail.com"
    port = 587

    # 1. Intentar cargar desde st.secrets si está disponible
    if st is not None:
        try:
            # Soporta formato [smtp] o [email] en secrets.toml
            smtp_config = st.secrets.get("smtp", {}) or st.secrets.get("email", {})
            user = smtp_config.get("user") or smtp_config.get("email_user")
            password = smtp_config.get("password") or smtp_config.get("email_password")
            server = smtp_config.get("server", server)
            port = int(smtp_config.get("port", port))
        except Exception:
            pass

    # 2. Fallback a variables de entorno del sistema
    if not user:
        user = os.environ.get("EMAIL_USER") or os.environ.get("SMTP_USER")
    if not password:
        password = os.environ.get("EMAIL_PASSWORD") or os.environ.get("SMTP_PASSWORD")
    if os.environ.get("EMAIL_SERVER") or os.environ.get("SMTP_SERVER"):
        server = os.environ.get("EMAIL_SERVER") or os.environ.get("SMTP_SERVER")
    if os.environ.get("EMAIL_PORT") or os.environ.get("SMTP_PORT"):
        try:
            port = int(os.environ.get("EMAIL_PORT") or os.environ.get("SMTP_PORT"))
        except ValueError:
            pass

    return user, password, server, port


def enviar_reporte_email(
    ruta_pdf: str,
    destinatario: str,
    asunto: str = "Reporte Semanal CLC - Mercado Libre & Performance"
) -> bool:
    """
    Envía un reporte PDF adjunto por correo electrónico a través del servidor SMTP de Gmail.

    Parámetros:
    -----------
    ruta_pdf : str
        Ruta local del archivo PDF a adjuntar (ej. 'reportes/reporte_semana.pdf').
    destinatario : str
        Correo electrónico del destinatario (ej. 'cliente@empresa.com').
    asunto : str, opcional
        Asunto del correo electrónico. Por defecto: "Reporte Semanal CLC - Mercado Libre & Performance".

    Retorna:
    --------
    bool
        True si el correo fue enviado exitosamente, False si ocurrió algún error.
    """
    # 1. Obtener y validar credenciales de seguridad
    remitente, password, smtp_server, smtp_port = obtener_credenciales()

    if not remitente or not password:
        print("❌ [EMAIL_ERROR] Credenciales SMTP no encontradas. Configura EMAIL_USER y EMAIL_PASSWORD en variables de entorno o en .streamlit/secrets.toml.")
        return False

    # 2. Validar existencia del archivo PDF
    pdf_path = Path(ruta_pdf)
    if not pdf_path.exists() or not pdf_path.is_file():
        print(f"❌ [EMAIL_ERROR] El archivo PDF no existe en la ruta especificada: '{ruta_pdf}'")
        return False

    try:
        # 3. Construcción del mensaje MIME
        mensaje = MIMEMultipart()
        mensaje["From"] = f"CLC Reportes <{remitente}>"
        mensaje["To"] = destinatario
        mensaje["Subject"] = asunto

        # 4. Cuerpo del mensaje en formato HTML corporativo
        cuerpo_html = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
        </head>
        <body style="margin: 0; padding: 20px; font-family: 'Segoe UI', Arial, sans-serif; color: #222222; background-color: #F8FAF9;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #FFFFFF; border: 1px solid #E0E4E8; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 6px rgba(0,0,0,0.04);">
                
                <!-- Encabezado con Verde Corporativo CLC -->
                <div style="background-color: #124E3F; padding: 22px 26px; color: #FFFFFF;">
                    <h2 style="margin: 0; font-size: 1.3rem; font-weight: 700; letter-spacing: 0.5px;">CLC Mercado Libre</h2>
                    <p style="margin: 4px 0 0 0; font-size: 0.85rem; color: #A5D6A7;">Reporte Ejecutivo de Rendimiento & Performance</p>
                </div>

                <!-- Contenido Principal -->
                <div style="padding: 26px;">
                    <p style="font-size: 1rem; margin-top: 0;">Estimado/a,</p>
                    
                    <p style="font-size: 0.95rem; line-height: 1.5; color: #333333;">
                        Te compartimos el <strong>Reporte Semanal de Rendimiento</strong> correspondiente al último período consolidado de Mercado Libre.
                    </p>
                    
                    <!-- Tarjeta informativa de archivo adjunto -->
                    <div style="background-color: #F1F6F4; border-left: 4px solid #25D366; padding: 14px 18px; margin: 20px 0; border-radius: 4px;">
                        <p style="margin: 0; font-size: 0.9rem; color: #124E3F;">
                            📎 <strong>Documento adjunto:</strong> <span style="color: #222222; font-weight: 600;">{pdf_path.name}</span>
                        </p>
                        <p style="margin: 6px 0 0 0; font-size: 0.8rem; color: #666666;">
                            El archivo incluye KPIs clave, mix de canales (Ads vs. Orgánico), evolución diaria y ranking de artículos más vendidos.
                        </p>
                    </div>

                    <p style="font-size: 0.9rem; line-height: 1.5; color: #555555;">
                        Quedamos a tu entera disposición ante cualquier consulta o análisis adicional requerido.
                    </p>

                    <p style="font-size: 0.95rem; margin-bottom: 0; color: #222222;">
                        Saludos cordiales,<br>
                        <strong>Equipo de Operaciones & Analítica - CLC</strong>
                    </p>
                </div>

                <!-- Pie de página -->
                <div style="background-color: #F8FAF9; padding: 14px 26px; border-top: 1px solid #EAEAEA; text-align: center;">
                    <p style="margin: 0; font-size: 0.75rem; color: #888888;">
                        Este es un mensaje generado automáticamente por el sistema de reportes de CLC. Por favor no responder a este remitente.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        mensaje.attach(MIMEText(cuerpo_html, "html", "utf-8"))

        # 5. Adjuntar el documento PDF
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
            server.starttls()  # Inicializar cifrado TLS
            server.ehlo()
            server.login(remitente, password)
            server.sendmail(remitente, [destinatario], mensaje.as_string())

        print(f"✅ [EMAIL_SUCCESS] Reporte enviado exitosamente a: {destinatario}")
        return True

    except smtplib.SMTPAuthenticationError as auth_err:
        print(f"❌ [EMAIL_ERROR] Error de autenticación SMTP: Verifica tu usuario/correo y tu Contraseña de Aplicación. Detalle: {auth_err}")
        return False
    except smtplib.SMTPException as smtp_err:
        print(f"❌ [EMAIL_ERROR] Error en el protocolo SMTP: {smtp_err}")
        return False
    except Exception as e:
        print(f"❌ [EMAIL_ERROR] Ocurrió un error inesperado al enviar el correo: {e}")
        return False


if __name__ == "__main__":
    # Test básico de ejecución individual
    print("Módulo email_service cargado correctamente.")
