"""
Métricas de desempenho do sistema.

Acompanha indicadores em tempo real do pipeline de detecção: FPS, tempo de
inferência, quantidade de detecções por classe, número de pessoas e alertas
de não conformidade.

A classe é thread-safe porque o stream de vídeo (generate_frames) e o
endpoint /metrics são executados em threads diferentes pelo servidor Flask.

Atende ao critério de avaliação "Análise de desempenho".
"""

import threading
import time
from collections import deque


class MetricsTracker:

    def __init__(self, window=30):

        self._lock = threading.Lock()
        self._window = window

        # janelas deslizantes para médias móveis
        self._frame_times = deque(maxlen=window)   # timestamps dos frames
        self._inference_times = deque(maxlen=window)  # ms por frame

        self._start_time = time.time()
        self.reset()

    def reset(self):
        with self._lock:
            self._frame_times.clear()
            self._inference_times.clear()
            self._start_time = time.time()

            self.total_frames = 0
            self.total_detections = 0
            self.class_counts = {}
            self.people = 0
            self.compliant = 0
            self.non_compliant = 0
            self.alerts = 0

    def update(self, inference_ms, detections, compliance=None):
        """
        Registra um frame processado.

        inference_ms : tempo da inferência do modelo, em milissegundos
        detections   : lista de detecções (dicts com 'class')
        compliance   : resultado opcional do ComplianceChecker
        """
        now = time.time()

        with self._lock:
            self._frame_times.append(now)
            self._inference_times.append(inference_ms)

            self.total_frames += 1
            self.total_detections += len(detections)

            # contagem por classe (acumulada da janela atual de frame)
            counts = {}
            for det in detections:
                cls = det["class"]
                counts[cls] = counts.get(cls, 0) + 1
            self.class_counts = counts

            if compliance is not None:
                self.people = compliance.get("people", 0)
                self.compliant = compliance.get("compliant", 0)
                self.non_compliant = compliance.get("non_compliant", 0)
                self.alerts = compliance.get("non_compliant", 0)
            else:
                self.people = counts.get("person", 0)

    def _fps(self):
        """FPS pela média móvel dos timestamps na janela."""
        if len(self._frame_times) < 2:
            return 0.0
        span = self._frame_times[-1] - self._frame_times[0]
        if span <= 0:
            return 0.0
        return (len(self._frame_times) - 1) / span

    def _avg_inference(self):
        if not self._inference_times:
            return 0.0
        return sum(self._inference_times) / len(self._inference_times)

    def snapshot(self):
        """Retorna um dict serializável com o estado atual das métricas."""
        with self._lock:
            return {
                "fps": round(self._fps(), 1),
                "inference_ms": round(self._avg_inference(), 1),
                "total_frames": self.total_frames,
                "total_detections": self.total_detections,
                "class_counts": dict(self.class_counts),
                "people": self.people,
                "compliant": self.compliant,
                "non_compliant": self.non_compliant,
                "alerts": self.alerts,
                "uptime_s": round(time.time() - self._start_time, 1),
            }
