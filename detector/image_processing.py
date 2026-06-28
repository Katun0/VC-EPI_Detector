import cv2
import numpy as np

class ImageProcessor:

    def __init__(self, clahe_clip=2.0, clahe_grid=8):

        # CLAHE (equalização adaptativa) reutilizável - mais barato criar uma vez
        self.clahe = cv2.createCLAHE(
            clipLimit=clahe_clip,
            tileGridSize=(clahe_grid, clahe_grid)
        )

    # ------------------------------------------------------------------ #
    # Técnicas individuais
    # ------------------------------------------------------------------ #
    @staticmethod
    def to_grayscale(frame):
        """Converte BGR para escala de cinza."""
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    @staticmethod
    def equalize_hist(frame):
        """Equalização de histograma global (em escala de cinza)."""
        gray = ImageProcessor.to_grayscale(frame)
        return cv2.equalizeHist(gray)

    @staticmethod
    def gaussian_blur(frame, ksize=5):
        """Filtro de suavização Gaussiano. ksize deve ser ímpar."""
        if ksize % 2 == 0:
            ksize += 1
        return cv2.GaussianBlur(frame, (ksize, ksize), 0)

    @staticmethod
    def edges(frame, low=100, high=200):
        """Detecção de bordas com Canny."""
        gray = ImageProcessor.to_grayscale(frame)
        return cv2.Canny(gray, low, high)

    @staticmethod
    def morphology(mask, op="open", ksize=5, iterations=1):
        """Operações morfológicas sobre uma máscara binária."""
        kernel = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE,
            (ksize, ksize)
        )

        ops = {
            "open": cv2.MORPH_OPEN,
            "close": cv2.MORPH_CLOSE,
            "erode": cv2.MORPH_ERODE,
            "dilate": cv2.MORPH_DILATE,
        }

        return cv2.morphologyEx(
            mask,
            ops.get(op, cv2.MORPH_OPEN),
            kernel,
            iterations=iterations
        )

    # ------------------------------------------------------------------ #
    # Pré-processamento aplicado antes da inferência
    # ------------------------------------------------------------------ #
    def enhance(self, frame):
        """
        Melhora o contraste preservando as cores aplicando CLAHE apenas
        no canal de luminância (YUV). Útil em cenas escuras antes de detectar.
        """
        yuv = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV)
        yuv[:, :, 0] = self.clahe.apply(yuv[:, :, 0])
        return cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)

    # ------------------------------------------------------------------ #
    # Visualização das etapas (para demonstrar o critério)
    # ------------------------------------------------------------------ #
    def debug_grid(self, frame, cell_width=320):
        """
        Monta um mosaico 2x3 com as etapas de processamento, para
        demonstrar visualmente as técnicas aplicadas.
        """
        gray = self.to_grayscale(frame)
        equalized = self.equalize_hist(frame)
        blur = self.gaussian_blur(frame, 7)
        edge = self.edges(frame)
        enhanced = self.enhance(frame)

        # converte os que são 1 canal para 3 canais para empilhar
        gray3 = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        eq3 = cv2.cvtColor(equalized, cv2.COLOR_GRAY2BGR)
        edge3 = cv2.cvtColor(edge, cv2.COLOR_GRAY2BGR)

        cells = [
            (frame, "Original"),
            (gray3, "Escala de Cinza"),
            (eq3, "Equalizacao Hist."),
            (blur, "Filtro Gaussiano"),
            (edge3, "Bordas (Canny)"),
            (enhanced, "Enhance (CLAHE)"),
        ]

        resized = [self._label(self._resize(img, cell_width), name)
                   for img, name in cells]

        top = np.hstack(resized[0:3])
        bottom = np.hstack(resized[3:6])

        return np.vstack([top, bottom])

    @staticmethod
    def _resize(img, width):
        h, w = img.shape[:2]
        height = int(h * (width / w))
        return cv2.resize(img, (width, height))

    @staticmethod
    def _label(img, text):
        out = img.copy()
        cv2.rectangle(out, (0, 0), (out.shape[1], 26), (0, 0, 0), -1)
        cv2.putText(
            out,
            text,
            (8, 18),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (56, 189, 248),
            1,
            cv2.LINE_AA
        )
        return out
