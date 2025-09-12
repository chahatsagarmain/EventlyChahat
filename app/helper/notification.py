# import requests

# def send_mailgun_email(to_email: str, subject: str, text: str, from_email: str = "you@yourdomain.com"):
#     url = f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages"
    
#     response = requests.post(
#         url,
#         auth=("api", MAILGUN_API_KEY),
#         data={
#             "from": f"App Mailer <{from_email}>",
#             "to": [to_email],
#             "subject": subject,
#             "text": text,
#         },
#     )

#     if response.status_code == 200:
#         print("✅ Email sent successfully")
#     else:
#         print(f"❌ Failed: {response.status_code} {response.text}")

def send_main():
    print("mail triggered")