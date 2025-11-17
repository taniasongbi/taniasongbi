# GitHub 저장소 설정 가이드

본 문서는 연구 데이터를 GitHub에 업로드하고 Zenodo와 연동하여 DOI를 발급받는 방법을 안내합니다.

## GitHub + Zenodo 연동의 장점

1. **버전 관리**: Git을 통한 데이터 버전 관리
2. **무료**: GitHub는 무료로 제공
3. **DOI 발급**: Zenodo와 연동하여 자동으로 DOI 발급
4. **코드와 데이터 통합**: 분석 코드와 데이터를 함께 관리
5. **장기 보존**: Zenodo가 자동으로 아카이브하여 장기 보존 보장

## 사전 준비

### 1. Git LFS 설치 확인

GitHub는 100MB 이상의 파일을 직접 업로드할 수 없으므로 Git LFS (Large File Storage)를 사용해야 합니다.

```bash
# Git LFS 설치 확인
git lfs version

# 설치되어 있지 않다면 설치
# macOS
brew install git-lfs

# 설치 후 초기화
git lfs install
```

### 2. GitHub 계정 및 저장소 준비

1. GitHub 계정이 없다면 https://github.com 에서 생성
2. 새 저장소 생성 (예: `emg-walking-data`)

## 저장소 업로드 절차

### 1단계: 로컬 Git 저장소 초기화

```bash
cd "/Users/tania/Library/Mobile Documents/com~apple~CloudDocs/사자1/research_data_repository"

# Git 저장소 초기화
git init

# Git LFS 초기화
git lfs install

# Git LFS로 CSV 파일 추적 설정
git lfs track "*.csv"

# .gitattributes 파일 커밋
git add .gitattributes
git commit -m "Configure Git LFS for CSV files"
```

### 2단계: 파일 추가 및 커밋

```bash
# 모든 파일 추가
git add .

# 첫 커밋
git commit -m "Initial commit: EMG walking data repository

- 9 CSV files with 16-channel EMG signals
- Total data: 2.0GB, 6,079,344 rows
- Sampling rate: 2,148 Hz
- Measurement period: 2024-12-11 to 2024-12-16"
```

### 3단계: GitHub 저장소에 연결 및 푸시

```bash
# GitHub 저장소 URL로 변경 (실제 저장소 URL 사용)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# 브랜치 이름 설정
git branch -M main

# GitHub에 푸시 (Git LFS 파일 포함)
git push -u origin main
```

**주의**: Git LFS를 사용하면 첫 푸시에 시간이 오래 걸릴 수 있습니다 (2GB 데이터).

### 4단계: GitHub 저장소 설정

1. GitHub 저장소 페이지에서 "Settings" 클릭
2. "General" 섹션에서:
   - Description 추가: "EMG Walking Data Repository - 16-channel electromyography signals during walking"
   - Topics 추가: `emg`, `walking`, `gait-analysis`, `biomechanics`, `research-data`
   - Visibility: Public (또는 Private, 필요시)

3. "Releases" 섹션에서:
   - 첫 번째 릴리스 생성 (v1.0.0)
   - Release notes 작성

## Zenodo 연동 및 DOI 발급

### 1단계: Zenodo 계정 생성

1. https://zenodo.org 접속
2. "Sign up" 클릭하여 계정 생성
3. GitHub 계정으로 로그인 가능 (OAuth)

### 2단계: GitHub-Zenodo 연동

1. Zenodo에 로그인
2. 상단 메뉴에서 "GitHub" 클릭
3. "Enable" 버튼 클릭하여 GitHub 인증
4. 저장소 선택 (예: `emg-walking-data`)
5. "Enable" 클릭하여 연동 활성화

### 3단계: DOI 발급

1. GitHub 저장소에서 새 Release 생성
   - Tag: `v1.0.0` (또는 원하는 버전)
   - Title: "EMG Walking Data Repository v1.0.0"
   - Description: 릴리스 노트 작성

2. Release를 "Publish" 클릭

3. Zenodo가 자동으로 감지하여:
   - 데이터를 다운로드
   - DOI 발급
   - 메타데이터 생성

4. 몇 분 후 Zenodo에서 DOI 확인:
   - Zenodo 대시보드에서 확인
   - 또는 GitHub 저장소의 "About" 섹션에 DOI가 표시됨

### 4단계: Zenodo 메타데이터 수정 (선택사항)

1. Zenodo에서 발급된 레코드로 이동
2. "Edit" 클릭
3. 메타데이터 수정:
   - Title: "EMG Walking Data Repository"
   - Description: 상세 설명 추가
   - Keywords: EMG, walking, gait analysis, biomechanics
   - License: CC BY 4.0 (또는 적절한 라이선스)
   - Publication date: 설정
   - Creators: 저자 정보 추가

4. "Save" 클릭

## README 업데이트

GitHub 저장소에 DOI가 발급되면 README.md를 업데이트하세요:

```markdown
## 인용 방법

이 데이터를 사용하실 경우, 다음 형식으로 인용해주세요:

```
[저자명]. (2024). EMG Walking Data Repository (Version 1.0) [Dataset]. 
Zenodo. https://doi.org/10.5281/zenodo.XXXXXXX
```

## 저장소 정보

- **GitHub**: https://github.com/YOUR_USERNAME/YOUR_REPO_NAME
- **DOI**: https://doi.org/10.5281/zenodo.XXXXXXX
- **Zenodo**: https://zenodo.org/record/XXXXXXX
```

## 저널 제출 시 정보 제공

저널에 데이터 저장소 정보를 제공할 때 다음 형식을 사용하세요:

### 데이터 가용성 선언

```
The data supporting the findings of this study are openly available in:
- GitHub: https://github.com/YOUR_USERNAME/YOUR_REPO_NAME
- Zenodo: https://doi.org/10.5281/zenodo.XXXXXXX
```

### 논문 본문 인용

```
The EMG walking data used in this study are publicly available 
(DOI: 10.5281/zenodo.XXXXXXX) [1].
```

### 참고문헌 형식

```
[1] [저자명]. (2024). EMG Walking Data Repository (Version 1.0) [Dataset]. 
Zenodo. https://doi.org/10.5281/zenodo.XXXXXXX
```

## 주의사항

1. **Git LFS 할당량**: 
   - GitHub Free 계정: 1GB 저장 공간, 1GB/월 대역폭
   - 2GB 데이터의 경우 유료 플랜 고려 또는 Zenodo에만 업로드

2. **대안**: 
   - Git LFS 할당량이 부족한 경우, CSV 파일은 Zenodo에만 업로드하고
   - GitHub에는 메타데이터와 코드만 업로드하는 방법도 가능

3. **버전 관리**:
   - 데이터 업데이트 시 새 Release 생성
   - Zenodo가 자동으로 새 버전에 DOI 발급

## 문제 해결

### Git LFS 파일이 업로드되지 않는 경우

```bash
# Git LFS 상태 확인
git lfs ls-files

# LFS 파일 다시 푸시
git lfs push origin main --all
```

### Zenodo 연동이 작동하지 않는 경우

1. Zenodo에서 GitHub 연동 재설정
2. GitHub 저장소의 Webhook 설정 확인
3. Release를 다시 생성

## 추가 리소스

- [Git LFS 문서](https://git-lfs.github.com/)
- [Zenodo GitHub 연동 가이드](https://guides.github.com/activities/citable-code/)
- [GitHub Releases 가이드](https://docs.github.com/en/repositories/releasing-projects-on-github)

