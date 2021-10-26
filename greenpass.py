import sys
import glob
import json
import zlib
import cbor2
import os
from PIL import Image
from pyzbar import pyzbar
from datetime import datetime
from urllib.request import urlopen
from cose.messages import CoseMessage
from cose.headers import KID, Algorithm
from base64 import b64decode, b64encode
from base45 import b45decode

from cose.algorithms import Es256
from cose.keys.curves import P256
from cose.algorithms import Es256, EdDSA, Ps256
from cose.headers import KID, Algorithm
from cose.keys import CoseKey
from cose.keys.keyparam import KpAlg, EC2KpX, EC2KpY, EC2KpCurve, RSAKpE, RSAKpN
from cose.keys.keyparam import KpKty
from cose.keys.keytype import KtyEC2, KtyRSA
from cose.messages import CoseMessage
from cryptography import x509
from cryptography.utils import int_to_bytes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePublicKey
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

sch = open('dataset/schema-combined.json')
glb_schema = json.load(sch)

kids = {}

valuesets = {}

def add_kid(kid_b64, key_b64):
        kid = b64decode(kid_b64)
        asn1data = b64decode(key_b64)

        pub = serialization.load_der_public_key(asn1data)
        if (isinstance(pub, RSAPublicKey)):
              kids[kid_b64] = CoseKey.from_dict(
               {
                    KpKty: KtyRSA,
                    KpAlg: Ps256,  # RSSASSA-PSS-with-SHA-256-and-MFG1
                    RSAKpE: int_to_bytes(pub.public_numbers().e),
                    RSAKpN: int_to_bytes(pub.public_numbers().n)
               })
        elif (isinstance(pub, EllipticCurvePublicKey)):
              kids[kid_b64] = CoseKey.from_dict(
               {
                    KpKty: KtyEC2,
                    EC2KpCurve: P256,  # Ought o be pk.curve - but the two libs clash
                    KpAlg: Es256,  # ecdsa-with-SHA256
                    EC2KpX: pub.public_numbers().x.to_bytes(32, byteorder="big"),
                    EC2KpY: pub.public_numbers().y.to_bytes(32, byteorder="big")
               })
        else:
              print(f"Skipping unexpected/unknown key type (keyid={kid_b64}, {pub.__class__.__name__}).",  file=sys.stderr)

def load_pub_keys():
    #keys = urlopen('https://verifier-api.coronacheck.nl/v4/verifier/public_keys')
    keys = open('dataset/public_keys.json')
    pkg = json.load(keys)
    payload = b64decode(pkg['payload'])
    trustlist = json.loads(payload)
    eulist = trustlist['eu_keys']
    for kid_b64 in eulist:
        add_kid(kid_b64,eulist[kid_b64][0]['subjectPk'])

def load_valuesets():
    for name in ["co", "ma", "mp", "tg", "tr", "tt", "vp"]:
        filename = "dataset/{}.json".format(name)
        valuesets[name] = json.load(open(filename))["valueSetValues"]

load_valuesets()

def annotate(data, schema=glb_schema['properties'], level=0):
    res = ""
    for key, value in data.items():
        description = schema[key].get('title') or schema[key].get('description') or key
        description, _, _ = description.partition(' - ')
        if type(value) is dict:
            res = res + (('  '*level) + ' ' + description) + "\n"
            _, _, sch_ref = schema[key]['$ref'].rpartition('/')
            res = res + annotate(value, glb_schema['$defs'][sch_ref]['properties'], level+1) + "\n"
        elif type(value) is list:
            res = res + (('  '*level) + ' ' + description) + "\n"
            _, _, sch_ref = schema[key]['items']['$ref'].rpartition('/')
            for v in value:
                res = res + annotate(v, glb_schema['$defs'][sch_ref]['properties'], level+1) + "\n"
        else: # value is scalar

            if key in valuesets and value in valuesets[key]:
                value = valuesets[key][value]["display"] + " ({})".format(value)

            res = res +(('  '*level) + ' ' + description + ': ' + str(value)) + "\n"
    return res


def read_qr(pil):
    try:
        return pyzbar.decode(pil)[0].data
    except:
        return None

def decode_certificate(encoded):
    version = encoded[0:4]
    if version != b'HC1:':
        return None
    compressed = encoded[4:]
    return zlib.decompress(b45decode(compressed))

def signature_valid(cose):
    load_pub_keys()
    given_kid = None
    if KID in cose.phdr.keys():
       given_kid = cose.phdr[KID]
    else:
       given_kid = cose.uhdr[KID]

    given_kid_b64 = b64encode(given_kid).decode('ASCII')


    if not given_kid_b64 in kids:
        return False
    else:
        key  = kids[given_kid_b64]

        cose.key = key
        if not cose.verify_signature():
            return False
        else:
            return True

def load_certificate(cose_document):
    cert = cbor2.loads(cose_document.payload)
    data = {}
    try:
        data['issuer'] = valuesets["co"][cert[1]]["display"]
    except:
        data['issuer'] = '⚠️ Unknown '+str(cert[1])
    data['expiry'] = cert[4]
    data['generated_ad'] = cert[6]
    data['certificate'] = cert[-260][1]

    return data

def certinfo(content):
    try:
        cose_document = decode_certificate(content)
        cose = CoseMessage.decode(cose_document)
        is_valid = signature_valid(cose)
        certificate = load_certificate(cose)

        return (certificate, is_valid)
    except:
        return (None, None)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} QR_CODE.png", file=sys.stderr)
        print(f"Usage: {sys.argv[0]} 'HC1:.....'", file=sys.stderr)
        sys.exit(1)
    else:
        if os.path.exists(sys.argv[1]):
            infile = sys.argv[1]
            qr_pil = Image.open(infile)
            content = read_qr(qr_pil)
        else:
            infile = None
            content = sys.argv[1].encode('UTF-8')

    certificate, is_valid = certinfo(content)
    print(annotate(certificate['certificate']))
