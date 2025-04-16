from pydantic import BaseModel, Field

class PaymentResponse(BaseModel):
    """
    Schema for Paystack payment initialization response
    """
    authorization_url: str = Field(
        ...,
        example="https://checkout.paystack.com/0peioxfhpn",
        description="Paystack checkout URL for payment processing"
    )
    reference: str = Field(
        ...,
        example="7PVGX8MEK85t",
        description="Unique transaction reference ID"
    )
    access_code: str = Field(
        ...,
        example="d7gofp6y",
        description="Access code for transaction verification"
    )
