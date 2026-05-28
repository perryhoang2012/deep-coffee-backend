from __future__ import annotations

from typing import Optional

from core.config import settings


class VisionService:
    _insightface_app = None

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
            try:
                embedding = self._build_embedding(image, detection["bounding_box"])
            except ModuleNotFoundError as exc:
                return {
                    "success": False,
                    "reason": "missing_dependency",
                    "message": f"Missing Python package: {exc.name}",
                    "detector_used": detection["detector_used"],
                    "faces_detected": detection["faces_detected"],
                    "bounding_box": detection["bounding_box"],
                }
            except RuntimeError as exc:
                return {
                    "success": False,
                    "reason": "face_embedding_failed",
                    "message": str(exc),
                    "detector_used": f"{detection['detector_used']}+insightface",
                    "faces_detected": detection["faces_detected"],
                    "bounding_box": detection["bounding_box"],
                }

            return {
                "success": True,
                "reason": "face_detected",
                "embedding": embedding,
                "embedding_model": "insightface",
                "detector_used": f"{detection['detector_used']}+insightface",
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

    def _build_embedding(self, image, bounding_box: Optional[dict] = None) -> list[float]:
        import numpy as np

        app = self._get_insightface_app()
        faces = app.get(image, max_num=0)
        if not faces:
            raise RuntimeError("InsightFace could not extract an embedding from the detected face.")

        face = self._select_insightface_match(faces, bounding_box)
        embedding = getattr(face, "normed_embedding", None)
        if embedding is None:
            embedding = getattr(face, "embedding", None)
        if embedding is None:
            raise RuntimeError("InsightFace returned a face without an embedding.")

        embedding_array = np.asarray(embedding, dtype="float32")
        norm = float(np.linalg.norm(embedding_array))
        if norm == 0:
            raise RuntimeError("InsightFace returned an empty embedding.")

        embedding_array = embedding_array / norm
        return [float(value) for value in embedding_array.tolist()]

    def _get_insightface_app(self):
        if VisionService._insightface_app is not None:
            return VisionService._insightface_app

        from insightface.app import FaceAnalysis

        app = FaceAnalysis(
            name=settings.INSIGHTFACE_MODEL_NAME,
            root=settings.INSIGHTFACE_MODEL_ROOT,
            allowed_modules=["detection", "recognition"],
            providers=["CPUExecutionProvider"],
        )
        app.prepare(
            ctx_id=-1,
            det_size=(settings.INSIGHTFACE_DET_SIZE, settings.INSIGHTFACE_DET_SIZE),
        )
        VisionService._insightface_app = app
        return app

    def _face_area(self, bbox) -> float:
        if bbox is None or len(bbox) < 4:
            return 0.0

        x1, y1, x2, y2 = [float(value) for value in bbox[:4]]
        return max(0.0, x2 - x1) * max(0.0, y2 - y1)

    def _select_insightface_match(self, faces, bounding_box: Optional[dict]):
        if not bounding_box:
            return max(
                faces,
                key=lambda detected_face: self._face_area(getattr(detected_face, "bbox", None)),
            )

        target_center_x = (float(bounding_box["x1"]) + float(bounding_box["x2"])) / 2
        target_center_y = (float(bounding_box["y1"]) + float(bounding_box["y2"])) / 2

        def distance_to_detected_face(detected_face) -> float:
            bbox = getattr(detected_face, "bbox", None)
            if bbox is None or len(bbox) < 4:
                return float("inf")

            face_center_x = (float(bbox[0]) + float(bbox[2])) / 2
            face_center_y = (float(bbox[1]) + float(bbox[3])) / 2
            return (face_center_x - target_center_x) ** 2 + (face_center_y - target_center_y) ** 2

        return min(faces, key=distance_to_detected_face)
