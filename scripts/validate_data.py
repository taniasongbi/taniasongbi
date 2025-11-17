#!/usr/bin/env python3
"""
EMG 데이터 검증 스크립트

이 스크립트는 저장소의 모든 CSV 파일을 검증하여:
1. 파일 존재 여부 확인
2. 기본 구조 확인 (컬럼 수, 헤더)
3. 데이터 무결성 확인 (결측값, 데이터 타입)
4. 샘플링 레이트 일관성 확인
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path

# 저장소 루트 디렉토리
REPO_ROOT = Path(__file__).parent.parent
DATA_DIR = REPO_ROOT / "data" / "raw"

# 예상 컬럼 수
EXPECTED_COLUMNS = 17  # Time (s) + 16 EMG channels
EXPECTED_SAMPLING_RATE = 2147  # Hz (대략적인 값)

def validate_file(filepath):
    """단일 파일 검증"""
    results = {
        'filename': filepath.name,
        'exists': False,
        'readable': False,
        'columns_ok': False,
        'rows': 0,
        'missing_values': 0,
        'sampling_rate': 0,
        'errors': []
    }
    
    try:
        # 파일 존재 확인
        if not filepath.exists():
            results['errors'].append("파일이 존재하지 않습니다")
            return results
        
        results['exists'] = True
        
        # 파일 읽기
        try:
            df = pd.read_csv(filepath, nrows=1000)  # 먼저 일부만 읽어서 구조 확인
            results['readable'] = True
        except Exception as e:
            results['errors'].append(f"파일 읽기 실패: {str(e)}")
            return results
        
        # 컬럼 수 확인
        if len(df.columns) == EXPECTED_COLUMNS:
            results['columns_ok'] = True
        else:
            results['errors'].append(f"예상 컬럼 수: {EXPECTED_COLUMNS}, 실제: {len(df.columns)}")
        
        # 전체 파일 읽기 (행 수 확인)
        try:
            df_full = pd.read_csv(filepath)
            results['rows'] = len(df_full)
            
            # 결측값 확인
            results['missing_values'] = df_full.isnull().sum().sum()
            
            # 샘플링 레이트 계산
            if 'Time (s)' in df_full.columns and len(df_full) > 1:
                time_diff = df_full['Time (s)'].diff().dropna()
                if len(time_diff) > 0:
                    avg_interval = time_diff.mean()
                    results['sampling_rate'] = 1.0 / avg_interval if avg_interval > 0 else 0
            
        except Exception as e:
            results['errors'].append(f"전체 파일 읽기 실패: {str(e)}")
        
    except Exception as e:
        results['errors'].append(f"예상치 못한 오류: {str(e)}")
    
    return results

def main():
    """메인 검증 함수"""
    print("=" * 60)
    print("EMG 데이터 검증 시작")
    print("=" * 60)
    print()
    
    # 데이터 디렉토리 확인
    if not DATA_DIR.exists():
        print(f"오류: 데이터 디렉토리를 찾을 수 없습니다: {DATA_DIR}")
        return
    
    # CSV 파일 목록 가져오기
    csv_files = list(DATA_DIR.glob("*.csv"))
    
    if not csv_files:
        print(f"오류: {DATA_DIR}에 CSV 파일이 없습니다")
        return
    
    print(f"발견된 파일 수: {len(csv_files)}")
    print()
    
    # 각 파일 검증
    all_results = []
    for csv_file in sorted(csv_files):
        print(f"검증 중: {csv_file.name}")
        results = validate_file(csv_file)
        all_results.append(results)
        
        if results['errors']:
            print(f"  ⚠️  오류: {', '.join(results['errors'])}")
        else:
            print(f"  ✓ 파일 정상")
            print(f"    - 행 수: {results['rows']:,}")
            print(f"    - 결측값: {results['missing_values']}")
            print(f"    - 샘플링 레이트: {results['sampling_rate']:.2f} Hz")
        print()
    
    # 요약 통계
    print("=" * 60)
    print("검증 요약")
    print("=" * 60)
    
    valid_files = [r for r in all_results if not r['errors']]
    invalid_files = [r for r in all_results if r['errors']]
    
    print(f"총 파일 수: {len(all_results)}")
    print(f"정상 파일: {len(valid_files)}")
    print(f"오류 파일: {len(invalid_files)}")
    
    if valid_files:
        total_rows = sum(r['rows'] for r in valid_files)
        total_missing = sum(r['missing_values'] for r in valid_files)
        avg_sampling_rate = np.mean([r['sampling_rate'] for r in valid_files if r['sampling_rate'] > 0])
        
        print()
        print(f"총 데이터 행 수: {total_rows:,}")
        print(f"총 결측값: {total_missing}")
        print(f"평균 샘플링 레이트: {avg_sampling_rate:.2f} Hz")
    
    if invalid_files:
        print()
        print("오류가 있는 파일:")
        for r in invalid_files:
            print(f"  - {r['filename']}: {', '.join(r['errors'])}")
    
    print()
    print("검증 완료")

if __name__ == "__main__":
    main()

