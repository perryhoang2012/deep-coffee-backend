from __future__ import annotations

from typing import Optional

from core.config import settings


class VisionService:
    def extract_face_embedding(self, image_bytes: bytes) -> dict:
        try:
            image = self._decode_image(image_bytes)
        except ModuleNotFoundError as exc:
            return {
                "success": False,
                "reason": "missing_dependency",
                "message": f"Missing Python package: {exc.name}",
                "detector_used": None,
                "faces_detected": 0,
            }

        if image is None:
            return {
                "success": False,
                "reason": "invalid_image",
                "detector_used": None,
                "faces_detected": 0,
            }

        detection = self._detect_face(image)
        if not detection["face_crop"] is None:
            embedding = self._build_embedding(detection["face_crop"])
            return {
                "success": True,
                "reason": "face_detected",
                "embedding": embedding,
                "detector_used": detection["detector_used"],
                "faces_detected": detection["faces_detected"],
                "bounding_box": detection["bounding_box"],
            }

        return {
            "success": False,
            "reason": "no_face_detected",
            "detector_used": detection["detector_used"],
            "faces_detected": detection["faces_detected"],
        }

    def _decode_image(self, image_bytes: bytes):
        import cv2
        import numpy as np

        np_buffer = np.frombuffer(image_bytes, dtype=np.uint8)
        return cv2.imdecode(np_buffer, cv2.IMREAD_COLOR)

    def _detect_face(self, image) -> dict:
        yolo_result = self._detect_face_with_yolo(image)
        if yolo_result:
            return yolo_result
        return self._detect_face_with_opencv(image)

    def _detect_face_with_yolo(self, image) -> Optional[dict]:
        if not settings.YOLO_MODEL_PATH:
            return None

        try:
            from ultralytics import YOLO
        except ImportError:
            return None

        try:
            model = YOLO(settings.YOLO_MODEL_PATH)
            results = model.predict(source=image, verbose=False)
        except Exception:
            return None

        if not results:
            return None

        boxes = results[0].boxes
        if boxes is None or len(boxes) == 0:
            return {
                "face_crop": None,
                "detector_used": "yolo",
                "faces_detected": 0,
                "bounding_box": None,
            }

        best_box = max(boxes, key=lambda box: float((box.xyxy[0][2] - box.xyxy[0][0]) * (box.xyxy[0][3] - box.xyxy[0][1])))
        x1, y1, x2, y2 = [int(value) for value in best_box.xyxy[0].tolist()]
        face_crop = image[max(y1, 0):max(y2, 0), max(x1, 0):max(x2, 0)]

        return {
            "face_crop": face_crop if face_crop.size else None,
            "detector_used": "yolo",
            "faces_detected": len(boxes),
            "bounding_box": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
        }

    def _detect_face_with_opencv(self, image) -> dict:
        import cv2

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))

        if len(faces) == 0:
            return {
                "face_crop": None,
                "detector_used": "opencv-haar",
                "faces_detected": 0,
                "bounding_box": None,
            }

        x, y, w, h = max(faces, key=lambda face: face[2] * face[3])
        face_crop = image[y:y + h, x:x + w]
        return {
            "face_crop": face_crop,
            "detector_used": "opencv-haar",
            "faces_detected": len(faces),
            "bounding_box": {"x1": int(x), "y1": int(y), "x2": int(x + w), "y2": int(y + h)},
        }

    def _build_embedding(self, face_crop) -> list[float]:
        import cv2
        import numpy as np

        target_size = settings.FACE_EMBEDDING_SIZE
        gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
        normalized = cv2.resize(gray, (target_size, target_size), interpolation=cv2.INTER_AREA)
        normalized = normalized.astype("float32") / 255.0

        # MVP embedding: downsample face patch into a deterministic feature vector.
        block_size = 8
        embedding = []
        for row in range(0, target_size, block_size):
            for col in range(0, target_size, block_size):
                block = normalized[row:row + block_size, col:col + block_size]
                embedding.append(float(np.mean(block)))

        return embedding
