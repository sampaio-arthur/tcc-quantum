from __future__ import annotations

import math

import numpy as np
from scipy.stats import spearmanr
from sklearn.metrics import ndcg_score, precision_score, recall_score

from domain.entities import EvaluationResult


class SklearnMetricsAdapter:
    def evaluate_query(
        self,
        *,
        query_id: str | None,
        query_text: str,
        pipeline: str,
        retrieved_doc_ids: list[str],
        retrieved_scores: list[float],
        relevant_doc_ids: list[str],
        k: int,
    ) -> EvaluationResult:
        relevant_set = set(relevant_doc_ids)
        topk_retrieved = retrieved_doc_ids[:k]
        universe = list(dict.fromkeys(topk_retrieved + list(relevant_set)))
        y_true_cls = [1 if doc_id in relevant_set else 0 for doc_id in universe]
        y_pred_cls = [1 if doc_id in topk_retrieved else 0 for doc_id in universe]

        precision = float(precision_score(y_true_cls, y_pred_cls, zero_division=0))
        recall = float(recall_score(y_true_cls, y_pred_cls, zero_division=0))

        y_true = np.array([[1 if doc_id in relevant_set else 0 for doc_id in topk_retrieved]], dtype=float)
        y_score = np.array([retrieved_scores[:k] or [0.0] * k], dtype=float)
        if y_true.shape[1] < k:
            pad = k - y_true.shape[1]
            y_true = np.pad(y_true, ((0, 0), (0, pad)))
            y_score = np.pad(y_score, ((0, 0), (0, pad)))
        ndcg = float(ndcg_score(y_true, y_score, k=k))

        spearman = self._spearman_topk(retrieved_doc_ids[:k], relevant_doc_ids[:k], k)
        return EvaluationResult(
            query_id=query_id,
            query_text=query_text,
            pipeline=pipeline,
            precision_at_k=precision,
            recall_at_k=recall,
            ndcg_at_k=ndcg,
            spearman=spearman,
            top_k_doc_ids=retrieved_doc_ids[:k],
        )

    def _spearman_topk(self, retrieved: list[str], reference: list[str], k: int) -> float:
        union_ids = list(dict.fromkeys(retrieved + reference))
        if len(union_ids) < 2:
            return 1.0
        default_rank = k + 1
        r_rank = {doc_id: idx + 1 for idx, doc_id in enumerate(retrieved)}
        g_rank = {doc_id: idx + 1 for idx, doc_id in enumerate(reference)}
        a = [r_rank.get(doc_id, default_rank) for doc_id in union_ids]
        b = [g_rank.get(doc_id, default_rank) for doc_id in union_ids]
        corr = spearmanr(a, b).correlation
        if corr is None or math.isnan(corr):
            return 0.0
        return float(corr)
