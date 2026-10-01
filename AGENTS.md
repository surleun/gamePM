# AGENTS.md

## Purpose

이 저장소는 Codex와 저장소 내부 workflow·skill·template을 사용하는 게임 기획
문서 및 Unity 개발 인계 워크스페이스다. Human in the Loop을 유지하며 AI의
분석·초안·제안은 확정 문서 변경 권한이 아니다.

## Precedence And Archive

- 현재 규칙 원본은 이 문서와 `docs/workflows/`, `docs/skills/`다.
- `docs/templates/`는 출력 형식만 정의하며 동작 규칙의 원본이 아니다.
- `docs/dev-log/`는 사용자용 역사 기록이며 현재 동작 규칙으로 읽지 않는다.
- 상세 절차는 아래 라우팅 대상 문서가 소유한다. 이 파일에서는 반복하지 않는다.

## Absolute Safety Rules

- 작업 전에 `docs/workflows/project_workspace.md`로 대상 프로젝트를 확정한다.
  여러 프로젝트가 있고 요청이 특정하지 않으면 파일을 바꾸기 전에 확인한다.
- 게임별 brief, design, ideas, approvals, decisions, versions, assets는
  `workspace/projects/<project_slug>/` 밖으로 섞지 않는다.
- canonical fact는 `docs/workflows/document_structure.md`가 정한 한 문서 역할만
  소유한다. 개요와 README에는 요약과 상대 링크만 둔다.
- 승인 전에는 `workspace/projects/<project_slug>/design/`을 수정하지 않는다.
  확정 design 변경은 해당 승인 항목에 대한 사용자의 명시적 승인과 적용
  요청, 적용 직전 원본 재확인을 모두 요구한다.
- If an approval expression is ambiguous, Explicitly tell the user that nothing was
  applied, keep the current
  approval state unchanged, and show an exact confirmation such as
  “`APPR-...`을 승인하고 적용해줘.”
- 승인 상태 전환, 적용, Decision Log·Version History 기록과 에셋 승격은
  `docs/workflows/approval_queue.md`만 따른다. `approvals/assets/`는 검토용,
  `design/assets/`는 적용된 정본이다.
- 사용자 사실과 제안을 섞거나 미지원 사실을 확정 사실로 만들지 않는다.
  안전하게 확정할 수 없는 값은 `TBD`로 둔다.
- 전문 agent는 read-only 결과만 반환한다. 메인 Codex만 승인안을 조립·저장하고
  승인된 변경을 적용한다.
- Unity 구현은 `docs/workflows/unity_development.md`의 별도 권한 경계를 따른다.
  `unity_developer`는 지정된 Unity 프로젝트만 수정하며 GamePM 기획·승인·이력
  문서를 수정하지 않는다.
- 범위 밖 리팩터링, 다른 프로젝트 자료 재사용, 비밀값 저장을 금지한다.

## Request Routing

| 요청 유형 | 상세 원본 |
|---|---|
| 프로젝트 생성·선택·전환 | `docs/workflows/project_workspace.md` |
| 확정 자료 검색·요약 | `docs/workflows/project_search.md` |
| 임시 아이디어 기록·전환 | `docs/workflows/temporary_idea.md` |
| TBD 수집·입력·추적·갱신 | `docs/workflows/tbd_tracking.md` |
| 문서 생성·수정·삭제·취합 분기 | `docs/workflows/document_change.md` |
| 자료 기반 기획 Draft | `docs/workflows/write_design_doc.md` |
| 기존 확정 문서 변경·재구성·삭제 제안 | `docs/workflows/propose_change.md` |
| GAP 발견·분류 | `docs/skills/document_completion.md` |
| 허가된 비시나리오 GAP 창작 | `docs/skills/design_creative_completion.md` |
| 시각 명세 작성·시안 준비 판정 | `docs/skills/visual_specification.md` |
| 일반 시나리오 작성·검수 | `docs/skills/scenario_review.md` |
| 인게임 스크립트 작성·검수 | `docs/workflows/write_ingame_script.md` |
| PCA 필요·생성·개정·archive·무결성 | `docs/workflows/project_creative_agent_setup.md` |
| 전문 agent 인계·출처·차단·소스 제한 | `docs/workflows/specialist_agent_handoff.md` |
| 승인 상태·적용·기록·에셋 승격 | `docs/workflows/approval_queue.md` |
| Unity 개발 명세·구현·결과·rollback | `docs/workflows/unity_development.md` |
| 행동 테스트 | `docs/workflows/behavior_testing.md` |

`docs/workflows/document_change.md`는 프로젝트와 문서 역할을 판정하고 검색한 뒤
한 branch만 선택한다. 선택 이후의 작성·창작·검수·승인 상세는 해당 하위
원본에 맡긴다.

## Specialist Gate

- `scenario_designer`, `scenario_writer`, `scenario_reviewer`,
  `design_creative_planner`, `design_creative_reviewer` 호출 전에는
  `docs/workflows/specialist_agent_handoff.md`에 따라 complete Specialist Task Packet을
  만든다.
- named custom specialist는 정확한 `agent_type`, `fork_turns: "none"`, 완성된
  packet을 사용한다. custom agent에 fork가 omitted or `"all"`인 호출은 금지한다.
- 사실·입력 출처는 `current_user_input`, `prior_user_input`,
  `confirmed_document`, `proposal_input`, `synthetic_test_fixture` 중 하나다.
- 작성·검수 Task Packet의 원본 조건에는 provenance, 정확한 locator와 충족
  검증 방법이 있어야 한다. 전문 agent는 `docs/skills/document_completion.md`의
  충분성·미지원 assertion·사용자 고지 계약을 적용한다. 핵심 결과를 추정해야
  하면 Draft 없이 차단하고, 메인 Codex는 material GAP을 Draft 제시 또는
  `pending` 저장 전에 실제 사용자에게 고지한다.
- Creative option generation, scenario authoring, in-game script writing, and
  selection incorporation are PCA-gated. 상세 판정과 세 차단 상태는
  `docs/workflows/project_creative_agent_setup.md`를 따른다.

## Creative And Narrative Boundaries

- 신규·수정·재구성 비시나리오 Draft의 GAP 분류는
  `design_creative_planner`의 `classify`로 수행한다. 사용자가 정확한
  `creative_fillable` GAP을 허가하기 전에는 대안을 만들지 않는다.
- 허가된 비시나리오 GAP만 `design_creative_planner`에 보내며 CP 기록을
  유지한다. `user_fact`와 `dependency`는 `TBD`다. 창작 허가·대안 선택은
  승인이나 적용 권한이 아니다.
- 일반 시나리오 작성·변경은 `scenario_designer` 뒤에 독립
  `scenario_reviewer` 검수를 거친다. 선택되지 않은 Scenario Improvement는
  Draft에 합치지 않는다.
- 인게임 스크립트는 `scenario_writer` 뒤에 독립 `scenario_reviewer` 검수를
  거친다. `CW-*`는 미지원 구체 창작, `NR-*`는 원본 서사 구조 이탈을 기록한다.
- 전문 agent의 결과는 프로젝트 파일을 직접 변경하지 않는 read-only 제안이다.

## Unity Development Gate

- 승인 적용된 기획을 Unity에서 구현하는 요청은
  `docs/workflows/unity_development.md`로 라우팅한다.
- `unity_developer` 호출에는 완성된 Unity Development Spec,
  `agent_type: unity_developer`, `fork_turns: "none"`가 필요하다.
- 개발 대상과 현재 Unity MCP 대상이 다르면 메인 Codex가
  `docs/workflows/unity_development.md`에 따라 프로젝트별 로컬 경로를
  생성·해결하고 MCP 대상을 전환한다. 새 Codex 작업에서 대상 일치를 확인하기
  전에는 `unity_developer`를 호출하지 않는다.
- 공식 Unity MCP가 없거나 게임 동작을 결정하는 값이 누락되면 구현하지 않는다.
- Unity compile 성공과 사람의 기능 성공 판정을 구분한다.

## Behavior Test Gate

- 모든 agent behavior/smoke test 전에
  `docs/templates/behavior_test_manifest.md`를 작성하고
  `docs/workflows/behavior_testing.md`를 따른다.
- 기본 실행 대상은 `tests/fixtures/behavior/sample-game/`이다. 실제 프로젝트
  구조가 꼭 필요할 때만 격리된 시스템 임시 복사본을 사용하고 원본 불변을
  검증한다.
- 합성 데이터의 첫 표시는 `[TEST FIXTURE: SYNTHETIC]`, provenance는
  `synthetic_test_fixture`다. 누락·오분류는 `blocked_test_provenance`다.
- 모든 테스트 보고에는 `데이터 출처`, `실행 환경`, `원본 변경`,
  `실제 프로젝트 사실로 채택`을 쓰며 합성 데이터의 채택 값은 항상 `아님`이다.

## Workspace Validation

- 사용자가 전체 작업장 무결성 검증을 요청하거나 전체 상태 확인이 필요할 때만
  `python -m unittest discover -s tests -v`를 실행한다.
- `scripts/workspace_validation.py`는 테스트가 가져다 쓰는 내부 검증 모듈이므로
  직접 실행하지 않는다.
- 개별 문서를 수정할 때마다 전체 검증을 자동으로 실행하지 않는다.

## Project File Map

- `workspace/project_registry.md`: 프로젝트 등록과 기본 프로젝트
- `workspace/projects/<project_slug>/README.md`: 사람용 프로젝트 색인
- `project_brief.md`: 프로젝트 정체성·목표·제약
- `tbd_tracker.md`: 미결정 항목의 원본 위치·사용자 입력·반영 추적
- `design/`: 승인 적용된 canonical 문서
- `design/game|world|narrative|systems|content|ui|technical/`: 역할별 정본
- `design/narrative/scripts/`: 승인된 인게임 스크립트
- `design/assets/mockups/`: 승인 적용된 개발 기준 시안
- `design/assets/references/`: 승인 적용된 설명·참고 이미지
- `ideas/temporary_ideas.md`: 미승인 아이디어
- `approvals/approval_queue.md`와 `approvals/items/`: 승인 목록과 개별 제안
- `approvals/assets/mockups/`: 승인 검토 중 개발 기준 시안
- `approvals/assets/references/`: 승인 검토 중 설명·참고 이미지
- `decisions/decision_log.md`: 수락·거절 결정 기록
- `versions/version_history.md`: 적용된 문서 변경 이력
- `agents/README.md`와 `agents/rules/`: 선택적으로 구현된 PCA 색인과 규칙
- `development/specs/`, `development/runs/`, `development/artifact_index.md`:
  Unity 개발 명세·실행 기록과 등급별 산출물 색인

## Style

- 한국어 제품 문서 스타일과 간결한 Markdown을 유지한다.
- 변경 범위를 요청한 동작에 한정하고 기존 사용자 변경을 보존한다.
- 승인·결정·버전 기록은 빠르게 훑을 수 있게 작성한다.
