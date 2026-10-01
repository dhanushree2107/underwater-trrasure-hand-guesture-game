"""
Underwater Sound Manager
Provides procedural synthesized audio for all game actions, ambient sounds,
and feedback cues. Safe fallback guarantees zero crashes if audio devices are unavailable.
"""

import io
import math
import struct
import wave
from typing import Dict, Optional
import pygame

class SoundManager:
    """Manages audio playback and synthesizes rich sound effects procedurally."""

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.enabled = True
        self.volume = 0.8
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.ambient_channel: Optional[pygame.mixer.Channel] = None
        
        self._init_mixer()
        if self.enabled:
            self._generate_all_sounds()

    def _init_mixer(self) -> None:
        """Safely initializes the pygame mixer with fallback."""
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.pre_init(frequency=self.sample_rate, size=-16, channels=2, buffer=512)
                pygame.mixer.init()
            pygame.mixer.set_num_channels(16)
            self.ambient_channel = pygame.mixer.Channel(0)
        except Exception as e:
            print(f"[SoundManager] Warning: Audio mixer could not initialize ({e}). Audio disabled.")
            self.enabled = False

    def _create_wav_bytes(self, samples: list, channels: int = 1) -> bytes:
        """Encodes raw integer samples into an in-memory WAV byte buffer."""
        byte_io = io.BytesIO()
        with wave.open(byte_io, 'wb') as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(self.sample_rate)
            raw_data = struct.pack(f"<{len(samples)}h", *samples)
            wf.writeframes(raw_data)
        return byte_io.getvalue()

    def _synth_tone(self, freq: float, duration: float, envelope: str = 'exp', volume: float = 0.5) -> list:
        """Synthesizes a simple sine wave tone with the given envelope."""
        n_samples = int(self.sample_rate * duration)
        samples = []
        for i in range(n_samples):
            t = i / self.sample_rate
            val = math.sin(2.0 * math.pi * freq * t)
            
            # Envelopes
            if envelope == 'exp':
                amp = math.exp(-3.5 * (i / n_samples))
            elif envelope == 'linear_decay':
                amp = 1.0 - (i / n_samples)
            elif envelope == 'attack_decay':
                attack = min(1.0, i / (0.1 * n_samples))
                amp = attack * (1.0 - (i / n_samples))
            elif envelope == 'bell':
                amp = math.sin(math.pi * (i / n_samples))
            else:
                amp = 1.0
                
            sample_val = int(val * amp * volume * 32767)
            sample_val = max(-32767, min(32767, sample_val))
            samples.append(sample_val)
        return samples

    def _synth_sweep(self, start_freq: float, end_freq: float, duration: float, volume: float = 0.5) -> list:
        """Synthesizes a frequency modulated sweep tone."""
        n_samples = int(self.sample_rate * duration)
        samples = []
        phase = 0.0
        for i in range(n_samples):
            alpha = i / n_samples
            freq = start_freq + (end_freq - start_freq) * alpha
            phase += 2.0 * math.pi * freq / self.sample_rate
            val = math.sin(phase)
            amp = math.exp(-2.5 * alpha)
            sample_val = int(val * amp * volume * 32767)
            samples.append(max(-32767, min(32767, sample_val)))
        return samples

    def _synth_chord(self, freqs: list, duration: float, volume: float = 0.4) -> list:
        """Synthesizes a harmonious multi-frequency chord."""
        n_samples = int(self.sample_rate * duration)
        samples = []
        for i in range(n_samples):
            t = i / self.sample_rate
            val = sum(math.sin(2.0 * math.pi * f * t) for f in freqs) / len(freqs)
            amp = math.exp(-3.0 * (i / n_samples))
            sample_val = int(val * amp * volume * 32767)
            samples.append(max(-32767, min(32767, sample_val)))
        return samples

    def _synth_noise_burst(self, duration: float, volume: float = 0.4, decay: float = 4.0) -> list:
        """Synthesizes an organic filtered noise burst (e.g. bubble or water rush)."""
        import random
        n_samples = int(self.sample_rate * duration)
        samples = []
        prev = 0.0
        for i in range(n_samples):
            alpha = i / n_samples
            raw = (random.random() * 2.0 - 1.0)
            # Low pass filter
            filtered = prev * 0.75 + raw * 0.25
            prev = filtered
            amp = math.exp(-decay * alpha)
            sample_val = int(filtered * amp * volume * 32767)
            samples.append(max(-32767, min(32767, sample_val)))
        return samples

    def _generate_all_sounds(self) -> None:
        """Pre-generates all synthesized audio cues and creates pygame Sounds."""
        try:
            # 1. Bubble pop
            b_sweep = self._synth_sweep(400, 950, 0.12, volume=0.35)
            self._load_sound('bubble', b_sweep)

            # 2. Coin / Treasure collection (sparkling crystal chime)
            c1 = self._synth_chord([987.77, 1318.51, 1975.53], 0.45, volume=0.5)
            self._load_sound('treasure', c1)

            # 3. Rare Artifact (majestic dual chime)
            rare = self._synth_chord([587.33, 880.00, 1174.66, 1760.00], 0.7, volume=0.6)
            self._load_sound('rare_treasure', rare)

            # 4. Sonar ping (deep sinusoidal resonance with slow fade)
            sonar = self._synth_tone(880.0, 1.2, envelope='exp', volume=0.55)
            self._load_sound('sonar', sonar)

            # 5. Fake Treasure Buzz (discordant buzz)
            fake_samples = []
            n_samples = int(self.sample_rate * 0.4)
            for i in range(n_samples):
                t = i / self.sample_rate
                # Sawtooth / square wave dissonance
                val = 0.5 * math.sin(2.0 * math.pi * 140 * t) + 0.5 * math.sin(2.0 * math.pi * 185 * t)
                if ((int(t * 28)) % 2) == 0:
                    val *= 0.2
                amp = math.exp(-2.0 * (i / n_samples))
                fake_samples.append(max(-32767, min(32767, int(val * amp * 0.55 * 32767))))
            self._load_sound('fake_warning', fake_samples)

            # 6. Sea Mine Trap Explosion (low frequency rumble + noise)
            trap_samples = []
            n_samples = int(self.sample_rate * 0.8)
            import random
            prev = 0.0
            for i in range(n_samples):
                t = i / self.sample_rate
                noise = random.random() * 2.0 - 1.0
                filtered_noise = prev * 0.85 + noise * 0.15
                prev = filtered_noise
                sub = math.sin(2.0 * math.pi * 55.0 * t * (1.0 - t * 0.4))
                val = 0.6 * sub + 0.4 * filtered_noise
                amp = math.exp(-3.5 * (i / n_samples))
                trap_samples.append(max(-32767, min(32767, int(val * amp * 0.8 * 32767))))
            self._load_sound('trap', trap_samples)

            # 7. Water Current whoosh
            whoosh = self._synth_noise_burst(1.2, volume=0.45, decay=2.0)
            self._load_sound('current', whoosh)

            # 8. Shark Warning (heavy pulse)
            shark_warn = self._synth_sweep(90, 75, 0.6, volume=0.7)
            self._load_sound('shark_warning', shark_warn)

            # 9. Level Complete fanfare (C5 -> E5 -> G5 -> C6 rapid arpeggio)
            fanfare_samples = []
            note_dur = 0.12
            fanfare_samples.extend(self._synth_tone(523.25, note_dur, 'attack_decay', 0.5))
            fanfare_samples.extend(self._synth_tone(659.25, note_dur, 'attack_decay', 0.5))
            fanfare_samples.extend(self._synth_tone(783.99, note_dur, 'attack_decay', 0.5))
            fanfare_samples.extend(self._synth_tone(1046.50, 0.6, 'exp', 0.6))
            self._load_sound('level_complete', fanfare_samples)

            # 10. Game Over (sad descending motif)
            gover_samples = []
            gover_samples.extend(self._synth_tone(440.0, 0.25, 'linear_decay', 0.45))
            gover_samples.extend(self._synth_tone(370.0, 0.25, 'linear_decay', 0.45))
            gover_samples.extend(self._synth_tone(311.13, 0.7, 'exp', 0.5))
            self._load_sound('game_over', gover_samples)

            # 11. Button Click & Hover
            self._load_sound('click', self._synth_tone(1200.0, 0.06, 'exp', 0.35))
            self._load_sound('hover', self._synth_tone(650.0, 0.04, 'exp', 0.2))

            # 12. Whirlpool vortex suction
            whirl = self._synth_sweep(180, 70, 0.9, volume=0.55)
            self._load_sound('whirlpool', whirl)

            # 13. Electric Jellyfish zap
            zap = self._synth_sweep(1400, 220, 0.18, volume=0.45)
            self._load_sound('jellyfish_zap', zap)

            # 14. Ancient puzzle success & seal unlocked
            puzzle_chime = self._synth_chord([523.25, 659.25, 783.99, 1046.50, 1318.51], 0.85, volume=0.6)
            self._load_sound('puzzle_success', puzzle_chime)
            seal_unlocked = self._synth_chord([440.0, 554.37, 659.25, 880.0], 1.2, volume=0.7)
            self._load_sound('ancient_seal', seal_unlocked)

            # 15. Heavy treasure pickup & drop
            heavy_thud = self._synth_sweep(120, 45, 0.35, volume=0.65)
            self._load_sound('heavy_drop', heavy_thud)

        except Exception as e:
            print(f"[SoundManager] Warning during sound synthesis: {e}")

    def _load_sound(self, name: str, samples: list) -> None:
        """Converts sample list into WAV bytes and stores as pygame.mixer.Sound."""
        wav_data = self._create_wav_bytes(samples)
        sound = pygame.mixer.Sound(file=io.BytesIO(wav_data))
        sound.set_volume(self.volume)
        self.sounds[name] = sound

    def play(self, sound_name: str, volume_mult: float = 1.0) -> None:
        """Plays a named sound effect safely."""
        if not self.enabled:
            return
        sound = self.sounds.get(sound_name)
        if sound:
            try:
                sound.set_volume(max(0.0, min(1.0, self.volume * volume_mult)))
                sound.play()
            except Exception as e:
                print(f"[SoundManager] Play error on '{sound_name}': {e}")

    def set_volume(self, volume: float) -> None:
        """Sets the global master volume (0.0 to 1.0)."""
        self.volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.volume)

    def toggle_mute(self) -> bool:
        """Toggles audio on/off and returns new state."""
        self.enabled = not self.enabled
        return self.enabled
