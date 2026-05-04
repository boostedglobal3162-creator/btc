import os
import shutil
import certifi

def apply_system_fixes():
    """Applies SSL and DNS workarounds for robust connectivity."""
    try:
        cert_path = certifi.where()
        public_cert_dir = r"C:\Users\Public\TradeKing_Certs"
        os.makedirs(public_cert_dir, exist_ok=True)
        local_cert = os.path.join(public_cert_dir, "cacert.pem")
        if not os.path.exists(local_cert):
            shutil.copy(cert_path, local_cert)
        
        os.environ['SSL_CERT_FILE'] = local_cert
        os.environ['AIODNS_RESOLVER'] = 'threading'
        print(f"[System Fix] SSL and DNS workarounds applied.")
    except Exception as e:
        print(f"[System Fix] Failed to apply: {e}")

def format_timestamp(ts):
    """Utility to format timestamps consistently."""
    return ts.strftime("%Y-%m-%d %H:%M:%S")
