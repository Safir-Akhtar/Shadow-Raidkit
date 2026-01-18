# core/mic_broadcast.py - Shadow Tools live mic broadcast to all connected alts in VC
import threading
import time
import pyaudio
from .config import MIC_BROADCAST_ACTIVE, MIC_DEVICE_INDEX, VOICE_CLIENTS

def mic_broadcast_thread():
    p = pyaudio.PyAudio()
    stream = None
    try:
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=48000,
            input=True,
            frames_per_buffer=960,
            input_device_index=MIC_DEVICE_INDEX
        )
        print(f"[Shadow Tools] Mic broadcast thread started (device index: {MIC_DEVICE_INDEX})")
        while True:
            if not MIC_BROADCAST_ACTIVE:
                time.sleep(0.05)
                continue
            try:
                data = stream.read(960, exception_on_overflow=False)
                sent_count = 0
                for vc in list(VOICE_CLIENTS.values()):
                    if vc and vc.is_connected():
                        try:
                            vc.send_audio_packet(data, encode=True)
                            sent_count += 1
                        except:
                            pass
                if sent_count > 0:
                    print(f"[Shadow Mic] Sent audio to {sent_count} alts")
            except Exception as e:
                print(f"[Shadow Mic] Broadcast error: {e}")
                time.sleep(0.5)
    except Exception as e:
        print(f"[Shadow Mic] Failed to initialize mic stream: {e}")
    finally:
        if stream:
            stream.stop_stream()
            stream.close()
        p.terminate()
        print("[Shadow Tools] Mic broadcast thread stopped")

def start_mic_thread():
    threading.Thread(target=mic_broadcast_thread, daemon=True).start()