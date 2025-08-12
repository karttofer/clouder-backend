import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader, select_autoescape
from premailer import transform
import html2text
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path

load_dotenv()
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_API_KEY = os.getenv("SENDER_API_KEY")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"

env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(["html"])
)
def render_html(template_name: str, **context) -> str:
    ctx = {
        "year": datetime.now().year,
        **context
    }
    template = env.get_template(template_name)
    print(template, 'pedr')
    html = template.render(**ctx)
    html_inlined = transform(html, remove_classes=False, keep_style_tags=True)
    return html_inlined


def html_to_text(html: str) -> str:
    h = html2text.HTML2Text()
    h.ignore_images = True
    h.ignore_links = False
    return h.handle(html)


def send_email(recipient_email: str, subject: str, template_name: str, **context):
    html_body = render_html(template_name, subject=subject, **context)
    text_body = html_to_text(html_body)

    message = MIMEMultipart("alternative")
    message["From"] = SENDER_EMAIL
    message["To"] = recipient_email
    message["Subject"] = subject

    message.attach(MIMEText(text_body, "plain"))
    message.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_API_KEY)
        server.sendmail(SENDER_EMAIL, recipient_email, message.as_string())

    print(f"Email enviado a {recipient_email}")