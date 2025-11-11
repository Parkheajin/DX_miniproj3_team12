# -*- coding: utf-8 -*-
from __future__ import annotations
import os, json
from typing import Dict, Any, List
import numpy as np

from student.common.schemas import Day5Plan
from .embeddings import Embeddings
from .store import FaissStore

def _idx_paths(index_dir: str):
    return (
        os.path.join(index_dir, "faiss.index"),
        os.path.join(index_dir, "docs.jsonl"),
    )

def _load_store(plan: Day5Plan, emb: Embeddings) -> FaissStore:
    index_path, docs_path = _idx_paths(plan.index_dir)
    if not (os.path.exists(index_path) and os.path.exists(docs_path)):
        raise FileNotFoundError(f"FAISS 인덱스가 없습니다. 먼저 ingest를 실행하세요: {plan.index_dir}")
    store = FaissStore.load(index_path, docs_path)
    # 차원 체크
    test_dim = emb.encode(["__dim_check__"]).shape[1]
    if store.dim != test_dim:
        raise ValueError(f"임베딩 차원이 인덱스와 다릅니다. (index={store.dim}, embedder={test_dim})")
    return store

def _gate(contexts: List[Dict[str, Any]], plan: Day5Plan) -> Dict[str, Any]:
    if not contexts:
        return {"status":"insufficient","top_score":0.0,"mean_topk":0.0}
    top_score = float(contexts[0]["score"])
    mean_topk = float(np.mean([c["score"] for c in contexts[:plan.top_k]]))
    if top_score >= plan.min_score and mean_topk >= plan.min_mean_topk:
        return {"status":"enough","top_score":top_score,"mean_topk":mean_topk}
    return {"status":"insufficient","top_score":top_score,"mean_topk":mean_topk}

def _draft_answer(query: str, contexts: List[Dict[str, Any]], plan: Day5Plan) -> str:
    """공모전 추천 초안 생성"""
    if not contexts:
        return ""
    
    # 공모전 정보 추출 및 요약
    buf, budget = [], plan.max_context
    
    # 상위 공모전 간단 요약
    top_contests = []
    for i, c in enumerate(contexts[:3], 1):  # 상위 3개만
        chunk = c.get("chunk", c.get("text", "")).strip()
        
        # 공모전명 추출 시도
        import re
        title_match = re.search(r'\[공모전명\]:\s*(.+?)(?=\n\[|$)', chunk, re.DOTALL)
        title = title_match.group(1).strip() if title_match else f"공모전 #{i}"
        
        score = c.get("score", 0)
        top_contests.append(f"{i}. {title} (매칭도: {score*100:.1f}%)")
        
        budget -= len(title)
        if budget <= 0:
            break
    
    summary = f"'{query}' 검색 결과 {len(contexts)}개 공모전을 찾았습니다.\n\n"
    summary += "추천 공모전:\n" + "\n".join(top_contests)
    
    return summary

class Day5Agent:  # Day2Agent → Day5Agent
    def __init__(self, plan_defaults: Day5Plan = Day5Plan()):
        self.plan_defaults = plan_defaults

    def handle(self, query: str, plan: Day5Plan = None) -> Dict[str, Any]:
        plan = plan or self.plan_defaults
        emb = Embeddings(model=plan.embedding_model)

        store = _load_store(plan, emb)
        qv = emb.encode([query])[0]
        contexts = store.search(qv, top_k=plan.top_k)

        gate = _gate(contexts, plan)
        
        payload: Dict[str, Any] = {
            "type": "contest_recommendation",  # rag_answer → contest_recommendation
            "query": query,
            "plan": plan.__dict__,
            "contexts": contexts,
            "gating": gate,
            "answer": "",
            "stats": {  # 통계 정보 추가
                "total_results": len(contexts),
                "avg_score": float(np.mean([c["score"] for c in contexts])) if contexts else 0.0,
                "search_method": "rag_only" if plan.force_rag_only else "hybrid"
            }
        }
        
        if plan.force_rag_only or (gate["status"] == "enough" and plan.return_draft_when_enough):
            payload["answer"] = _draft_answer(query, contexts, plan)
        
        return payload