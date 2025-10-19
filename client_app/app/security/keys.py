from Crypto.PublicKey import RSA
import os

#rutas donde se guarda la llave privada y publica
PRIVATE_KEY_PATH = "./certs/private.pem"
PUBLIC_KEY_PATH = "./certs/public.pem"

def generate_keys():
    """Genera un nuevo par de claves RSA si no existen."""
    if not os.path.exists("certs"): #crea la carpeta certs si no existe
        os.makedirs("certs")

    #Verifica si las claves RSA ya existen. Si ya existen, no hace nada (no las regenera). Si no existen, las crea desde cero.
    if not os.path.exists(PRIVATE_KEY_PATH) or not os.path.exists(PUBLIC_KEY_PATH):
        key = RSA.generate(2048)
        with open(PRIVATE_KEY_PATH, "wb") as f:
            f.write(key.export_key())
        with open(PUBLIC_KEY_PATH, "wb") as f:
            f.write(key.publickey().export_key())
        print("RSA keys generated.")
