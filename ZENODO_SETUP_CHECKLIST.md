# Zenodo 연동 및 DOI 발급 체크리스트

## 1단계: Zenodo-GitHub 연동

- [ ] Zenodo에 GitHub 계정으로 로그인: https://zenodo.org/
- [ ] Settings → GitHub → 해당 저장소(`taniasongbi/taniasongbi`) Enable (ON)
- [ ] 저장소가 **Public**인지 확인 (Private 저장소는 Zenodo에서 접근 불가)

## 2단계: 메타데이터 파일 확인

- [x] `CITATION.cff` 파일 생성 완료 (작성자 정보 수정 필요)
- [x] `.zenodo.json` 파일 생성 완료 (작성자 정보 수정 필요)
- [ ] 작성자 이름, ORCID, 라이선스 정보 업데이트

## 3단계: GitHub Release 생성

- [ ] GitHub 저장소에서 "Releases" → "Create a new release" 클릭
- [ ] Tag version: `v0.1.0` (또는 원하는 버전)
- [ ] Release title: `v0.1.0 - Initial release`
- [ ] Description 작성 (선택사항)
- [ ] "Publish release" 클릭

## 4단계: Zenodo 자동 아카이빙 확인

- [ ] Release 생성 후 몇 분 내에 Zenodo에서 아카이브 생성 확인
- [ ] Zenodo 레코드 페이지에서 DOI 확인
- [ ] 개념 DOI (모든 버전)와 버전 DOI (특정 버전) 확인

## 5단계: README 업데이트

- [ ] Zenodo 레코드 페이지에서 배지 Markdown 복사
- [ ] README.md의 DOI 배지 자리표시자(`10.5281/zenodo.XXXXXXX`)를 실제 DOI로 교체
- [ ] 인용 섹션의 DOI 링크 업데이트
- [ ] Data Availability 섹션의 DOI 링크 업데이트

## 6단계: 논문 작성 시

- [ ] Data Availability 섹션에 버전 DOI 포함 (재현성)
- [ ] 참고문헌에 버전 DOI 사용
- [ ] GitHub 저장소 링크 포함

## 개념 DOI vs 버전 DOI

- **버전 DOI**: 특정 릴리스(예: v1.0)를 정확히 가리킴. **논문 본문/참고문헌에는 버전 DOI 사용 권장** (재현성)
- **개념 DOI**: "모든 버전"을 가리킴. README 배지에는 보통 개념 DOI 사용

## 참고 링크

- [GitHub: 콘텐츠 참조/인용 & Zenodo 연동](https://docs.github.com/en/repositories/archiving-a-github-repository/referencing-and-citing-content)
- [GitHub: CITATION.cff 안내](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-citation-files)
- [Zenodo: DOI 버전 관리](https://help.zenodo.org/)
- [Zenodo: .zenodo.json 메타데이터](https://developers.zenodo.org/#depositions)

