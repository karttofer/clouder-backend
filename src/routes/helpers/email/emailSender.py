import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.utils import make_msgid
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
SMTP_PORT = int(os.getenv("SMTP_PORT"))

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
ASSETS_DIR = Path(__file__).resolve().parent / "assets"

env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(["html"])
)

def render_html(template_name: str, **context) -> str:
    ctx = {"year": datetime.now().year, **context}
    template = env.get_template(template_name)
    html = template.render(**ctx)
    html_inlined = transform(html, remove_classes=False, keep_style_tags=True)
    return html_inlined

def html_to_text(html: str) -> str:
    h = html2text.HTML2Text()
    h.ignore_images = True
    h.ignore_links = False
    return h.handle(html)

def _attach_image(message: MIMEMultipart, path: Path, cid_name: str) -> str:
    """
    Adjunta una imagen y devuelve el string 'cid:...' para usar en el HTML.
    """
    with open(path, "rb") as f:
        img = MIMEImage(f.read())
    cid = make_msgid(domain="candhr.local")[1:-1]
    img.add_header("Content-ID", f"<{cid}>")
    img.add_header("Content-Disposition", "inline", filename=path.name)
    message.attach(img)
    return f"cid:{cid}"

def send_email(recipient_email: str, subject: str, template_name: str, **context):
    root = MIMEMultipart("related")
    root["From"] = SENDER_EMAIL
    root["To"] = recipient_email
    root["Subject"] = subject

    alt = MIMEMultipart("alternative")
    root.attach(alt)

    cids = {}
    # TODO: Take a look to the dark theme
    # cids["logo_light_cid"]    = _attach_image(root, ASSETS_DIR / "logo-light.png", "logo_light")
    # cids["logo_dark_cid"]     = _attach_image(root, ASSETS_DIR / "logo-dark.png",  "logo_dark")
    # cids["wordmark_dark_cid"] = _attach_image(root, ASSETS_DIR / "wordmark-dark.png",  "wordmark_dark")

    cids["wordmark_light_cid"]= _attach_image(root, ASSETS_DIR / "wordmark-light.png", "wordmark_light")
    cids["icon_globe_cid"]    = _attach_image(root, ASSETS_DIR / "icon-globe.png", "icon_globe")
    cids["icon_linkedin_cid"] = _attach_image(root, ASSETS_DIR / "icon-linkedin.png", "icon_linkedin")

    # Render HTML con esos CIDs
    html_body = render_html(template_name, subject=subject, **context, **cids)
    text_body = html_to_text(html_body)

    alt.attach(MIMEText(text_body, "plain", "utf-8"))
    alt.attach(MIMEText(html_body, "html", "utf-8"))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_API_KEY)
        server.sendmail(SENDER_EMAIL, recipient_email, root.as_string())

    print(f"Email enviado a {recipient_email}")
