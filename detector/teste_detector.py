"""
Teste de fumaça do pipeline de detecção.

Roda o detector em um frame sintético (sem precisar de webcam ou arquivo)
e valida que a inferência, as métricas e a verificação de conformidade
funcionam de ponta a ponta.

Uso:
    python -m detector.teste_detector
"""

import numpy as np

from detector import EPIDetector, MetricsTracker, ComplianceChecker, ImageProcessor


def main():
    # frame sintético (640x480, ruído) só para exercitar o pipeline
    frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

    detector = EPIDetector(confidence=0.25)
    checker = ComplianceChecker()
    metrics = MetricsTracker()
    processor = ImageProcessor()

    annotated, detections, inference_ms, compliance = detector.predict(
        frame, checker=checker
    )
    metrics.update(inference_ms, detections, compliance)

    # exercita o processamento de imagem
    grid = processor.debug_grid(frame)

    print(f"[OK] Inferência: {inference_ms:.1f} ms")
    print(f"[OK] Detecções: {len(detections)}")
    print(f"[OK] Conformidade: {compliance}")
    print(f"[OK] Frame anotado: {annotated.shape}")
    print(f"[OK] Mosaico de processamento: {grid.shape}")
    print(f"[OK] Snapshot de métricas: {metrics.snapshot()}")
    print("[OK] Teste de fumaça concluído com sucesso.")


if __name__ == "__main__":
    main()
