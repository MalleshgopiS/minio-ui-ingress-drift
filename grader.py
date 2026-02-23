import subprocess
import json

def run(cmd: str):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout.strip(), result.stderr.strip()

def check_ingress():
    # Fetch full JSON to ensure reliable parsing
    cmd = "kubectl get ingress bleater-ui -n bleater -o json"
    rc, out, err = run(cmd)
    if rc != 0:
        return False, f"Failed to get ingress: {err}"

    try:
        data = json.loads(out)
        spec = data.get('spec', {})
        # Extract fields
        service = spec['rules'][0]['http']['paths'][0]['backend']['service']['name']
        port = spec['rules'][0]['http']['paths'][0]['backend']['service']['port']['number']
        secret = spec['tls'][0]['secretName']

        if service == "bleater-minio" and port == 9001 and secret == "bleater-minio-tls":
            return True, "Success"
        return False, f"Values mismatch: {service}, {port}, {secret}"
    except (KeyError, IndexError):
        return False, "Ingress structure is missing required fields"

def grade():
    success, message = check_ingress()
    return {"score": 1.0 if success else 0.0, "message": message}

if __name__ == "__main__":
    print(json.dumps(grade()))