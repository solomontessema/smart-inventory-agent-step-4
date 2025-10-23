import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from langchain_community.chat_models import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from config import OPENAI_API_KEY, AGENT_NAME, AGENT_EMAIL_ADDRESS, AGENT_EMAIL_PASSWORD, BOSS_NAME, BOSS_EMAIL_ADDRESS
 
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

llm = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=OPENAI_API_KEY)


def format_email_body(raw_data: str) -> str:
    """
    Uses LLM to convert raw inventory or supplier data into a natural-language email body.
    """
    prompt = PromptTemplate(
        input_variables=["data","AGENT_NAME", "BOSS_NAME"],
        template="""
You are an inventory assistant. Your name is {AGENT_NAME}. use that name in signature. Format the email into a professional, natural-language email body to sent to me the boss. my name is {BOSS_NAME}.

Data:
{data}

Email:
"""
    )
    return llm.predict(prompt.format(data=raw_data, AGENT_NAME=AGENT_NAME, BOSS_NAME=BOSS_NAME))


def send_email(to_address, subject, body, to_eattachment_path=None):

    if not AGENT_EMAIL_ADDRESS or not AGENT_EMAIL_PASSWORD:
        raise ValueError("Missing EMAIL_ADDRESS or EMAIL_PASSWORD in environment.")

    # Create the email message
    msg = MIMEMultipart()
    msg["From"] = AGENT_EMAIL_ADDRESS
    msg["To"] = to_address
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    # Send the email

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(AGENT_EMAIL_ADDRESS, AGENT_EMAIL_PASSWORD)
        server.send_message(msg)
        print("Email sent successfully.")

def send_email_tool(input: str, use_llm_formatting: bool = True) -> str:
    """
    Expected input format:
    subject || body
    If multiple '||' are present, only the first separates subject from body.
    """
    parts = input.split("||", 1)
    subject = parts[0].strip()
    raw_body = parts[1].strip() if len(parts) > 1 else ""

    body = format_email_body(raw_body) if use_llm_formatting else raw_body
    try:
        send_email(
            to_address="solomon.tessema@ionnova.com",
            subject=subject,
            body=body
        )
        return "Email sent successfully."
    except Exception as e:
        return f"Failed to send email: {str(e)}"

    