import subprocess
import base64
import json
import qrcode
from datetime import datetime, timedelta, timezone
from lxml import etree
from zeep import Client
from zeep.transports import Transport
import ssl
import requests
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# ============================
# CONFIGURACIÓN
# ============================
SERVICE = "wsfe"
CERT = "cert.crt"
KEY = "private.key"
TRA_PATH = "TRA.xml"
CMS_PATH = "TRA.cms"
TA_PATH = "TA.xml"

WSAA_WSDL = "https://wsaa.afip.gov.ar/ws/services/LoginCms?WSDL"
WSFE_WSDL = "https://servicios1.afip.gov.ar/wsfev1/service.asmx?WSDL"

CUIT = 27962218739  # tu CUIT
PTO_VTA = 11        # Punto de venta
TIPO_CBTE = 11      # Factura C


# ============================
# 1) Crear TRA.xml
# ============================
def crear_tra(service=SERVICE, out_path=TRA_PATH):
    now = datetime.now(timezone(timedelta(hours=-3)))
    gen_time = (now - timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%S%z")
    exp_time = (now + timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%S%z")

    gen_time = gen_time[:-2] + ":" + gen_time[-2:]
    exp_time = exp_time[:-2] + ":" + exp_time[-2:]

    root = etree.Element("loginTicketRequest", version="1.0")
    header = etree.SubElement(root, "header")
    etree.SubElement(header, "uniqueId").text = str(int(now.timestamp()))
    etree.SubElement(header, "generationTime").text = gen_time
    etree.SubElement(header, "expirationTime").text = exp_time
    etree.SubElement(root, "service").text = service

    xml_str = etree.tostring(root, pretty_print=True, xml_declaration=True, encoding="UTF-8")
    with open(out_path, "wb") as f:
        f.write(xml_str)

    print(f"[OK] TRA generado en {out_path}")
    return out_path


# ============================
# 2) Firmar con OpenSSL
# ============================
def firmar_tra(tra_path=TRA_PATH, cms_path=CMS_PATH, cert=CERT, key=KEY):
    cmd = [
        "openssl", "smime", "-sign",
        "-in", tra_path,
        "-out", cms_path,
        "-signer", cert,
        "-inkey", key,
        "-outform", "DER",
        "-nodetach"
    ]
    subprocess.run(cmd, check=True)
    print(f"[OK] TRA firmado en {cms_path}")
    return cms_path


# ============================
# 3) Login CMS
# ============================
def login_cms(cms_path=CMS_PATH, wsdl=WSAA_WSDL):
    client = Client(wsdl=wsdl)
    cms_bytes = open(cms_path, "rb").read()
    cms_b64 = base64.b64encode(cms_bytes).decode("utf-8")
    response = client.service.loginCms(cms_b64)
    print("[OK] LoginCms ejecutado")
    return response


# ============================
# 4) Guardar TA
# ============================
def guardar_ta(response_xml, out_path=TA_PATH):
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(response_xml)
    print(f"[OK] TA guardado en {out_path}")


# ============================
# 5) Token y Sign
# ============================
def obtener_token_sign(ta_path=TA_PATH):
    tree = etree.parse(ta_path)
    token = tree.findtext(".//token")
    sign = tree.findtext(".//sign")
    return token, sign


# ============================
# SSL Context Adapter
# ============================
class SSLContextAdapter(HTTPAdapter):
    def __init__(self, ssl_context=None, **kwargs):
        self.ssl_context = ssl_context
        super().__init__(**kwargs)

    def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
        self.poolmanager = PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_context=self.ssl_context,
            **pool_kwargs
        )


def get_client(wsdl_url):
    ctx = ssl.create_default_context()
    ctx.set_ciphers('DEFAULT:@SECLEVEL=1')
    session = requests.Session()
    session.mount("https://", SSLContextAdapter(ctx))
    transport = Transport(session=session)
    return Client(wsdl=wsdl_url, transport=transport)


# ============================
# 6) Generar QR AFIP
# ============================
def generar_qr_afip(cuit, pto_vta, cbte_tipo, nro_cbte, cae, cae_vto, importe, fecha, moneda="PES"):
    data = {
        "ver": 1,
        "fecha": fecha,
        "cuit": cuit,
        "ptoVta": pto_vta,
        "tipoCmp": cbte_tipo,
        "nroCmp": nro_cbte,
        "importe": importe,
        "moneda": moneda,
        "ctz": 1,
        "tipoDocRec": 96,
        "nroDocRec": 12345678,
        "tipoCodAut": "E",
        "codAut": int(cae)
    }

    url_qr = "https://www.afip.gob.ar/fe/qr/?p=" + \
        base64.urlsafe_b64encode(json.dumps(data).encode()).decode()

    img = qrcode.make(url_qr)
    img.save("qr_afip.png")
    print("[OK] QR generado en qr_afip.png")
    return "qr_afip.png"


# ============================
# 7) Generar PDF
# ============================
def generar_pdf_factura(cuit, razon_social, cliente, cae, cae_vto, qr_path, salida="factura.pdf"):
    c = canvas.Canvas(salida, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, f"Factura C")
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 70, f"Razón Social: {razon_social}")
    c.drawString(50, height - 85, f"CUIT: {cuit}")
    c.drawString(50, height - 100, f"Cliente: {cliente}")

    c.drawString(50, height - 140, f"CAE: {cae}")
    c.drawString(50, height - 160, f"Vencimiento CAE: {cae_vto}")

    c.drawImage(qr_path, width - 200, height - 250, 150, 150)

    c.setFont("Helvetica-Oblique", 8)
    c.drawString(50, 50, "Factura generada electrónicamente a través de AFIP WSFEv1")

    c.save()
    print(f"[OK] Factura generada en {salida}")


# ============================
# 8) Flujo completo: emitir y PDF
# ============================
def flujo_factura_y_pdf():
    token, sign = obtener_token_sign()
    client = get_client(WSFE_WSDL)

    hoy = datetime.now().strftime("%Y%m%d")

    # Consultar último comprobante
    ultimo = client.service.FECompUltimoAutorizado(
        Auth={"Token": token, "Sign": sign, "Cuit": CUIT},
        PtoVta=PTO_VTA,
        CbteTipo=TIPO_CBTE
    ).CbteNro

    nro_cbte = ultimo + 1
    print(f"[INFO] Próximo comprobante: {nro_cbte}")

    # Armar factura
    feCAEReq = {
        "FeCabReq": {
            "CantReg": 1,
            "PtoVta": PTO_VTA,
            "CbteTipo": TIPO_CBTE
        },
        "FeDetReq": {
            "FECAEDetRequest": [{
                "Concepto": 1,  # 1=Productos
                "DocTipo": 96,  # 96 = DNI
                "DocNro": 12345678,
                "CbteDesde": nro_cbte,
                "CbteHasta": nro_cbte,
                "CbteFch": hoy,

                # Importes obligatorios (todos deben estar)
                "ImpTotal": 1210.00,
                "ImpTotConc": 0.00,  # ⚠️ ESTE FALTABA
                "ImpNeto": 1210.00,
                "ImpOpEx": 0.00,  # operaciones exentas
                "ImpTrib": 0.00,
                "ImpIVA": 0.00,

                # Moneda
                "MonId": "PES",
                "MonCotiz": 1
            }]
        }
    }

    # Autorizar
    res = client.service.FECAESolicitar(
        Auth={"Token": token, "Sign": sign, "Cuit": CUIT},
        FeCAEReq=feCAEReq
    )

    print("Respuesta WSFEv1:", res)

    if res.FeDetResp and res.FeDetResp.FECAEDetResponse[0].Resultado == "A":
        detalle = res.FeDetResp.FECAEDetResponse[0]
        cae = detalle.CAE
        cae_vto = detalle.CAEFchVto
        print(f"✅ Factura autorizada. CAE: {cae}, vence {cae_vto}")

        qr = generar_qr_afip(CUIT, PTO_VTA, TIPO_CBTE, nro_cbte, cae, cae_vto, 1210.00, datetime.now().strftime("%Y-%m-%d"))
        generar_pdf_factura(CUIT, "Mi Empresa SRL", "Cliente Prueba", cae, cae_vto, qr)

    else:
        print("❌ Error al autorizar comprobante:", res)


# ============================
# MAIN
# ============================
if __name__ == "__main__":
    crear_tra()
    firmar_tra()
    ta_xml = login_cms()
    guardar_ta(ta_xml)
    flujo_factura_y_pdf()
