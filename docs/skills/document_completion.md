# Document Completion Skill

## Purpose

신규·수정·재구성 Draft에서 필요한 정보가 비어 있는 지점뿐 아니라 원본이
약속한 목표·제약·검증 조건을 Draft가 충족하는지 판단할 수 없는 지점을 찾고,
안정적인 GAP ID와 유형을 부여한다. 이 문서는 원본 충분성 판정, GAP 발견,
`creative_fillable | user_fact | dependency` 분류와 사용자 고지 계약의 유일한
상세 원본이다. 사용자 허가, 대안 생성, 선택 반영과 CP 기록은 소유하지 않는다.

## Scope

- 비시나리오 Draft는 `design_creative_planner`의 `classify` Phase가 분류한다.
- 일반 시나리오와 인게임 스크립트는 각 전담 작성 agent가 같은 분류 계약을
  적용한다.
- 분류는 프로젝트 창작 규칙 없이 수행할 수 있고, Draft를 확정하거나
  승인하는 작업이 아니다.

## Requirement Register

작성·검수 전에 이번 결과를 판단할 원본 조건을 표로 등록한다. 조건은 사용자
목표, Project Brief, 게임 개요, 대상 canonical owner와 직접 연결된 확정 문서,
허가된 proposal input에서만 가져온다.

| 필드 | 필수 내용 |
|---|---|
| 조건 ID | 작업 안에서 안정적인 ID |
| 원본 조건 | 목표·제약·검증 조건 한 가지 |
| provenance | 허용된 출처 유형 |
| source locator | 발화 또는 정확한 파일·섹션 |
| 적용 이유 | 현재 범위와 결과에 미치는 연결 |
| 충족 판단 기준 | 관찰·계산·대조할 증거와 통과 조건 |
| 창작 권한 | 이 조건에 대한 구체 창작 허용 여부와 정확한 범위 |

출처 유형이나 정확한 locator가 없는 Packet 문구는 원본 조건으로 사용하지
않는다. 메인 Codex가 확정 근거로 바로잡을 수 있으면 호출 전에 수정하고,
사용자 사실이나 다른 owner 결정이 필요하면 `blocked_missing_handoff`로
중단한다. Task Packet 자체는 프로젝트 사실이나 요구조건의 출처가 아니다.

## Source Sufficiency Gate

조건 상태는 Draft 전 source readiness와 Draft 후 conformance에서 다시
판정한다. Draft 전에는 원본 locator와 충족 판단 기준을, Draft 후에는 실제
충족 위치와 검증 결과까지 요구한다.

| 상태 | 판정 기준 |
|---|---|
| `covered` | 정확한 원본 locator, 적용 가능한 충족 판단 기준, Draft가 있으면 Draft 충족 위치와 검증 결과를 모두 추적할 수 있음 |
| `partial` | 원본 또는 Draft가 조건의 일부·일부 경로·일부 상태만 충족함 |
| `unverified` | 값이나 주장은 있지만 계산 기준·가정·검증 방법 또는 재현 증거가 없음 |
| `out_of_scope` | 작성 범위 밖이지만 현재 결과의 품질·연결·검증에 실질적 영향을 줌 |
| `conflict` | 사용자 지시, 허가 범위 또는 확정 원본끼리 양립하지 않음 |

측정 가능한 수치·분량·시간·경로 수는 단위, 포함·제외 기준, 계산식·가정과
재검증 조건이 없으면 `covered`가 아니다. reviewer는 승인 판단에 영향을 주는
측정값을 원본 Draft에서 독립 재계산한다.

| 판정 | 조건 | 처리 |
|---|---|---|
| `sufficient` | 적용 조건이 모두 `covered`이고 비중요 공백만 남음 | 정상 작성·검수 |
| `sufficient_with_gaps` | material GAP과 안전한 작성 경계가 분리됨 | 안전한 Draft와 사용자 고지 반환 |
| `blocked_insufficient_source` | 핵심 결과를 추정하지 않고는 안전한 Draft를 만들 수 없음 | Draft·대안 없이 부족 조건과 질문만 반환 |

`sufficient_with_gaps`는 자동 승인 가능 상태가 아니다.

## Unsupported Assertion Gate

원본 조건과 Draft의 구체 assertion은 다음 중 하나여야 한다.

- 정확한 locator가 있는 사용자 사실 또는 confirmed document
- 사용자가 정확한 범위에 허가한 proposal·창작
- 다른 owner 결정을 기다리는 명시적 `TBD`

새 인물·관계·동행, 사건 전제·결과, 상태·능력·아이템·게임오버·시스템 규칙을
근거나 정확한 창작 허가 없이 추가하면 unsupported assertion이다. `CW-*`나
`NR-*` 공개는 provenance 기록이지 창작 권한이 아니므로 이를 합법화하지
않는다.

- Packet의 미지원 조건은 호출 전에 제거·정정한다. 정정할 근거가 없으면
  `blocked_missing_handoff`다.
- Draft에서 안전하게 제거·재작성할 수 있으면 reviewer가
  `required_revision`으로 writer에게 돌려보낸다.
- 사용자 사실이나 선행 owner 없이는 안전한 결과가 불가능하면 reviewer는
  `blocked`로 반환하고 메인 Codex가 사용자 확인으로 전환한다.

## Gap Discovery

1. Requirement Register와 Source Sufficiency Gate를 먼저 적용한다.
2. 문서 template의 필수 필드와 해당 canonical role의 한 줄 책임을 확인한다.
3. 직접 채울 수 없는 필드와 `partial | unverified | out_of_scope | conflict`
   조건 중 결과를 실질적으로 바꾸는 항목을 누락 후보로 둔다.
4. 다른 canonical owner가 소유하는 정보는 현재 문서에 복제하지 않고
   dependency 후보로 둔다.
5. 같은 원인과 같은 대상 필드의 중복 후보를 하나로 합친다.
6. 각 누락에 문서 안에서 안정적인 `GAP-<document_slug>-<number>`를 부여한다.

## Classification

| 유형 | 판정 기준 | 현재 처리 |
|---|---|---|
| `creative_fillable` | 확인된 프로젝트 근거 안에서 복수 설계안으로 제안할 수 있음 | `TBD` |
| `user_fact` | 사용자의 실제 결정 또는 확인 가능한 외부 사실이 필요함 | `TBD` |
| `dependency` | 다른 canonical owner나 선행 승인 결과가 필요함 | `TBD` |

실제 플랫폼·엔진·예산·일정·인력, 확인되지 않은 에셋·데이터 ID, 외부 계약,
법적 조건과 라이선스는 `user_fact`다. 다른 문서가 소유하는 정사·규칙·계약,
아직 적용되지 않은 선행 제안은 `dependency`다. 단순한 이름·수치·예외도
프로젝트 근거 없이 하나로 결정할 수 있다는 이유만으로 `creative_fillable`로
분류하지 않는다.

## User Notice Contract

material GAP 고지는 각 항목마다 다음을 포함한다.

- 원본 조건과 근거
- 현재 상태 `partial | unverified | out_of_scope | conflict`
- 부족한 이유와 Draft·플레이 경험·제작에 미치는 영향
- 현재 처리 `TBD | 안전한 부분만 작성 | 작성 중단`
- 필요한 사용자 결정, 확인 가능한 외부 사실 또는 선행 canonical owner
- 사용자가 바로 답할 수 있는 정확한 질문 또는 다음 요청

specialist는 고지 초안을 메인 Codex에 반환한다. 실제 사용자 고지는 메인
Codex 책임이며 Draft를 최종 결과로 제시하거나 `pending` 승인 항목으로 저장하기
전에 수행한다. 고지 없이 Draft만 제시하거나 저장하지 않는다.

## Finding Routing

- 잘못된 `covered`, 고지 누락, 재현되지 않는 측정값, 안전하게 제거 가능한
  unsupported assertion은 `required_revision`이다.
- 사용자 사실 또는 선행 dependency 없이는 안전한 Draft가 불가능하면
  reviewer verdict는 `blocked`다. 같은 writer 호출을 반복하지 않고 메인
  Codex가 사용자 질문 또는 선행 작업으로 전환한다.
- 작성자가 Draft 전에 핵심 소스 부족을 발견하면
  `blocked_insufficient_source`와 질문만 반환한다.
- `추가 개선 권고 없음`과 reviewer `pass`는 모든 material 조건이
  `covered`이거나 User Notice Contract로 고지되고 active 필수 finding이 없을
  때만 사용할 수 있다.

## Risk

각 GAP에는 `docs/skills/conflict_review.md`의 `low | medium | high` 위험도를
붙인다. canonical owner, 핵심 루프·규칙, 문서 간 계약 또는 제작 범위를
바꿀 가능성이 있으면 `high`다.

## Output

specialist는 `docs/templates/approval_item.md` 또는
`docs/templates/change_proposal.md`의 `Source Sufficiency And User Notice`와
`Creative Completion Review` 표 스키마에 맞는 충분성·GAP 결과만 반환하며
승인 항목을 조립하지 않는다. 대안, 추천, 선택이나 CP 내용을 넣지 않는다.
후속 창작은 `docs/skills/design_creative_completion.md`가 이 GAP 목록을 입력으로
받아 처리한다.
