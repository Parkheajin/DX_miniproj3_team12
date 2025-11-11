# -*- coding: utf-8 -*-
"""
Day5 인덱스 빌드 (공모전용)
"""

import os, sys, json
from pathlib import Path
from typing import List, Dict, Any
import random
from datetime import datetime, timedelta

# ───────── 더미 공모전 생성 ─────────
def build_corpus(num_contests: int = 20) -> List[Dict[str, Any]]:
    """
    공모전 더미 데이터 생성 (테스트/데모용)
    
    Args:
        num_contests: 생성할 공모전 개수
        
    Returns:
        corpus: [{"id": str, "text": str, "meta": dict}, ...]
    """
    contest_templates = [
        {
            "name": "AI 헬스케어 챌린지",
            "host": "삼성전자",
            "field": "AI/헬스케어",
            "eligibility": "대학생, 일반인",
            "team_size": "1~4명",
            "prize": "대상 1,000만원, 우수상 500만원",
            "preferred_major": "컴퓨터공학, 의학, 생명공학",
            "detail": "딥러닝 기반 의료 영상 분석 기술을 활용한 질병 조기 진단 솔루션 개발"
        },
        {
            "name": "스마트시티 아이디어 공모전",
            "host": "서울시",
            "field": "도시계획/ICT",
            "eligibility": "제한없음",
            "team_size": "1~5명",
            "prize": "대상 2,000만원, 최우수상 1,000만원",
            "preferred_major": "도시공학, 건축학, IT",
            "detail": "IoT와 빅데이터를 활용한 스마트시티 구축 아이디어 제안"
        },
        {
            "name": "친환경 패키징 디자인 공모전",
            "host": "환경부",
            "field": "디자인/환경",
            "eligibility": "대학생",
            "team_size": "1~3명",
            "prize": "대상 500만원, 우수상 300만원",
            "preferred_major": "산업디자인, 환경공학",
            "detail": "재활용 가능한 친환경 소재를 활용한 혁신적인 패키징 디자인"
        },
        {
            "name": "핀테크 서비스 개발 공모전",
            "host": "금융위원회",
            "field": "핀테크/금융",
            "eligibility": "일반인, 스타트업",
            "team_size": "2~5명",
            "prize": "대상 3,000만원, 우수상 1,500만원, 투자 연계",
            "preferred_major": "경제학, 컴퓨터공학, 금융공학",
            "detail": "블록체인, AI를 활용한 혁신적인 금융 서비스 개발"
        },
        {
            "name": "소셜벤처 창업 아이디어 경진대회",
            "host": "중소벤처기업부",
            "field": "사회혁신/창업",
            "eligibility": "만 39세 이하",
            "team_size": "1~4명",
            "prize": "대상 1,500만원, 창업 지원금 5,000만원",
            "preferred_major": "경영학, 사회학, 제한없음",
            "detail": "사회문제 해결을 위한 지속가능한 비즈니스 모델 제안"
        },
        {
            "name": "메타버스 콘텐츠 크리에이터 공모전",
            "host": "문화체육관광부",
            "field": "메타버스/콘텐츠",
            "eligibility": "대학생, 일반인",
            "team_size": "1~6명",
            "prize": "대상 2,000만원, 우수상 1,000만원",
            "preferred_major": "게임개발, 3D디자인, 컴퓨터공학",
            "detail": "메타버스 플랫폼에서 활용 가능한 창의적인 콘텐츠 제작"
        },
        {
            "name": "빅데이터 분석 경진대회",
            "host": "한국데이터산업진흥원",
            "field": "빅데이터/AI",
            "eligibility": "대학생, 대학원생",
            "team_size": "1~4명",
            "prize": "대상 1,000만원, 우수상 500만원, 기업 인턴십",
            "preferred_major": "통계학, 컴퓨터공학, 데이터사이언스",
            "detail": "공공 빅데이터를 활용한 사회문제 해결 분석 모델 개발"
        },
        {
            "name": "모바일 앱 개발 챌린지",
            "host": "네이버",
            "field": "모바일/앱개발",
            "eligibility": "대학생",
            "team_size": "2~4명",
            "prize": "대상 1,500만원, 우수상 700만원, 채용 연계",
            "preferred_major": "컴퓨터공학, 소프트웨어공학",
            "detail": "일상의 불편함을 해결하는 혁신적인 모바일 애플리케이션 개발"
        },
        {
            "name": "ESG 경영 아이디어 공모전",
            "host": "대한상공회의소",
            "field": "경영/지속가능성",
            "eligibility": "대학생, 일반인",
            "team_size": "1~3명",
            "prize": "대상 800만원, 우수상 400만원",
            "preferred_major": "경영학, 환경공학, 제한없음",
            "detail": "기업의 환경·사회·지배구조 개선을 위한 실행 가능한 전략 제안"
        },
        {
            "name": "관광 마케팅 콘텐츠 공모전",
            "host": "한국관광공사",
            "field": "관광/마케팅",
            "eligibility": "제한없음",
            "team_size": "1~5명",
            "prize": "대상 1,000만원, 우수상 500만원",
            "preferred_major": "관광학, 마케팅, 미디어커뮤니케이션",
            "detail": "한국 관광 활성화를 위한 창의적인 마케팅 콘텐츠 기획 및 제작"
        }
    ]
    
    corpus: List[Dict[str, Any]] = []
    
    for i in range(num_contests):
        template = contest_templates[i % len(contest_templates)]
        
        # 랜덤 마감일
        days_until = random.randint(1, 180)
        deadline = (datetime.now() + timedelta(days=days_until)).strftime("%Y-%m-%d")
        
        # 회차 추가
        contest_num = i // len(contest_templates) + 1
        name_suffix = f" {contest_num}회" if contest_num > 1 else ""
        
        # 공모전 텍스트 (고정 형식)
        text = f"""[공모전명]: {template['name']}{name_suffix}
[주최]: {template['host']}
[분야]: {template['field']}
[참가 자격]: {template['eligibility']}
[팀 규모]: {template['team_size']}
[마감일]: {deadline}
[상금 및 혜택]: {template['prize']}
[전공 우대]: {template['preferred_major']}
[상세 내용]: {template['detail']}"""
        
        path = f"contests/contest_{i+1:03d}.txt"
        
        corpus.append({
            "id": f"{path}::chunk_0000",
            "text": text,
            "meta": {
                "path": path,
                "chunk": 0
            }
        })
    
    return corpus


# ───────── 코퍼스로부터 인덱스 빌드 ─────────
def build_index_from_corpus(
    corpus: List[Dict[str, Any]],
    index_dir: str,
    model: str = "text-embedding-3-small",
    batch_size: int = 128
):
    """
    코퍼스로부터 FAISS 인덱스 생성
    
    Args:
        corpus: [{"id": str, "text": str, "meta": dict}, ...]
        index_dir: 인덱스 저장 디렉토리
        model: 임베딩 모델명
        batch_size: 배치 크기
    """
    from student.day2.impl.embeddings import Embeddings
    from student.day2.impl.store import FaissStore
    
    print(f"[INFO] 코퍼스 크기: {len(corpus)}개")
    
    # 임베딩 생성
    emb = Embeddings(model=model, batch_size=batch_size)
    texts = [item["text"] for item in corpus]
    
    print(f"[INFO] 임베딩 생성 중... (model={model})")
    vectors = emb.encode(texts)
    print(f"[OK] 임베딩 완료: shape={vectors.shape}")
    
    # FAISS 인덱스 생성
    store = FaissStore(dim=vectors.shape[1])
    
    print(f"[INFO] FAISS 인덱스에 추가 중...")
    for i, (item, vec) in enumerate(zip(corpus, vectors)):
        doc = {
            "id": item["id"],
            "text": item["text"],
            "path": item.get("meta", {}).get("path", ""),
            "chunk": item.get("meta", {}).get("chunk", 0),
        }
        store.add(doc, vec)
    
    print(f"[OK] 인덱스 추가 완료: {len(corpus)}개")
    
    # 저장
    index_dir_path = Path(index_dir)
    index_dir_path.mkdir(parents=True, exist_ok=True)
    
    idx_path = index_dir_path / "faiss.index"
    docs_path = index_dir_path / "docs.jsonl"
    
    store.save(str(idx_path), str(docs_path))
    print(f"[OK] 인덱스 저장: {idx_path}")
    print(f"[OK] 문서 저장: {docs_path}")

def save_docs_jsonl(items: List[Dict[str, Any]], out_path: str):
    """
    문서 메타를 JSONL로 저장(ensure_ascii=False)
    """
    # ----------------------------------------------------------------------------
    # TODO[DAY2-G-07] 구현 지침
    #  - with open(out_path,"w",encoding="utf-8") as f:
    #       for it in items: f.write(json.dumps(it, ensure_ascii=False) + "\n")
    # ----------------------------------------------------------------------------
    # 정답 구현:
    with open(out_path, "w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")

# ───────── CLI 진입점 ─────────
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Day5 공모전 인덱스 빌드")
    parser.add_argument("--index_dir", default="indices/day5", help="인덱스 저장 경로")
    parser.add_argument("--model", default="text-embedding-3-small", help="임베딩 모델")
    parser.add_argument("--num_contests", type=int, default=20, help="더미 공모전 개수")
    parser.add_argument("--batch_size", type=int, default=128, help="임베딩 배치 크기")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Day5 공모전 인덱스 빌드")
    print("=" * 60)
    print(f"[INFO] 더미 공모전: {args.num_contests}개")
    print(f"[INFO] 인덱스 경로: {args.index_dir}")
    print(f"[INFO] 임베딩 모델: {args.model}")
    print("=" * 60)
    
    # 더미 코퍼스 생성
    corpus = build_corpus(num_contests=args.num_contests)
    
    # 인덱스 빌드
    build_index_from_corpus(
        corpus=corpus,
        index_dir=args.index_dir,
        model=args.model,
        batch_size=args.batch_size
    )
    
    print("\n" + "=" * 60)
    print("[DONE] 인덱스 빌드 완료 ✅")
    print("=" * 60)


if __name__ == "__main__":
    main()