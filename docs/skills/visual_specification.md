# Visual Specification Skill

## Purpose

화면을 구현하거나 시안을 만들기 전에 확정 자료와 사용자 입력을 시각 명세로
구체화한다. 이 문서는 시각 정보 추출, 시각 GAP 확인, 사용자 질문,
`ready_for_mockup` 판정과 시안 검토 인계의 유일한 상세 원본이다. 이미지 생성,
승인 상태 전환, 에셋 승격과 Unity 구현 절차는 소유하지 않는다.

출력 필드와 형식은 `docs/templates/visual_specification.md`를 사용한다. 일반 GAP
분류는 `docs/skills/document_completion.md`, 허가된 창작 대안은
`docs/skills/design_creative_completion.md`, 에셋 저장·승격은
`docs/workflows/approval_queue.md`를 따른다.

## Input Boundary

- 현재 사용자 입력과 같은 프로젝트의 승인 적용된 `design/`만 게임 사실로
  사용한다.
- `approvals/assets/references/`와 `design/assets/references/`의 이미지는 설명,
  흐름과 분위기 참고로만 사용한다. 정확한 배치·스타일·완성도 근거로 승격하지
  않는다.
- 미승인 아이디어, 다른 프로젝트 자료, 과거 승인 Draft와 역사 기록을 현재
  시각 기준으로 사용하지 않는다.
- 시각 명세는 UI canonical owner에 반영될 제안이며 승인·적용 권한이 없다.

## Phase Order

### draft

1. 기능·화면 범위가 드러난 개발 명세 Draft 또는 기획 요청을 확인한다.
2. 화면 목적, 플레이어 행동, 표시 문구, 정보 위계, 배치, 상태·전환,
   색상·서체, 해상도 대응, 사용할 에셋, 제작 제약과 사람 합격 기준을 확정
   근거에서 먼저 채운다.
3. 각 근거에 경로·섹션과 SHA-256 또는 사용자 발화를 기록한다.
4. 이미지는 `mockup | reference`로 분류하고 역할이 불명확하면 사용하지 않는다.

### resolve_gaps

1. 비어 있는 필드는 `docs/skills/document_completion.md`의 안정적인 `GAP-*`와
   `creative_fillable | user_fact | dependency` 분류를 사용한다.
2. 결과를 크게 바꾸는 미결정만 쉬운 표현의 질문으로 바꾸고 한 번에 1~3개씩
   확인한다. 이미 답한 내용은 다시 묻지 않는다.
3. `creative_fillable`의 대안은 사용자가 정확한 GAP을 허가한 뒤에만
   `docs/skills/design_creative_completion.md`와 PCA 게이트로 만든다.
4. `user_fact`와 `dependency`는 임의로 채우지 않고 `TBD`로 유지한다.
5. 답변과 선택은 같은 시각 명세 Draft에 누적하고 영향받는 필드만 다시 연다.

### ready_for_mockup

다음 조건을 모두 만족할 때만 상태를 `ready_for_mockup`으로 바꾼다.

- 구현 대상 화면과 상태별 표현이 식별되어 있다.
- 화면 문구, 정보 위계, 핵심 배치와 입력 결과가 정해져 있다.
- 색상·서체·에셋 역할과 해상도 대응에 구현을 갈라놓는 `TBD`가 없다.
- 사람 합격 기준이 관찰 가능한 문장으로 적혀 있다.
- canonical owner와 승인 대상 범위가 정해져 있다.

하나라도 빠지면 상태는 `draft | awaiting_user_decisions`이며 이미지 생성 도구를
호출하지 않는다.

## Mockup Handoff

1. `ready_for_mockup` 명세만 이미지 생성 입력으로 사용한다.
2. 생성된 개발 기준 시안은 `approvals/assets/mockups/`에 두고 명세와 같은 승인
   항목에서 검토한다.
3. 사용자 피드백이 명세 변경이면 명세를 먼저 갱신하고 다시
   `ready_for_mockup`을 확인한 뒤 시안을 수정한다.
4. 사용자가 시안을 선택하거나 만족을 표시해도 승인·적용으로 해석하지 않는다.
5. 명시적 승인·적용 후에만 `design/assets/mockups/`와 canonical UI 문서가 Unity
   `production` 개발 근거가 된다.

## Development Boundary

- `connection_test`에는 시각 명세 완료를 요구하지 않는다.
- `prototype`은 placeholder와 폐기 조건을 명시한 경우 reference 이미지를 참고할
  수 있지만 최종 시각 품질을 주장하지 않는다.
- 화면을 포함한 `production`은 적용된 시각 명세와
  `design/assets/mockups/`의 직접 대응 시안이 없으면 ready로 만들지 않는다.
- 이 skill은 read-only Draft를 반환하며 Approval Queue, `design/`, Decision Log,
  Version History와 Unity 프로젝트를 직접 수정하지 않는다.
