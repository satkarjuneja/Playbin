import subprocess
import numpy as np
import threading


#Spectral leakage is the smearing of signal energy across multiple frequencies
# in a Fast Fourier Transform (FFT) analysis.
# It occurs because the Discrete Fourier Transform (DFT) 
# assumes the analyzed signal block is infinitely periodic.
# If a signal's frequency does not align perfectly with the frequency bins, 
# cutting it into a finite block creates artificial discontinuities at the edges,
# which "leak" energy across the entire spectrum.The Hanning (or Hann) window is a standard,
# highly effective mathematical filter used to suppress this leakage.

class Audio_Processing:
    def __init__(self):
        self.sample_rate = 48000
        self.frame_size = 2048
        self.hop_size = 1024
        
        self.window = np.hanning(self.frame_size)
        self.buffer = np.zeros(self.frame_size * 4)
        self.write_index = 0
        self.spectrum = None
        
        self.thread=None
        self.proc=None
        self.bands_output=None
        
        self.bands = [
            (20, 250),      # Bass
            (250, 2000),    # Low-Mid
            (2000, 6000),   # High-Mid
            (6000, 16000)]   # Treble
        
    def analyzer_start_parsec(self): #connects to PulseAudio/PipeWire as a recording client and writes raw PCM(Pulse Code Modulation) to stdout
        self.proc = subprocess.Popen(
        ["parec",
        "--device=@DEFAULT_MONITOR@",
        "--format=float32le",
        "--rate=48000",
        "--channels=1"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,)
    
    def read_pcm(self): #Pulse Code Modulation 
        while(True):
            raw=self.proc.stdout.read(1024*4)
            if not raw:
                break
            samples = np.frombuffer(raw, dtype=np.float32)
            
            # 1. accumulate
            self.buffer = np.roll(self.buffer, -self.hop_size)
            self.buffer[-self.hop_size:] = samples

            # 2. window + FFT
            frame = self.buffer[-self.frame_size:] * self.window
            self.spectrum = np.abs(np.fft.rfft(frame))

            # 3. bin into bands
            freqs = np.fft.rfftfreq(self.frame_size, d=1.0 / self.sample_rate)
            band_values = []
            for low, high in self.bands:
                mask = (freqs >= low) & (freqs < high)
                band_values.append(float(np.mean(self.spectrum[mask])))
            self.bands_output = band_values
                
    def start_analyzer_thread(self):
        self.analyzer_start_parsec()
        self.thread = threading.Thread(target=self.read_pcm, daemon=True) 
        self.thread.start() 
    
    def stop_analyzer_thread(self):
        if self.proc:
            self.proc.terminate()
        self.proc = None        
        
    