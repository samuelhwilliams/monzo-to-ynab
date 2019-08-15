import base64

from google.cloud import kms


def kms_decrypt(key_resource_name, ciphertext):
    return (
        kms.KeyManagementServiceClient()
        .decrypt(key_resource_name, base64.b64decode(ciphertext))
        .plaintext.decode("ascii")
    )
