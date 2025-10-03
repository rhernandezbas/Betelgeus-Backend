import subprocess
import base64
from datetime import datetime, timedelta, timezone
from lxml import etree
from zeep import Client
from zeep.transports import Transport
import ssl
import requests
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager

# ============================
# CONFIGURACIÓN
# ============================
SERVICE = "wsmtxca"
CERT = "cert.crt"     # Certificado de aplicación (producción)
KEY = "private.key"   # Clave privada asociada
TRA_PATH = "TRA.xml"
CMS_PATH = "TRA.cms"
TA_PATH = "TA.xml"

WSAA_WSDL = "https://wsaa.afip.gov.ar/ws/services/LoginCms?WSDL"
WSMTXCA_WSDL = "https://serviciosjava.afip.gob.ar/wsmtxca/services/MTXCAService?wsdl"

CUIT = 27962218739  # ⚠️ tu CUIT real
PTO_VTA = 11        # Punto de venta en producción
TIPO_CBTE = 6       # 6 = Factura B

# ============================
# 1) Crear TRA.xml
# ============================
def crear_tra(service=SERVICE, out_path=TRA_PATH):
    now = datetime.now(timezone(timedelta(hours=-3)))  # GMT-3
    gen_time = (now - timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%S%z")
    exp_time = (now + timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%S%z")

    # corregir offset -0300 → -03:00
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
# 2) Firmar con OpenSSL (CMS)
# ============================
def firmar_tra(tra_path=TRA_PATH, cms_path=CMS_PATH, cert=CERT, key=KEY):
    cmd = [
        "openssl", "smime", "-sign",
        "-in", tra_path,
        "-out", cms_path,
        "-signer", cert,
        "-inkey", key,
        "-outform", "DER",  # AFIP acepta DER
        "-nodetach"
    ]
    subprocess.run(cmd, check=True)
    print(f"[OK] TRA firmado en {cms_path}")
    return cms_path

# ============================
# 3) Llamar al WSAA
# ============================
def login_cms(cms_path=CMS_PATH, wsdl=WSAA_WSDL):
    client = Client(wsdl=wsdl)
    cms_bytes = open(cms_path, "rb").read()
    cms_b64 = base64.b64encode(cms_bytes).decode("utf-8")
    response = client.service.loginCms(cms_b64)
    print("[OK] LoginCms ejecutado")
    return response

# ============================
# 4) Guardar TA.xml
# ============================
def guardar_ta(response_xml, out_path=TA_PATH):
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(response_xml)
    print(f"[OK] TA guardado en {out_path}")

# ============================
# 5) Obtener token y sign
# ============================
def obtener_token_sign(ta_path=TA_PATH):
    tree = etree.parse(ta_path)
    token = tree.findtext(".//token")
    sign = tree.findtext(".//sign")
    return token, sign

# ============================
# Adapter para usar SSLContext custom
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

# ============================
# Helper: Cliente con SSL relajado
# ============================
def get_client(wsdl_url):
    ctx = ssl.create_default_context()
    ctx.set_ciphers('DEFAULT:@SECLEVEL=1')  # ⚠️ bajar seguridad para AFIP

    session = requests.Session()
    session.mount("https://", SSLContextAdapter(ctx))

    transport = Transport(session=session)
    return Client(wsdl=wsdl_url, transport=transport)

# ============================
# 6) Consultar último comprobante autorizado
# ============================
def consultar_ultimo_comprobante(token, sign, pto_vta, tipo_cbte):
    client = get_client(WSMTXCA_WSDL)
    auth = {"token": token, "sign": sign, "cuitRepresentada": CUIT}

    res = client.service.consultarUltimoComprobanteAutorizado(
        authRequest=auth,
        consultaUltimoComprobanteAutorizadoRequest={
            "codigoTipoComprobante": tipo_cbte,
            "numeroPuntoVenta": pto_vta
        }
    )

    ultimo = getattr(res, "numeroComprobante", None)
    if ultimo is None:
        print("[INFO] No hay comprobantes previos, se empezará en 1")
        return 0

    print(f"[OK] Último comprobante autorizado: {ultimo}")
    return ultimo

# ============================
# 7) Consultar comprobante específico
# ============================
def consultar_comprobante(token, sign, pto_vta, tipo_cbte, nro_cbte):
    client = get_client(WSMTXCA_WSDL)
    auth = {"token": token, "sign": sign, "cuitRepresentada": CUIT}

    res = client.service.consultarComprobante(
        authRequest=auth,
        consultaComprobanteRequest={
            "codigoTipoComprobante": tipo_cbte,
            "numeroPuntoVenta": pto_vta,
            "numeroComprobante": nro_cbte
        }
    )

    print("Respuesta consultarComprobante:", res)
    return res

# ============================
# 8) Flujo: Emitir y consultar comprobante
# ============================
def flujo_factura_y_consulta():
    token, sign = obtener_token_sign()
    client = get_client(WSMTXCA_WSDL)

    hoy = datetime.now().strftime("%Y-%m-%d")

    # Paso 1: consultar último nro de comprobante
    ultimo = consultar_ultimo_comprobante(token, sign, pto_vta=PTO_VTA, tipo_cbte=TIPO_CBTE)
    numero_comprobante = ultimo + 1

    item = {
        "unidadesMtx": 0,  # normalmente 0 si no usás tablas MTX
        "codigoMtx": "",
        "codigo": "P001",  # código interno del producto
        "descripcion": "Producto de prueba",
        "cantidad": 1,
        "codigoUnidadMedida": 7,  # 7 = unidad
        "precioUnitario": 1000.00,
        "importeBonificacion": 0.00,
        "codigoCondicionIVA": 5,  # 5 = 21% IVA
        "importeIVA": 210.00,
        "importeItem": 1210.00
    }

    # Paso 2: armar comprobante
    comprobanteCAERequest = {
        "codigoTipoComprobante": 6,  # Factura B
        "numeroPuntoVenta": 11,
        "numeroComprobante": numero_comprobante,
        "fechaEmision": hoy,
        "codigoConcepto": 1,  # 1 = Productos
        "codigoTipoDocumento": 96,  # DNI
        "numeroDocumento": 12345678,
        "condicionIVAReceptor": 5,  # Responsable inscripto / consumidor final según corresponda
        "importeGravado": 1000.00,
        "importeNoGravado": 0.00,
        "importeExento": 0.00,
        "importeSubtotal": 1000.00,
        "importeOtrosTributos": 0.00,
        "importeTotal": 1210.00,
        "codigoMoneda": "PES",
        "cotizacionMoneda": 1,
        "fechaVencimientoPago": hoy,
        "arrayItems": {"item": [item]},
        "arraySubtotalesIVA": {
            "subtotalIVA": [
                {
                    "codigo": 5,  # 21%
                    "importe": 210.00
                }
            ]
        }
    }

    auth = {"token": token, "sign": sign, "cuitRepresentada": CUIT}

    print(f"[INFO] Emitiendo factura en PV {PTO_VTA} número {numero_comprobante}...")
    res = client.service.autorizarComprobante(authRequest=auth, comprobanteCAERequest=comprobanteCAERequest)

    print("Respuesta WSMTXCA:", res)

    if hasattr(res, "resultado") and res.resultado == "A":
        print(f"✅ Factura autorizada. CAE: {res.cae} (vence {res.fechaVencimientoCAE})")
        # Paso 3: consultar comprobante recién emitido
        consultar_comprobante(token, sign, pto_vta=PTO_VTA, tipo_cbte=TIPO_CBTE, nro_cbte=numero_comprobante)
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
    flujo_factura_y_consulta()


