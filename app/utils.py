from mailjet_rest import Client
from flask import current_app

def send_email(to_email, subject, html_content):
    mailjet = Client(
        auth=(current_app.config['MAILJET_API_KEY'], 
              current_app.config['MAILJET_API_SECRET']),
        version='v3.1'
    )
    data = {
        'Messages': [{
            'From': {
                'Email': current_app.config['MAILJET_SENDER_EMAIL'],
                'Name': current_app.config['MAILJET_SENDER_NAME']
            },
            'To': [{
                'Email': to_email
            }],
            'Subject': subject,
            'HTMLPart': html_content
        }]
    }
    return mailjet.send.create(data=data)