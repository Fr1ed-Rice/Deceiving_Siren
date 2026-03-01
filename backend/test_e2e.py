"""Quick end-to-end test of encode/decode API."""
import requests
import tempfile
import wave
import numpy as np
import os
import shutil

td = tempfile.mkdtemp()
print(f"Temp dir: {td}")

# Create test WAV (3 seconds of silence at 44100Hz)
wav_path = os.path.join(td, "carrier.wav")
samples = np.zeros(44100 * 3, dtype=np.int16)
with wave.open(wav_path, "wb") as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(44100)
    w.writeframes(samples.tobytes())
print(f"Created carrier WAV: {os.path.getsize(wav_path)} bytes")

# Create test payload
payload_path = os.path.join(td, "secret.txt")
with open(payload_path, "w") as f:
    f.write("Hello from Deceiving Siren!")
print(f"Created payload: {os.path.getsize(payload_path)} bytes")

# Send to encode API
with open(wav_path, "rb") as carrier, open(payload_path, "rb") as payload:
    resp = requests.post(
        "http://127.0.0.1:5000/api/encode",
        files={
            "carrier": ("carrier.wav", carrier, "audio/wav"),
            "payload": ("secret.txt", payload, "text/plain"),
        },
        data={"output_format": "wav"},
    )

print(f"Encode status: {resp.status_code}")
if resp.status_code == 200:
    out = os.path.join(td, "stego.wav")
    with open(out, "wb") as f:
        f.write(resp.content)
    print(f"Stego output: {os.path.getsize(out)} bytes")

    # Decode
    with open(out, "rb") as stego:
        resp2 = requests.post(
            "http://127.0.0.1:5000/api/decode",
            files={"audio": ("stego.wav", stego, "audio/wav")},
        )
    print(f"Decode status: {resp2.status_code}")
    if resp2.status_code == 200:
        print(f"Decoded: {resp2.content}")
    else:
        print(f"Decode error: {resp2.text}")
else:
    print(f"Encode error: {resp.text}")

shutil.rmtree(td)
print("Done!")
