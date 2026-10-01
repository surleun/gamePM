# Document Change Workflow

## Purpose

문서 작업의 상위 라우터다. 대상 프로젝트와 canonical role을 판정하고 관련
자료를 최소 범위로 검색한 뒤 하나의 branch와 하위 workflow를 선택한다.
Draft 작성, 창작, 검수, 승인 상태 전환의 상세 절차는 소유하지 않는다.

## Entry Check

1. `docs/workflows/project_workspace.md`로 프로젝트 ID와 루트를 확정한다.
   TBD 목록 생성·입력·갱신은 보조 작업 문서 관리로 판정하고
   `docs/workflows/tbd_tracking.md`로 직접 보낸다. 기획값 변경까지 요청하면
   추적 입력과 원본 변경을 구분하고 후자는 아래 canonical role 분기를 따른다.
2. `docs/workflows/document_structure.md`로 입력을 canonical role별로 나누고
   각 단위의 현재 또는 미래 소유 문서와 표준 경로를 정한다.
3. `docs/workflows/project_search.md`의 단계적 확대·조기 중단 규칙으로 관련
   문서를 검색한다.
4. 검색 결과를 확정 문서, 승인 제안, 임시 아이디어, 결정·버전 기록으로
   구분한다. 현재 분기에 필요하지 않은 기록은 열지 않는다.
5. 아래 branch를 하나 선택하고 프로젝트, 역할, 대상 경로, 검색 근거와 판정
   이유를 하위 workflow에 전달한다.

## Branch Selection

| Branch | 선택 조건 | 다음 원본 |
|---|---|---|
| `create_new_document` | 독립 주제이고 적합한 기존 정본이 없음 | `docs/workflows/write_design_doc.md` |
| `update_existing_document` | 기존 정본의 책임 범위 안의 변경 | `docs/workflows/propose_change.md` |
| `restructure_documents` | 여러 canonical owner의 원자적 생성·수정·이동이 필요 | `docs/workflows/propose_change.md` |
| `delete_existing_document` | 사용자가 식별 가능한 정본 삭제를 요청 | `docs/workflows/propose_change.md` |
| `compile_from_sources` | 저장보다 자료 정리·요약·출처 묶음이 목적 | 읽기 전용 결과 |
| `draft_design_from_materials` | 기존 자료를 기획서 구조로 만드는 것이 목적 | `docs/workflows/write_design_doc.md` |
| `draft_ingame_script` | 플레이어 대본·씬 명세 작성이 목적 | `docs/workflows/write_ingame_script.md` |
| `ask_for_clarification` | 프로젝트·역할·대상·권한을 안전하게 판정할 수 없음 | 필요한 질문 |

## Branch Rules

### create_new_document

기존 문서에 넣으면 책임이 섞이거나 탐색성이 나빠질 때 선택한다. 미래 경로와
canonical role을 확정해 `write_design_doc.md`에 전달한다.

### update_existing_document

요청이 기존 정본의 한 줄 책임 안에 있을 때 선택한다. 정확한 대상 경로와
검색한 근거를 `propose_change.md`에 전달한다.

### restructure_documents

한 요청이 여러 소유 문서 또는 링크 갱신을 함께 요구하거나, 기존 문서에
서로 다른 role이 섞였을 때 선택한다. 일부만 먼저 적용할 수 없는 원자적 변경
범위를 `propose_change.md`에 전달한다.

### delete_existing_document

삭제 대상이 하나로 식별되고 문서 자체 제거가 목적일 때 선택한다. 참조 링크,
대체 owner와 정보 유실 가능성을 검색해 `propose_change.md`에 전달한다.

### compile_from_sources

확정·미확정 정보를 구분하고 출처를 표시해 읽기 전용으로 반환한다. 사용자가
저장을 요청하면 적합한 create/update branch로 다시 분기한다.

### draft_design_from_materials

자료의 구조화가 목적일 때 선택한다. 입력 자료와 미래 owner를
`write_design_doc.md`에 전달한다.

### draft_ingame_script

대상 시나리오, 챕터·Scene 범위와 검색 근거를
`write_ingame_script.md`에 전달한다.

### ask_for_clarification

분기를 바꾸는 핵심 정보만 질문하고 파일을 수정하지 않는다.

## Output

- 프로젝트 ID와 루트
- canonical role과 대상 또는 미래 경로
- 선택 branch와 판정 이유
- 실제 검색한 파일
- 다음 workflow 또는 필요한 질문

## Routing Boundary

- 수집 대상 원본의 변경 작업을 완료할 때는
  `docs/workflows/tbd_tracking.md`에 따라 영향받는 추적 항목도 갱신한다.
- 시나리오·GAP·PCA·전문 agent·승인 상세는 `AGENTS.md`의 Request Routing에
  있는 해당 canonical 문서로 보낸다.
- 승인 전 `design/` 수정 금지와 한 프로젝트 범위 제한을 유지한다.
- 이 라우터는 Draft, 창작 대안, 검수 보고서나 승인 항목을 직접 만들지 않는다.
