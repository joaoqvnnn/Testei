import uuid, random
from config import PURINCASH_API_KEY

async def create_pix(user_id: int, value: float) -> dict:
    """
    STUB. Substitua por chamada real à PurinCash quando tiver a API Key.
    Retorna dict com 'ref', 'code' (copia e cola) e 'expires_in'.
    """
    ref = uuid.uuid4().hex[:12]
    # código fake só pra UI funcionar (não pague este código)
    fake = "00020126" + "".join(random.choices("0123456789", k=60))
    return {"ref": ref, "code": fake, "expires_in": 600}
