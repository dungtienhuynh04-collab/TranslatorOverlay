import base64
import time
import cv2
import mss
import numpy as np
import requests
from PyQt6.QtCore import QThread, pyqtSignal

class TranslationService(QThread):
    # Signals to communicate back to the Main UI thread
    translation_result = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    status_update = pyqtSignal(str)

    def __init__(self, api_url, model_name, target_lang, sys_prompt, capture_geom):
        super().__init__()
        self.api_url = api_url.rstrip("/")
        if not self.api_url.endswith("/v1"):
            self.api_url += "/v1"
        self.model_name = model_name
        self.target_lang = target_lang
        self.sys_prompt = sys_prompt
        # capture_geom is a tuple: (x, y, width, height)
        self.capture_geom = capture_geom
        self.is_running = True
        
        # Keep track of previous frame for change detection
        self.prev_frame_gray = None
        self.change_threshold = 3.0 # Percentage of pixels that must change

    def run(self):
        with mss.mss() as sct:
            while self.is_running:
                try:
                    # 1. Grab screen area defined by the capture overlay
                    x, y, w, h = self.capture_geom
                    
                    # Prevent capturing invalid regions
                    if w <= 0 or h <= 0:
                        self.status_update.emit("Capture box is too small.")
                        time.sleep(1)
                        continue
                        
                    monitor = {"top": y, "left": x, "width": w, "height": h}
                    sct_img = sct.grab(monitor)
                    
                    # Convert to numpy array for OpenCV
                    img = np.array(sct_img)
                    
                    # 2. Check for image changes to avoid spamming the LLM
                    gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
                    
                    if self.prev_frame_gray is not None:
                        # Resize if dimensions changed (user resized the window)
                        if self.prev_frame_gray.shape != gray.shape:
                            self.prev_frame_gray = gray
                        
                        else:
                            # Absolute difference between frames
                            diff = cv2.absdiff(self.prev_frame_gray, gray)
                            non_zero_count = np.count_nonzero(diff > 30) # Ignore tiny noise
                            total_pixels = gray.size
                            
                            changed_percent = (non_zero_count / total_pixels) * 100
                            
                            if changed_percent < self.change_threshold:
                                # Image hasn't changed enough, sleep and try again
                                time.sleep(0.5)
                                continue
                    
                    # Update previous frame
                    self.prev_frame_gray = gray.copy()
                    
                    self.status_update.emit("Change detected, translating...")
                    
                    # 3. Convert image to base64
                    # Encode to JPEG to save bandwidth
                    _, buffer = cv2.imencode('.jpg', img, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
                    base64_img = base64.b64encode(buffer).decode('utf-8')
                    
                    # 4. Formulate the dynamically replaced prompt
                    final_prompt = self.sys_prompt.replace("{language}", self.target_lang)
                    
                    # 5. Send to LM Studio Local API (OpenAI Compatible)
                    headers = {
                        "Content-Type": "application/json"
                    }
                    
                    payload = {
                        "model": self.model_name,
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": final_prompt},
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/jpeg;base64,{base64_img}"
                                        }
                                    }
                                ]
                            }
                        ],
                        "temperature": 0.3, # Low temperature for more deterministic translation
                        "max_tokens": 1024
                    }
                    
                    response = requests.post(
                        f"{self.api_url}/chat/completions",
                        headers=headers,
                        json=payload,
                        timeout=15 # Don't hang forever
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if "choices" in data and len(data["choices"]) > 0:
                            result_text = data["choices"][0]["message"]["content"]
                            self.translation_result.emit(result_text)
                            self.status_update.emit("Translation successful.")
                        elif "error" in data:
                            err_data = data["error"]
                            if isinstance(err_data, dict):
                                err_msg = err_data.get("message", str(err_data))
                            else:
                                err_msg = str(err_data)
                            self.error_occurred.emit(f"LM Studio error: {err_msg}")
                        else:
                            resp_str = str(data)
                            self.error_occurred.emit(f"Unexpected response:\n{resp_str[:100]}")
                    else:
                        try:
                            error_msg = response.json().get("error", {}).get("message", response.text)
                        except:
                            error_msg = response.text
                        self.error_occurred.emit(f"API Error ({response.status_code}): {error_msg}")
                        
                except requests.exceptions.RequestException as e:
                    self.error_occurred.emit(f"Connection error with LM Studio:\n{e}")
                    # Sleep longer on connection error
                    time.sleep(2)
                except Exception as e:
                    self.error_occurred.emit(f"Unknown error:\n{e}")
                
                # Sleep a bit between successful loops to prevent locking the thread
                time.sleep(1)

    def update_geometry(self, geom):
        self.capture_geom = geom
        
    def stop(self):
        self.is_running = False
        self.wait()
