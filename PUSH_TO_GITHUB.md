# GitHub에 푸시하기

로컬 저장소가 준비되었습니다. 이제 GitHub에 업로드하세요.

## 1단계: GitHub에서 새 저장소 생성

1. https://github.com 에 로그인
2. 우측 상단의 "+" 버튼 클릭 → "New repository" 선택
3. 저장소 정보 입력:
   - **Repository name**: `emg-walking-data` (또는 원하는 이름)
   - **Description**: `EMG Walking Data Repository - 16-channel electromyography signals during walking`
   - **Visibility**: Public (또는 Private)
   - **⚠️ 중요**: "Initialize this repository with a README" 체크하지 않기
   - "Create repository" 클릭

## 2단계: GitHub 저장소에 연결 및 푸시

GitHub에서 저장소를 생성하면 표시되는 URL을 사용하세요. 예시:

```bash
cd "/Users/tania/Library/Mobile Documents/com~apple~CloudDocs/사자1/research_data_repository"

# GitHub 저장소 URL 추가 (YOUR_USERNAME과 YOUR_REPO_NAME을 실제 값으로 변경)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# 또는 SSH 사용 시:
# git remote add origin git@github.com:YOUR_USERNAME/YOUR_REPO_NAME.git

# 브랜치 이름 확인/설정
git branch -M main

# GitHub에 푸시 (Git LFS 파일 포함)
git push -u origin main
```

**주의사항**:
- 2GB 데이터를 푸시하는 데 시간이 오래 걸릴 수 있습니다 (10-30분)
- Git LFS 파일은 별도로 업로드되므로 추가 시간이 필요합니다
- 네트워크 연결이 안정적인지 확인하세요

## 3단계: 푸시 진행 상황 확인

푸시 중에는 다음과 같은 메시지가 표시됩니다:

```
Uploading LFS objects: 100% (9/9), 2.0 GB | 0 B/s, done.
Enumerating objects: 16, done.
Counting objects: 100% (16/16), done.
...
```

## 4단계: GitHub 저장소 설정

푸시가 완료되면:

1. GitHub 저장소 페이지에서 "Settings" 클릭
2. "General" 섹션에서:
   - Description 확인/수정
   - Topics 추가: `emg`, `walking`, `gait-analysis`, `biomechanics`, `research-data`
3. 저장소가 Public인 경우, README.md가 자동으로 표시됩니다

## 5단계: Zenodo 연동 (DOI 발급)

### Zenodo 계정 생성 및 연동

1. https://zenodo.org 접속
2. "Sign up" → GitHub 계정으로 로그인
3. 상단 메뉴에서 "GitHub" 클릭
4. 저장소 옆의 "Enable" 버튼 클릭

### Release 생성 및 DOI 발급

1. GitHub 저장소에서 "Releases" → "Create a new release" 클릭
2. 정보 입력:
   - **Tag version**: `v1.0.0`
   - **Release title**: `EMG Walking Data Repository v1.0.0`
   - **Description**: 
     ```
     Initial release of EMG walking data repository.
     
     - 9 CSV files with 16-channel EMG signals
     - Total data: 2.0GB, 6,079,344 rows
     - Sampling rate: 2,148 Hz
     - Measurement period: 2024-12-11 to 2024-12-16
     ```
3. "Publish release" 클릭
4. 몇 분 후 Zenodo에서 DOI가 자동으로 발급됩니다
5. GitHub 저장소의 "About" 섹션에 DOI가 표시됩니다

## 문제 해결

### Git LFS 할당량 초과

GitHub Free 계정의 Git LFS 할당량:
- 저장 공간: 1GB
- 대역폭: 1GB/월

2GB 데이터의 경우:
- **옵션 1**: GitHub Pro로 업그레이드 ($4/월)
- **옵션 2**: CSV 파일은 Zenodo에만 업로드하고, GitHub에는 메타데이터만 업로드
- **옵션 3**: 데이터를 압축하여 크기 줄이기

### 푸시 실패 시

```bash
# Git LFS 상태 확인
git lfs ls-files

# LFS 파일 다시 푸시
git lfs push origin main --all

# 일반 파일 푸시
git push origin main
```

### 인증 문제

```bash
# GitHub 인증 확인
gh auth status

# 또는 Personal Access Token 사용
git remote set-url origin https://YOUR_TOKEN@github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
```

## 다음 단계

1. ✅ GitHub 저장소 생성
2. ✅ 데이터 푸시
3. ✅ Zenodo 연동
4. ✅ Release 생성 및 DOI 발급
5. 📝 README.md에 DOI 정보 추가
6. 📝 저널에 저장소 정보 제공

## 저널 제출 시 사용할 정보

### 데이터 가용성 선언

```
The data supporting the findings of this study are openly available in:
- GitHub: https://github.com/YOUR_USERNAME/YOUR_REPO_NAME
- Zenodo: https://doi.org/10.5281/zenodo.XXXXXXX
```

### 인용 형식

```
[저자명]. (2024). EMG Walking Data Repository (Version 1.0) [Dataset]. 
Zenodo. https://doi.org/10.5281/zenodo.XXXXXXX
```

