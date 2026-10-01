# Design Creative Completion Skill

## Purpose

`docs/skills/document_completion.md`가 분류한 비시나리오
`creative_fillable` GAP에 대해 사용자 허가를 확인하고, 복수 대안을 만들며,
선택 결과를 `CP-*`로 추적해 Draft에 반영한다. 이 문서는 허가, 대안 생성,
선택 반영, CP와 창작 검수의 유일한 상세 원본이다. GAP을 새로 찾거나 유형을
재분류하지 않는다.

대안 생성과 선택 반영은 PCA 게이트 대상이다. 상세 판정은
`docs/workflows/project_creative_agent_setup.md`를 따른다. 일반 시나리오와
인게임 스크립트는 각각 `docs/skills/scenario_review.md`와
`docs/workflows/write_ingame_script.md`의 전용 provenance를 사용한다.

## Input Contract

- 완성된 `Creative Completion Review`
- 정확한 프로젝트, canonical role, Draft와 근거 경로
- 대상으로 삼을 `creative_fillable` GAP ID
- 사용자 허가 또는 선택 문구
- PCA 게이트 결과와 Specialist Task Packet

`user_fact`와 `dependency`는 입력되더라도 대안을 만들지 않고 `TBD`로
반환한다. 허가 범위가 없거나 모호하면 전체 GAP을 보여주고 정확한 GAP ID
선택을 요청한다.

## Phase Order

### authorize

1. 메인 Codex가 전체 GAP 목록과 분류를 사용자에게 보여준다.
2. 어떤 `creative_fillable` GAP을 창작으로 채울지 명시적으로 확인한다.
3. 사용자가 요청에서 이미 정확한 GAP 또는 범위를 허가했다면 질문을
   반복하지 않고 그 범위만 기록한다.
4. 허가, 대안 선택과 추천안 위임은 승인·적용 권한이 아니다.

### generate_options

1. 허가된 GAP과 PCA 게이트 결과만 `design_creative_planner`에 전달한다.
2. `low | medium`에는 구별되는 대안 2개, `high`에는 3개를 만든다.
3. 각 대안에 설계 의도, 프로젝트 근거, 플레이·제작·후속 owner 영향을
   기록한다.
4. 프로젝트 약속과 제약에 가장 잘 맞는 하나를 추천하고 이유를 적는다.
5. 이름만 바꾸거나 수만 채운 후보를 서로 다른 대안으로 세지 않는다.

### incorporate_selection

1. 사용자가 선택한 정확한 대안만 입력으로 사용한다.
2. 메인 Codex가 현재 원본을 재확인한 뒤 선택 결과와 현재 PCA를
   `design_creative_planner`에 전달한다.
3. 선택안만 Draft에 반영하고 해당 문장·필드에
   `[^CP-<document_slug>-<number>]` 각주를 붙인다.
4. 선택하지 않은 대안은 Draft 밖 Creative Proposal Log에 보존한다.
5. 갱신된 Draft는 명시적 승인을 기다리는 제안 상태로 돌아간다.

## Creative Proposal Log

각 허가 GAP에 `CP-<document_slug>-<number>`를 부여하고
`docs/templates/approval_item.md` 또는 `docs/templates/change_proposal.md`의
`Creative Proposal Log` 형식을 사용한다. CP 각주는 AI 기획 창작임을 밝히고
선택 근거와 영향, 관련 승인 제안을 연결한다.

## Provisional Numbers

밸런스 값·확률·시간·비용·보상량은 `provisional` 가설로만 제안한다. 값의
가정, 기대 행동, 검증 지표와 재조정 조건을 함께 기록한다. 승인은 초기
기획값 채택이지 밸런스 검증 완료가 아니다.

## Review

PCA의 `self_and_main | independent_high_risk | independent_always` 정책을
따른다. 필요한 경우 `design_creative_reviewer`가 같은 근거와 규칙으로 허가
범위, 대안 구별성, 추천 근거, owner 영향과 CP 공개를 검수한다. `blocking`
또는 `required_revision`이 남으면 원 작성 agent의 수정과 재검수 전에는 다음
단계로 보내지 않는다.

## Boundary

이 skill과 전문 agent는 read-only 제안을 반환하며 Approval Queue,
`design/`, Decision Log, Version History를 수정하거나 승인·적용하지 않는다.
메인 Codex는 승인 초안을 만들기 전에 허가 범위, 출처, CP 표식, 의존성과
검수 결과를 대조한다.
