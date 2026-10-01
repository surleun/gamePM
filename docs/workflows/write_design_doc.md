# Write Design Doc Workflow

## Purpose

`docs/workflows/document_change.md`가 선택한 `create_new_document` 또는
`draft_design_from_materials` branch의 근거를 canonical role에 맞는 Draft로
구조화한다. 승인 전에는 확정 문서를 만들지 않는다.

## Steps

1. 라우터가 전달한 프로젝트, 미래 owner·경로, 검색 근거와 입력 자료를
   확인한다.
2. `docs/workflows/document_structure.md`로 canonical role을 확인하고 해당
   `docs/templates/` 문서 template을 사용해 출처 기반 Draft를 만든다.
3. 다른 role의 상세는 복제하지 않고 owner와 필요한 링크만 표시한다.
4. 비시나리오 Draft는 `design_creative_planner`의 `classify` Phase로 보내
   `docs/skills/document_completion.md`의 GAP 발견·분류를 수행한다.
5. 분류 결과를 모두 보여준 뒤 사용자가 창작 보완을 허가한 GAP이 있으면
   `docs/skills/design_creative_completion.md`의 authorize →
   generate_options → incorporate_selection 순서를 따른다.
6. scenario role은 `docs/skills/scenario_review.md`의 작성·독립 검수 흐름으로
   보낸다.
7. 검수된 read-only 제안은 `docs/workflows/approval_queue.md`의 진입 조건에
   맞춰 메인 Codex가 `pending` 승인 초안으로 조립한다.

## Boundary

- 출처 없는 사실은 확정하지 않고 `TBD`로 둔다.
- 하위 skill의 GAP 유형, 허가, 옵션 수, CP나 검수 절차를 이 문서에서 다시
  정의하지 않는다.
- 사용자 승인 전 `workspace/projects/<project_slug>/design/`을 수정하지 않는다.
