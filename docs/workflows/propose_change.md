# Propose Change Workflow

## Purpose

`docs/workflows/document_change.md`가 선택한 update, restructure 또는 delete
branch를 검토 가능한 read-only 변경 Draft로 만든다. 확정 문서를 직접
수정하지 않는다.

## Steps

1. 라우터가 전달한 프로젝트, canonical role, 대상 경로, branch와 검색 근거를
   확인한다.
2. 대상이 프로젝트 안에 있고 현재 책임이 요청과 일치하는지 확인한다.
   owner가 여러 후보로 남으면 질문하고 Draft를 확정하지 않는다.
3. 현재 상태와 사용자 요청을 분리하고 `docs/skills/conflict_review.md`로 충돌,
   링크, 의존성과 영향 범위를 검토한다.
4. update/restructure의 비시나리오 Draft는
   `design_creative_planner`의 `classify` Phase로 보내
   `docs/skills/document_completion.md`의 GAP 발견·분류를 수행한다.
5. 분류 결과를 모두 보여준 뒤 사용자가 창작 보완을 허가한 GAP이 있으면
   `docs/skills/design_creative_completion.md`의 authorize →
   generate_options → incorporate_selection 순서를 따른다.
6. scenario role은 `docs/skills/scenario_review.md`의 작성·독립 검수 흐름으로
   보낸다.
7. delete는 대상, 참조, 대체 owner와 정보 유실 분석만 만들며 GAP 창작
   흐름을 실행하지 않는다.
8. 메인 Codex가 `docs/templates/change_proposal.md`와 승인 template으로
   변경안을 조립해 `docs/workflows/approval_queue.md`의 `pending` 진입 조건을
   따른다.

## Boundary

- 하위 skill의 GAP 유형, 허가, 옵션 수, CP나 검수 절차를 이 문서에서 다시
  정의하지 않는다.
- 창작 허가·대안 선택은 승인이나 적용이 아니다.
- 사용자 승인 전 `workspace/projects/<project_slug>/design/`을 수정하거나
  삭제하지 않는다.
