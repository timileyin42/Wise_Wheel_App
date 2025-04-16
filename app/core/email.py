import httpx
from fastapi import BackgroundTasks
from app.core.config import settings
from typing import Dict, Any

async def send_mailjet_email(
    to_email: str,
    subject: str,
    template_name: str,
    context: Dict[str, Any],
    background_tasks: BackgroundTasks
):
    """Send transactional emails via Mailjet"""
    try:
        # In production: Render Jinja template with context
        html_content = f"""
        <h1>{subject}</h1>
        <pre>{context}</pre>
        """
        
        # Use background task for non-blocking operation
        async def _send_email():
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.mailjet.com/v3.1/send",
                    auth=(settings.MAILJET_API_KEY, settings.MAILJET_API_SECRET),
                    json={
                        "Messages": [{
                            "From": {
                                "Email": settings.MAILJET_SENDER_EMAIL,
                                "Name": settings.MAILJET_SENDER_NAME
                            },
                            "To": [{"Email": to_email}],
                            "Subject": subject,
                            "HTMLPart": html_content
                        }]
                    }
                )
                response.raise_for_status()
        
        background_tasks.add_task(_send_email)
        
    except Exception as e:
        # Implement proper error logging
        print(f"Mailjet error: {str(e)}")
