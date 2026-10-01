# Scenario Writing Quality Skill

## Purpose

인게임 스크립트의 문장과 Scene 구성이 읽기 쉽고 플레이 가능한지 판단하는
품질 기준만 소유한다. Writer's Brief, source order, PCA, `CW-*`·`NR-*`, 독립
검수와 승인 경계는 `docs/workflows/write_ingame_script.md`가 소유한다.

## Scene Composition

- 한 Scene은 하나의 입력 대기 지점 또는 하나의 확정 결과 전달 단위로 나눈다.
- 모든 Scene과 분기는 선언된 진입점에서 도달 가능하고 종료, 다음 Scene 또는
  명시적 `TBD`로 이어져야 한다.
- 플레이어 노출 line은 화자, 지문·대사와 선택지를 실행 순서로 둔다.
- 구현 영역은 진입·종료 조건, 입력 mode, 분기, Outcome, 상태 변화와 공개
  정보를 플레이어 노출 문장과 분리한다.
- `Outcome Routing`에는 Outcome ID, 상태 변화와 다음 Scene을 두고,
  `Outcome Details`에는 같은 순서로 확정 결과와 공개 정보를 둔다.
- Routing의 모든 Outcome은 Details에 정확히 한 번 대응하고 ID, 순서와 값이
  같아야 한다.
- Outcome별 공개 정보와 Scene 전체 `Information Visibility`를 구분한다.
- 미확정 리소스·판정값·데이터 ID는 `TBD`로 둔다.

## Player Agency

- 아직 선택하지 않은 플레이어 행동이나 대사를 이미 수행된 것으로 쓰지 않는다.
- 선택지를 표시한 뒤에는 입력을 기다리고 자동 선택·자동 확정을 추가하지 않는다.
- 선택지는 서로 다른 의도나 체감 결과를 제공한다. 의도적 합류에는 합류 이유와
  선택 이력을 남긴다.
- 숨겨진 정보와 미충족 공개 조건을 플레이어 노출 대본에 섞지 않는다.

## Data Consistency

- `choice_only`와 `choice_and_text`에는 하나 이상의 선택지가 있어야 한다.
- `narrative_only`에는 등록 가능한 `continue_outcome_id`가 필요하다.
- input mode, choices, checks, Outcome, 상태 변화와 next Scene 조합이 서로
  모순되지 않아야 한다.
- 내부 ID와 구현 메모는 플레이어 노출 문장에 넣지 않는다.

## Writing Craft

- 승인된 같은 프로젝트 대본에서 확인한 한국어 문체와 인물 말투를 우선한다.
- 설명으로 사건을 요약하기보다 감각, 행동, 반응과 subtext로 장면화한다.
- 각 line은 정보, 감정, 갈등, 선택 압력 또는 인물성 중 하나 이상의 목적을
  가진다.
- 화면에서 읽기 어려운 장문은 리듬과 의미 단위로 나눈다.
- 근거 없는 상투적 장르 어휘나 과도한 고어체를 자동으로 덧붙이지 않는다.
- 선택지 문구는 행동과 의도가 분명하고 선택 전 결과를 과도하게 누설하지 않는다.

## Quality Check

- 작성 workflow가 제공한 line·경로·선택·시간 측정값이 실제 Scene과 분기에서
  같은 단위·포함 기준으로 재현되는가
- 모든 Scene과 분기가 도달 가능하고 종료점이 있는가
- 플레이어 선택 전 행동·대사가 확정되지 않았는가
- Outcome Routing과 Details가 1:1로 일치하는가
- 플레이어 노출 문장에 내부 ID, 숨은 조건이나 제작 메모가 없는가
- 문장마다 장면 내 기능이 있고 인물별 말투가 구별되는가
