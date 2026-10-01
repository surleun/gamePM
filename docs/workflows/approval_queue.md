# Approval Queue Workflow

## Purpose

AI가 만든 변경안을 사용자가 검토하고 결정할 수 있게 관리한다.

이 문서는 승인 상태 전환, 적용 직전 원본 재확인, 확정 문서 적용,
Decision Log·Version History 기록과 에셋 승격의 유일한 상세 원본이다.
승인 항목의 필드와 배치는 `docs/templates/approval_item.md`가 소유한다.

`approvals/approval_queue.md`는 모든 승인 항목을 상태별 링크로 보여주는
색인이다. 각 승인 항목의 상세 내용과 상태의 원본은
`approvals/items/<year>/APPR-YYYYMMDD-NNN-<content-slug>.md`에 둔다. 개별 문서는 생성 이후 상태가
바뀌어도 이동하지 않는다.

## Status

승인안 등록·개정·상태 변경·적용 작업이 끝나면
`docs/workflows/tbd_tracking.md`에 따라 관련 입력·추적 항목을 갱신한다.
추적 문서의 상태는 아래 승인 상태의 원본을 대체하지 않는다.

- `pending`: 검토 대기
- `approved`: 승인됨, 아직 적용 전
- `applied`: 확정 문서에 반영 완료
- `on_hold`: 보류
- `change_requested`: 수정 요청
- `rejected`: 거부
- `needs_reconfirmation`: 적용 직전 원본이 달라져 재확인 필요

## Add Item Steps

1. `docs/workflows/project_workspace.md`에 따라 대상 프로젝트를 결정한다.
2. `docs/templates/approval_item.md` 형식을 따른다.
3. 작성·창작 workflow의 read-only 결과, 필수 검수와 의존성 해소 상태를
   확인한다. 미해결 차단이나 필수 수정이 있으면 저장하지 않는다.
4. `docs/workflows/document_structure.md`가 요구한 owner와 원자적 restructure
   범위, 링크 갱신을 template의 해당 필드에 기록한다.
5. 모든 대상의 현재 비교 범위, 기준 상태, 해시 방식과 SHA-256, 근거, 의존
   항목과 검토 에셋을 template에 기록한다. Git을 사용할 수 있으면 기준
   커밋을 보조 정보로 함께 기록하고, Git이 없으면 `해당 없음`으로 둔다.
6. `approvals/items/<생성 연도>/APPR-YYYYMMDD-NNN-<content-slug>.md`에 개별 승인 문서를 만들고 상태는
    기본적으로 `pending`으로 둔다.
7. Approval Queue의 `Pending` 구역에 개별 문서 링크를 추가한다. 모든 상태
    구역은 승인 ID 생성 순서인 오래된 항목부터 최신 항목 순으로 정렬한다.

## Revised Draft Re-entry

Scenario Improvement 선택 반영은 `docs/skills/scenario_review.md`, CP 선택
반영은 `docs/skills/design_creative_completion.md`가 소유한다. 두 경우 모두
검수된 새 Draft가 돌아오면 기존 승인을 재사용하지 않고 이 workflow의
`pending` 진입 검사를 다시 수행한다. 대상·목적·핵심 범위가 달라졌다면 기존
항목을 보존하고 새 항목 또는 원자적 `restructure` 항목으로 분리한다. PCA
과거 결과 정책은 `docs/workflows/project_creative_agent_setup.md`를 따른다.

## Apply Approved Item Steps

1. 사용자가 승인한 항목 ID나 제목을 명시했는지 확인한다.
2. 승인 항목의 프로젝트 ID, 대상 문서 경로, 기준 방식, 비교 대상, 작성 당시
   기준 상태, 해시 방식·SHA-256과 원본 요약이 기록되어 있는지 확인한다.
   기준 Git 커밋은 `git_and_file_sha256`일 때만 요구한다.
3. 승인 큐, 대상 문서, 결정 로그와 버전 기록이 모두 같은 프로젝트에 속하는지 확인한다.
4. Dependency Operations가 있으면 모든 선행 항목이 같은 프로젝트에 속하고
   `applied`인지 확인한다. 미적용 항목이 있으면 본 항목을 적용하지 않고 Review
   Notes에 대기 사유를 기록한다.
5. 선행 항목이 적용되었다면 그 변경으로 본 항목의 원본, `TBD` 또는 영향 범위가
   달라졌는지 확인한다. 달라졌으면 본 항목을 `needs_reconfirmation`으로 이동해
   초안을 갱신하고 다시 승인받는다.
6. 기존 문서 변경 또는 삭제는 작성 당시 비교 대상의 SHA-256과 현재 같은
   범위를 같은 해시 방식으로 계산한 SHA-256을 비교한다.
7. 신규 문서 생성은 작성 당시 기준 상태가 `absent`인지 확인하고, 현재 대상
   경로에 파일이 생겼는지와 `workspace/projects/<project_slug>/design/`에 동일
   제목·역할·범위의 문서가 새로 생겼는지 검색한다.
8. `restructure`이면 모든 기존 대상의 비교 결과와 모든 신규 문서의 역할
   중복 여부를 먼저 확인한다. 하나라도 불일치하면 어떤 대상도 변경하지 않는다.
9. `Subagent Review`가 있으면 시나리오 독립 검수의 `blocking` 또는
   `required_revision`과 프로젝트 창작 규칙이 요구한 비시나리오 독립 검수의
   필수 finding이 해소되었는지, 기획 창작이 사용자 허가 GAP 범위를 벗어나지
   않았는지 확인한다. 검수 근거가 없거나 필수 결과가 남아 있으면 적용하지
   않고 `needs_reconfirmation`으로 이동한다.
10. `Scenario Improvement Review`가 있으면 `proposed`나 `declined` 권고가
   Draft에 섞이지 않았는지 확인한다. `incorporated` 권고도 갱신된 Draft가
   명시적으로 승인된 경우에만 적용 대상으로 본다.
11. `Creative Proposal Log`가 있으면 `proposed`·`declined` 대안이 Draft에
    섞이지 않았는지, 모든 `incorporated` 내용에 대응하는 `CP-*` 각주가 있는지
    확인한다. 수치 제안은 `provisional`과 검증 기준이 있어야 한다.
12. 확정 문서 목록·경로·역할·담당 범위가 바뀌면 프로젝트 루트 README와
    `design/README.md`, `game_overview`의 영향받는 갱신이 승인 범위에 있는지
    확인한다. 누락되었으면 적용하지 않고 `needs_reconfirmation`으로 이동한다.
13. 비교 결과가 모두 일치하면 승인된 내용을 `workspace/projects/<project_slug>/design/`과
    승인 범위에 포함된 프로젝트 README·색인에 반영한다.
14. 승인 항목에 검토용 에셋이 있으면 Asset Operations의 `mockup | reference`
   역할을 확인하고 아래 Asset Promotion Rules에 따라 같은 역할의
   `design/assets/` 하위 폴더로 반영해 동일성을 검증한다. 기존 에셋 재분류는
   Asset Relocation Operations의 현재·이동 후 경로와 SHA-256을 같은 방식으로
   검증한다.
15. 비교 결과가 다르거나 기준 정보가 부족하면 적용을 중단하고
   `needs_reconfirmation`으로 처리한다.
16. 재확인 결과와 필요한 후속 조치를 승인 항목의 Review Notes와
   Decision History에 기록한다.
17. 승인 큐에서 실제 파일을 여는 근거 경로와 인라인 이미지 참조를 승인 후
    `design/assets/mockups/ | design/assets/references/`의 해당 역할 경로로
    갱신하고, Decision Log와 Version History에도 이 canonical 경로를 사용한다.
18. 같은 프로젝트의 Decision Log에 적용된 CP ID와 `provisional` 항목을 포함한
    결정 로그를 기록한다.
19. 같은 프로젝트의 Version History에 적용된 CP ID와 `provisional` 항목을
    포함한 버전 기록을 남긴다.
20. 역할별 `design/assets/` 반영, 동일성 검증과 참조 갱신이 모두 끝난 에셋만
    대응하는 `approvals/assets/` 역할 폴더에서 삭제하고 Asset Operations의
    적용 결과에 canonical 경로와 검토본 삭제 완료를 기록한다.
21. 대응하는 모든 검토용 에셋의 삭제까지 끝난 뒤 개별 승인 문서의 상태를
    `applied`로 갱신하고 Approval Queue 링크를 `Applied` 구역으로 옮긴다.

## Queue Index Rules

- 모든 개별 승인 문서는 상태와 관계없이 Approval Queue에 정확히 한 번 링크한다.
- 파일명은 승인 ID 뒤에 승인 내용을 나타내는 짧은 영문 kebab-case 슬러그를
  붙인다. 슬러그는 3~6단어를 권장하고 구현 행위보다 승인 대상을 표현한다.
  상태명은 넣지 않으며 생성 후에는 상태 변경을 이유로 파일명을 바꾸지 않는다.
- 상태의 원본은 개별 승인 문서 Metadata이며 Queue의 구역은 그 상태와 일치해야 한다.
- 각 상태 구역은 승인 ID 오름차순으로 정렬한다. 날짜가 같으면 마지막 3자리
  순번이 작성 순서를 결정한다.
- 상태가 바뀌면 개별 문서를 이동하지 않고 Metadata 상태와 Queue 링크 위치만
  함께 갱신한다.
- Queue에 없는 개별 승인 문서, 대상 파일이 없는 링크, 중복 링크와 ID·파일명·
  Metadata 불일치는 무결성 오류로 처리한다.

## Asset Promotion Rules

- 에셋 역할은 `mockup | reference` 중 하나다. `mockup`은 Unity가 구현할 화면의
  직접적인 시각 기준이고, `reference`는 설명·흐름·분위기 이해를 돕지만 그대로
  구현할 대상은 아니다.
- `mockup`은 `approvals/assets/mockups/`에서
  `design/assets/mockups/`로, `reference`는
  `approvals/assets/references/`에서 `design/assets/references/`로만 승격한다.
  역할이 다른 폴더로 교차 승격하지 않는다.
- 에셋 루트인 `approvals/assets/`와 `design/assets/` 바로 아래에 새 이미지를
  저장하지 않는다. 기존 루트 이미지를 재분류하려면 현재 경로·역할·SHA-256과
  새 경로를 모두 기록한 `restructure` 승인안을 사용한다.
- 재분류 `restructure`는 Asset Relocation Operations에 같은 프로젝트 안의
  현재 경로, 이동 후 역할 경로와 raw-bytes SHA-256을 기록한다. 적용 직전에
  원본 해시와 대상 경로의 부재를 다시 확인하고, 모든 파일을 이동한 뒤 같은
  해시를 검증해야 한다. 하나라도 불일치하면 어떤 파일도 이동하지 않는다.
- 재분류 적용에서는 현재 canonical 문서와 활성 인라인 링크만 새 경로로
  갱신한다. 과거 승인안, Decision Log, Version History와 개발 실행 기록의
  당시 경로는 감사 이력으로 보존하며 활성 참조로 보지 않는다.
- 항목이 `approved`이지만 아직 적용 전이면 검토용 에셋을 삭제하지 않는다.
- 이전 템플릿으로 작성되어 Asset Operations가 없는 항목은 기록된 검토
  경로, 승인 후 경로, 역할과 작성 당시 SHA-256으로 표를 먼저 보완한다. 이 중
  하나라도 확인할 수 없으면 적용하거나 검토본을 삭제하지 않고
  `needs_reconfirmation`으로 이동한다.
- Asset Operations의 역할과 검토·canonical 하위 폴더가 일치하지 않으면
  적용하지 않고 `needs_reconfirmation`으로 이동한다.
- 적용 전 검토용 파일의 현재 SHA-256을 Asset Operations의 작성 당시 값과
  비교한다. 값이 다르거나 파일이 없으면 에셋을 반영하거나 삭제하지 않고
  항목을 `needs_reconfirmation`으로 이동한다.
- 승인 후 경로에 파일이 없으면 승인된 파일을 해당 경로로 옮긴 뒤 SHA-256이
  검토본과 같은지 확인한다.
- 승인 후 경로에 같은 SHA-256의 파일이 이미 있으면 그 파일을 canonical
  에셋으로 사용한다. 다른 내용의 파일이 있으면 덮어쓰거나 검토본을 삭제하지
  않고 `needs_reconfirmation`으로 이동한다.
- 승인 큐에서 실제 파일을 여는 근거 경로 및 인라인 이미지 링크와 새
  Decision Log·Version History 기록은 역할에 맞는 `design/assets/` canonical
  경로를 가리켜야 한다. 이런 활성 참조가 `approvals/assets/`에 남아 있는
  동안에는 검토본을 삭제하지 않는다.
- Asset Operations의 기존 검토 경로와 SHA-256은 감사 이력으로 보존하고,
  적용 결과에 canonical 경로 반영과 검토본 삭제를 명시한다. 이 이력 표기는
  삭제된 파일을 계속 사용하는 활성 참조로 보지 않는다.
- 모든 검증과 참조 갱신이 성공한 뒤 해당 승인 항목에 연결된 검토본만
  `approvals/assets/`에서 삭제한다. 다른 항목의 에셋은 삭제하지 않는다.
- `on_hold`, `change_requested`, `rejected`, `needs_reconfirmation` 상태나 적용
  실패 상태에서는 검토본을 유지한다.

## Source Reconfirmation Rules

- 파일 또는 섹션의 작성 당시 기준 상태와 SHA-256이 원본 재확인의 권위 있는
  기준이다. Git은 필수가 아니며 커밋 ID는 감사와 추적을 위한 보조 정보다.
- 기준 방식은 `file_sha256 | git_and_file_sha256` 중 하나다. Git 저장소의
  `HEAD`를 읽을 수 있으면 `git_and_file_sha256`과 커밋 ID를 기록하고, 그렇지
  않으면 `file_sha256`과 `기준 Git 커밋: 해당 없음`을 기록한다.
- 비교 대상은 전체 문서가 기본이며, 독립적으로 식별 가능한 섹션만 바뀌는
  경우 해당 섹션을 기록할 수 있다.
- 기존 대상은 기준 상태를 `present`로 기록하고 해시 방식과 작성 당시
  SHA-256을 함께 기록한다. 신규 대상은 `absent`, 해시 방식과 SHA-256은
  `해당 없음`으로 기록한다.
- `text_lf`는 UTF-8 텍스트의 BOM을 제거하고 CRLF와 CR 줄바꿈을 LF로
  정규화한 바이트의 SHA-256이다. 그 밖의 공백·문자·마지막 줄바꿈은
  정규화하지 않는다. Markdown과 다른 UTF-8 텍스트에 사용한다.
- `raw_bytes`는 파일 바이트를 그대로 계산한 SHA-256이며 이미지와 다른
  바이너리 에셋에 사용한다.
- 섹션 비교는 제목이나 ID로 범위를 정확히 식별하고 그 범위의 텍스트만
  `text_lf` 방식으로 계산한다. 적용 직전에도 같은 범위와 방식을 사용한다.
- Git 커밋이 달라졌다는 사실만으로 불일치로 판정하지 않는다. 대상 해시,
  신규 경로의 부재 상태와 제안 영향 범위를 기준으로 판정한다.
- 원본 요약은 비교 대상의 핵심 내용과 전제 조건을 적는다. 기준 상태,
  비교 범위, 해시 방식 또는 필요한 SHA-256이 없으면 적용하지 않는다.
- 이전 템플릿으로 작성된 미적용 항목은 현재 원본을 기준으로 위 필드를
  보완하고 다시 승인받는다. 이미 `applied`인 과거 항목은 소급해 무효화하거나
  다시 적용하지 않는다.
- 기존 문서의 비교 대상 밖에서 발생한 변경도 제안의 영향 범위를 바꾸면
  불일치로 판단한다.
- 신규 문서는 동일 제목뿐 아니라 같은 역할이나 범위의 문서가 생겼는지도
  확인한다.
- `restructure`의 Target Operations는 하나의 비교 단위다. 기존 대상의
  해시·내용, 신규 문서 역할, 링크 영향 중 하나라도 달라지면 전체 항목을
  `needs_reconfirmation`으로 이동한다.
- Dependency Operations의 선행 항목이 적용되면 그 결과로 본 항목의 근거,
  `TBD` 또는 영향 범위가 달라졌는지 반드시 확인한다. 하나라도 달라지면 기존
  승인을 사용하지 않고 `needs_reconfirmation`으로 이동한다.
- `CP-*` 선택 후에는 선택 대안의 프로젝트 근거, 대상 필드와 영향 범위를
  다시 확인한다. 달라졌으면 선택이나 이전 승인을 재사용하지 않고 Draft와
  Creative Proposal Log를 갱신해 `pending`으로 되돌린다.
- Asset Operations의 검토용 파일 해시, 승인 후 경로 또는 대상 경로의 기존
  파일 상태가 기록과 다르면 해당 에셋을 삭제하지 않고 전체 항목을
  `needs_reconfirmation`으로 이동한다.
- 불일치 시 기존 승인을 사용해 자동 적용하지 않는다.

## Needs Reconfirmation Workflow

### Enter

1. 적용 직전 비교에서 원본, 영향 범위 또는 신규 문서 존재 여부가 달라지면
   적용을 중단한다.
2. 항목 상태를 `needs_reconfirmation`으로 바꾸고 실제 승인 큐의
   `Needs Reconfirmation` 영역으로 이동한다.
3. Reconfirmation에 진입 사유, 감지일, 현재 원본 요약과 비교 결과를
   기록한다.
4. 이전 승인 결정은 이력으로 보존하되 적용 권한으로 재사용하지 않는다.
5. `workspace/projects/<project_slug>/design/`, Decision Log, Version History는 수정하지 않는다.

### Resolve

- 현재 원본을 기준으로 변경안을 다시 작성한 뒤 검토를 기다리면 `pending`으로
  이동한다. 기준 방식, 선택적 Git 커밋, 비교 대상, 기준 상태, 해시 방식,
  SHA-256과 원본 요약도 함께 갱신한다.
- 사용자가 현재 원본과 갱신된 초안을 특정해 명시적으로 재승인하면
  `approved`로 이동한다. 재확인 결정자, 결정일과 이유를 기록한다.
- 사용자가 내용 수정을 요구하면 `change_requested`로 이동한다.
- 사용자가 보류하거나 거부하면 각각 `on_hold`, `rejected`로 이동한다.
- 어느 경우에도 `needs_reconfirmation`에서 `applied`로 직접 이동하지 않는다.
- 후속 상태와 전환 이유를 Reconfirmation에 기록해 재확인 이력을 보존한다.

## Non-Approval State Workflow

모든 상태 변경은 기존 Decision History를 덮어쓰지 않고 새 Decision Entry로
추가하며, 상태를 결정한 시점에 Decision Log도 작성한다.

### On Hold

- 사용자가 검토나 적용을 명시적으로 미룰 때 `on_hold`로 이동한다.
- 초안, 기준 정보, 기존 결정과 보류 이유를 그대로 보존한다.
- 사용자가 검토 재개를 요청하면 원본을 재확인한다. 기준이 같으면
  `pending`, 다르면 `needs_reconfirmation`으로 이동한다.
- 사용자가 수정 또는 거부를 결정하면 각각 `change_requested`, `rejected`로
  이동한다.

### Change Requested

- 사용자가 초안, 영향 분석 또는 누락 정보의 수정을 명시할 때
  `change_requested`로 이동하고 요청 내용을 Decision History에 기록한다.
- 대상 문서, 변경 목적과 범위가 유지되는 수정은 기존 승인 항목에 개정
  내용을 추가한다. 이전 Draft는 해당 Decision Entry의 Draft 요약으로
  추적한다.
- 대상 문서, 변경 목적 또는 핵심 범위가 달라지면 기존 항목을 종료하지 않고
  `change_requested`로 보존한 채 새 승인 항목을 만든다. 두 항목은
  `상위/대체 승인 항목`으로 서로 연결한다.
- 개정이 끝나면 기준 정보와 원본 요약을 갱신하고 `pending`으로 이동한다.
- 사용자가 수정 요청을 철회하고 검토를 종료하면 `rejected`로 이동한다.

### Rejected

- 사용자가 제안을 명시적으로 거부하거나 수정 없이 종료할 때 `rejected`로
  이동한다.
- 거부된 항목은 삭제하거나 Draft를 재사용하지 않고 결정 이유와 함께
  보존한다.
- 같은 목적을 다시 제안하려면 새 승인 항목을 만들고 기존 항목을 연결한다.
- `rejected`는 종료 상태이며 기존 항목을 `pending`으로 되돌리지 않는다.

## Apply Delete Item

1. 승인 항목의 변경 타입이 `delete`이고 사용자가 항목 ID 또는 제목과 삭제를
   명시적으로 승인했는지 확인한다.
2. Source Reconfirmation Rules에 따라 대상 문서 전체와 영향 범위를 다시
   확인한다.
3. 새 참조, 대체 문서 변경 또는 설정 유실 위험이 발견되면 삭제하지 않고
   `needs_reconfirmation`으로 이동한다.
4. 비교 결과가 같으면 대상 문서를 삭제하고, 같은 작업에서 Decision Log와
   Version History에 `delete` 기록을 추가한다.
5. Version History의 Before에는 삭제 문서 요약, After에는 `삭제됨`과 대체
   문서 경로를 기록한다.
6. 문서 삭제와 두 기록이 모두 끝난 뒤에만 승인 항목을 `applied`로 바꾼다.

삭제 승인에는 다른 문서의 동시 삭제나 수정 권한이 포함되지 않는다. 링크
정리나 대체 문서 변경이 필요하면 각각 승인 범위에 포함하거나 별도 승인
항목으로 제안한다.

## Safety Rule

승인 문구가 애매하면 승인하거나 적용하지 않는다. 예: "괜찮네", "좋아 보임",
"마음에 들어"는 명시 승인으로 보지 않는다. 이 경우 아무 변경도 적용하지
않았고 현재 승인 상태를 유지했다는 사실을 사용자에게 명시적으로 안내한다.
또한 적용하려면 대상 항목과 행동을 특정한
`APPR-...을 승인하고 적용해줘` 같은 확인이 필요하다고 알려준다.
다른 프로젝트의 승인 항목이나 결정 기록을 적용 근거로 사용하지 않는다.
`restructure`는 일부 경로만 적용하지 않는다. 검증을 모두 끝낸 뒤 전체를
적용하고 Decision Log와 Version History에 대상별 작업을 함께 기록한다.
미적용 Dependency Operations가 있는 항목은 적용하지 않는다.
`Scenario Improvement Review`의 `proposed`·`declined` 권고는 적용하지 않고,
`incorporated` 권고도 명시적으로 승인된 Draft에 포함된 내용만 적용한다.
`Creative Proposal Log`의 `proposed`·`declined` 대안은 적용하지 않고,
`incorporated` 내용도 CP 각주가 연결된 갱신 Draft가 명시적으로 승인된
경우에만 적용한다.
`Subagent Review`에 해소되지 않은 `blocking`·`required_revision` 결과가 있거나
허가받지 않은 GAP의 창작이 포함된 항목은 적용하지 않는다.
검토용 에셋이 포함된 항목은 대응하는 파일이 역할에 맞는
`design/assets/mockups/ | design/assets/references/`에 검증되어 있고 대응하는
`approvals/assets/` 역할 폴더에서 제거된 뒤에만 `applied`로 처리한다.
