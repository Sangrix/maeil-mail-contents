# maeil-mail-contents

매일메일(`maeil-mail.kr`) 서비스 종료 이후,
기존 콘텐츠를 모아두기 위한 저장소입니다.

### 콘텐츠 목차

- [Frontend - 질문 ID 기준 목차](./frontend/toc.md)
- [Backend - 질문 ID 기준 목차](./backend/toc.md)
- [Frontend - 질문 세부 카테고리 기준 목차](./frontend/toc-category.md)
- [Backend - 질문 세부 카테고리 기준 목차](./backend/toc-category.md)

### 스터디용 홈페이지

`site/index.html`을 브라우저로 열면 카테고리별로 질문을 탐색하고, 검색하고, 학습 완료 체크와 랜덤 복습을 할 수 있는 개인용 정적 페이지가 실행됩니다. 인터넷 연결 없이 파일만 열어도 동작합니다.

콘텐츠(`frontend/`, `backend/`)가 갱신되면 아래 명령으로 다시 생성하세요.

```
python3 site/build.py
```
