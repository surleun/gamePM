# DEV-YYYYMMDD-NNN — 개발 기능 제목

## Metadata

- 개발 ID: `DEV-YYYYMMDD-NNN`
- 프로젝트 ID:
- Unity project ref:
- 작업 유형: `implement | cleanup`
- 개발 등급: `connection_test | prototype | production`
- 등급 선정 근거:
- 상태: `draft | blocked | ready | implementing | failed_compile |
  needs_human_test | accepted | rolled_back`
- 작성일:
- 마지막 갱신:

## Request

- 사용자 목표:
- 기대 플레이어 경험:
- 포함 범위:
- 제외 범위:

## Sources

| 근거 | 출처 유형 | 경로·섹션 또는 발화 | SHA-256·상태 |
|---|---|---|---|
|  | `confirmed_document | current_user_input | live_unity_project` |  |  |

## Design Decisions

| 항목 | 확정 값·규칙 | canonical 근거 | 누락 여부 |
|---|---|---|---|
|  |  |  | `complete | design_decision_gap` |

## Visual Design

- 시각 명세 필요: `아니요 | 예`
- 적용된 Visual Specification 경로·SHA-256: `해당 없음 | 경로 · SHA-256`
- 적용된 개발 기준 시안 경로·SHA-256:
  `해당 없음 | design/assets/mockups/<file> · SHA-256`
- reference 이미지: `해당 없음 | design/assets/references/<file> · 참고 범위`
- production 시각 준비 상태: `not_applicable | complete | blocked`

## Unity Context

- Unity 버전:
- 관련 package와 버전:
- 입력·물리·렌더링 방식:
- 대상 scene·prefab·GameObject:
- 기존 관련 script·assembly·namespace:
- 외부 의존성:
- scene 통합 방식: `existing_scene | standalone_scene | additive_scene |
  build_entry | not_applicable`
- Build Settings·시작 scene 변경: `없음 | 정확한 변경과 순서`

## Technical Preflight

- MCP tool namespace·Editor ready·대상 경로·Pipeline:
- 직접 필요한 package·기본 resource:
- input system·render pipeline:
- 시스템 의존성:
- 누락 의존성의 설치·import 작업: `해당 없음 | 명세 내 구현 단계`
- mutation 없는 preflight 결과: `pass | blocked`

## Implementation Contract

- 구현 동작:
- 데이터와 상태 변화:
- 입력·출력:
- 예외·실패 처리:
- 성능·플랫폼 제약:
- 허용된 `implementation_choice`:
- 금지 조건:
- 대상 파일·asset 후보:

## Development Level Contract

- 산출물 분류: `connection_test | prototype | production`
- 통합 방식: `isolated | shared_integration`
- 생성·수정할 전용 경로:
- 기존 공용 파일 수정 목록: `없음 | 정확한 경로와 변경 목적`
- placeholder 목록: `없음 | 정확한 대상과 용도`
- placeholder 허용·교체 조건: `해당 없음 | 허용 범위·폐기 시점·교체 기준`
- 보존 정책: `preserve_until_explicit_cleanup`
- 정리 그룹: `connection_test | prototype | none`
- 승격 조건: `해당 없음 | 새 production 명세·실행에 필요한 조건`
- 등급별 완료 조건:

## Artifact Cleanup

- 정리 대상 artifact index 항목: `해당 없음 | 실행 ID 목록`
- 원본 구현 보고서: `해당 없음 | development/runs/<file>`
- 현재 SHA-256·후속 실행 의존성 재확인: `해당 없음 | pass | blocked`
- 정리 허용 범위: `해당 없음 | 전용 파일 제거·공용 파일 복원 범위`
- 차단 항목 처리: `해당 없음 | 보존 후 blocked 보고`

## Editor Tool Policy

- Editor 도구 필요 예상: `아니요 | 예 | 구현 중 기준에 따라 판단`
- 확인된 반복 사용 도구: `해당 없음 | 도구·재사용 대상·정식 경로`
- 허용되는 임시 도구 범위:
- 임시 도구 경로: `Assets/Editor/GamePMTemp/<run_id>/`
- source·meta snapshot과 삭제 시점: `실행 후 backup·SHA 기록, 최종 compile 전 삭제`

## Verification

- compile 성공 조건:
- 새 console error 허용: `아니요 | 명시된 예외`
- 자동 Play Mode·입력·화면 검증: `아니요 | 예`
- 자동 검증 범위·결과물 보존: `해당 없음 | 정확한 범위와 보존 경로`
- 사람 플레이 테스트 절차:
- 사용자 성공 판정 기준:
- rollback 기준:

## Handoff

- 대상 agent: `unity_developer`
- 실행 ID: `preflight 전 미발급 | DEV-YYYYMMDD-NNN-RUN-NNN`
- 명세 경로:
- 공식 Unity MCP 필요: `예`
- `eval | eval_file` 허용: `아니요`
- 반환 형식: `docs/templates/unity_implementation_report.md`
- 중단 상태: `blocked_missing_development_handoff |
  blocked_invalid_unity_project | blocked_missing_development_decision |
  blocked_unity_mcp_unavailable`
