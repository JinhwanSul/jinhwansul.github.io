# Jinhwan Sul — 개인 홈페이지

`jinhwansul.github.io`용 영어 연구자 홈페이지입니다. About, Publications, CV 페이지를 제공하며, About 페이지에서 연구·학력·경력 내용을 아래로 스크롤하며 볼 수 있습니다. 이 폴더를 만들었다는 것만으로 GitHub Pages에 배포되지는 않습니다.

## 로컬에서 보기

터미널에서 이 `homepage` 폴더로 이동한 뒤 실행합니다.

```sh
python3 scripts/build.py
python3 -m http.server 8000
```

브라우저에서 [로컬 홈페이지](http://localhost:8000)를 엽니다. 서버를 종료하려면 터미널에서 `Ctrl+C`를 누릅니다.

## 내용 수정하기

| 수정할 내용 | 파일 |
| --- | --- |
| 연락처 링크, 검색용 설명, 사이트 주소, 업데이트 날짜 | `data/profile.json` |
| 자기소개, 학력, 경력, 연구 소개 | `scripts/build.py`의 `home_content()` |
| 논문 제목, 저자, 연도, 발표처, 링크 등 | `data/publications.json` |
| 다운로드용 CV | `assets/Jinhwan_Sul_CV.pdf` |
| 프로필 사진 | `assets/jinhwan-sul.jpg` |
| 색상, 글꼴, 간격, 반응형 레이아웃 | `assets/styles.css` |
| 논문 필터와 현재 섹션 표시 | `assets/site.js` |
| 페이지 구성과 HTML 템플릿 | `scripts/build.py` |

내용을 수정한 뒤 `python3 scripts/build.py`를 다시 실행하고 브라우저를 새로고침합니다. 생성된 HTML을 직접 고치면 다음 생성 시 덮어써지므로, 데이터나 템플릿을 수정합니다. CV와 사진은 위 파일명을 유지하여 교체하면 됩니다.

CV 화면은 PDF를 변환한 이미지 3장으로 미리보기를 제공합니다. PDF를 교체하고 다시 생성하면 Poppler의 `pdftoppm`으로 이미지를 갱신합니다. Poppler가 없는 환경에서 PDF를 바꾸면 이전 이미지는 표시하지 않고 원본 PDF 링크를 제공합니다. PDF 원본은 수정하지 않습니다.

논문을 추가할 때는 기존 JSON 항목의 형식을 따릅니다. 논문 상태와 발표처를 구분하고, 확인된 링크만 입력합니다. 공개 코드가 없으면 `code` 값은 `null`로 둡니다.

## GitHub Pages에 올리기

1. GitHub 계정의 사용자명이 `JinhwanSul`이라면 저장소 이름을 `jinhwansul.github.io`로 만듭니다.
2. 홈페이지를 생성한 뒤, 이 `homepage` 폴더 **안의 파일과 하위 폴더**를 저장소의 최상위에 올립니다. `homepage`라는 상위 폴더를 그대로 넣지 않습니다. 숨김 파일 `.nojekyll`도 포함합니다.
3. 저장소의 **Settings → Pages → Build and deployment**에서 **Deploy from a branch**, 브랜치 **main**, 폴더 **/ (root)**를 선택하고 저장합니다.
4. GitHub의 배포 완료 표시를 확인한 뒤 [홈페이지 주소](https://jinhwansul.github.io/)에서 확인합니다.

이 사이트는 정적 HTML·CSS·JavaScript 파일로 동작합니다. 생성에는 Python 표준 라이브러리만 사용하며, 호스팅 환경에 별도 서버나 추가 의존성을 설치할 필요가 없습니다. 이후 변경 사항도 로컬에서 다시 생성한 뒤 저장소에 올립니다.
