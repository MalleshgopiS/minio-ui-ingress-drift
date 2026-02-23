import subprocess
import json

def run(cmd: str):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout.strip(), result.stderr.strip()

def check_ingress():
    # Fetching values as individual JSON components to avoid whitespace issues
    cmd = 'kubectl get ingress bleater-ui -n bleater -o json'
    rc, out, err = run(cmd)
    
    if rc != 0:
        return False, f"Failed to get ingress: {err}"
    
    data = json.loads(out)
    try:
        service = data['spec']['rules'][0]['http']['paths'][0]['backend']['service']['name']
        port = data['spec']['rules'][0]['http']['paths'][0]['backend']['service']['port']['number']
        secret = data['spec']['tls'][0]['secretName']
        
        if service == "bleater-minio" and port == 9001 and secret == "bleater-minio-tls":
            return True, "Ingress correctly configured"
        return False, f"Configuration mismatch: {service}, {port}, {secret}"
    except (KeyError, IndexError) as e:
        return False, f"Unexpected structure: {str(e)}"

def grade():
    success, message = check_ingress()
    return {"score": 1.0 if success else 0.0, "message": message}

if __name__ == "__main__":
    print(json.dumps(grade(), indent=2))