import uuid
import aiohttp
import asyncio
from config import MERCADO_PAGO_ACCESS_TOKEN

BASE_URL = "https://api.mercadopago.com/v1/payments"

async def create_pix(user_id: int, value: float, description: str = "Recarga Bellamy Store") -> dict:
    """
    Cria uma cobrança PIX no Mercado Pago.
    Retorna dict com 'ref' (ID do pagamento), 'code' (copia e cola) e 'expires_in'.
    """
    if not MERCADO_PAGO_ACCESS_TOKEN:
        raise Exception("Token do Mercado Pago não configurado.")

    headers = {
        "Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "X-Idempotency-Key": str(uuid.uuid4())
    }

    payload = {
        "transaction_amount": float(f"{value:.2f}"),
        "description": description,
        "payment_method_id": "pix",
        "payer": {
            "email": f"user{user_id}@bellamystore.com"
        }
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(BASE_URL, json=payload, headers=headers) as resp:
            data = await resp.json()
            if resp.status not in (200, 201):
                raise Exception(f"Erro Mercado Pago: {data}")

            payment_id = str(data["id"])
            qr_code = data["point_of_interaction"]["transaction_data"]["qr_code"]
            # O Mercado Pago expira o PIX em 30 minutos por padrão, mas usamos 10 min no bot.
            return {"ref": payment_id, "code": qr_code, "expires_in": 600}


async def check_payment_status(payment_id: str) -> str:
    """
    Consulta o status de um pagamento.
    Retorna 'approved', 'pending', 'rejected', etc.
    """
    if not MERCADO_PAGO_ACCESS_TOKEN:
        return "pending"

    headers = {"Authorization": f"Bearer {MERCADO_PAGO_ACCESS_TOKEN}"}
    url = f"{BASE_URL}/{payment_id}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            if resp.status != 200:
                return "pending"
            data = await resp.json()
            return data.get("status", "pending")
