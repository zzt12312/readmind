from __future__ import annotations

import re
import threading
from dataclasses import dataclass, field
from typing import Any

SEMANTIC_VECTOR_DIM = 384


def extract_keywords(text: str) -> list[str]:
    return re.findall(r"[\u4e00-\u9fff]{2,}|[A-Za-z]{3,}", (text or "").lower())


def hash_vectorize(text: str, dimension: int = SEMANTIC_VECTOR_DIM) -> list[float]:
    lowered = (text or "").lower()
    keywords = extract_keywords(lowered)
    compact = re.sub(r"\s+", "", lowered)
    grams = [compact[index : index + 2] for index in range(max(0, len(compact) - 1))]
    features = [*keywords[:48], *grams[:80]]

    if not features:
        return [0.0] * dimension

    vector = [0.0] * dimension
    for feature in features:
        bucket = hash(feature) % dimension
        vector[bucket] += 1.0

    norm = sum(value * value for value in vector) ** 0.5
    if norm == 0:
        return vector

    return [round(value / norm, 6) for value in vector]


@dataclass
class EmbeddingService:
    model_name: str
    batch_size: int = 32
    provider: str = field(default="hash-fallback", init=False)
    status: str = field(default="idle", init=False)
    last_error: str = field(default="", init=False)
    _model: Any = field(default=None, init=False, repr=False)
    _load_attempted: bool = field(default=False, init=False, repr=False)
    _warming: bool = field(default=False, init=False, repr=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False, repr=False)

    def _ensure_model(self) -> None:
        if self._load_attempted and self._model is not None:
            return

        with self._lock:
            if self._load_attempted and self._model is not None:
                return

            self._load_attempted = True
            self.status = "loading"
            self.last_error = ""
            try:
                from sentence_transformers import SentenceTransformer
            except Exception as error:
                self.provider = "hash-fallback"
                self.status = "fallback"
                self.last_error = str(error)
                return

            try:
                # 懒加载真实 embedding 模型。只有在首次需要生成向量时才下载/初始化，
                # 避免开发时每次启动 Flask 都付出额外成本。
                self._model = SentenceTransformer(self.model_name)
                self.provider = "sentence-transformers"
                self.status = "ready"
            except Exception as error:
                self._model = None
                self.provider = "hash-fallback"
                self.status = "fallback"
                self.last_error = str(error)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        self._ensure_model()
        if self._model is None:
            return [hash_vectorize(text) for text in texts]

        embeddings = self._model.encode(
            texts,
            batch_size=self.batch_size,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return [[round(float(value), 6) for value in vector] for vector in embeddings.tolist()]

    def embed_text(self, text: str) -> list[float]:
        return self.embed_texts([text])[0]

    def warmup(self) -> None:
        self.embed_text("embedding warmup")

    def start_warmup(self) -> bool:
        if self._warming or self.status == "ready":
            return False

        def _run() -> None:
            self._warming = True
            try:
                self.warmup()
            finally:
                self._warming = False

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()
        return True
