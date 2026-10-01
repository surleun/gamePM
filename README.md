# GamePM Codex Workspace

이 저장소는 Codex와 함께 게임 기획 자료를 작성하고 관리하는 로컬 문서
작업장이다. 별도의 OpenAI API 제품이나 게임 실행 프로그램은 아니다.

Codex는 기존 자료 검색, 기획서 초안, 창작 대안, 충돌 검토와 승인 기록을
도와준다. 게임의 확정 문서는 사용자가 승인 항목을 명시적으로 승인하고
적용해 달라고 요청한 뒤에만 변경한다.

## 빠른 시작

1. [프로젝트 목록](workspace/project_registry.md)에서 현재 작업할 게임을 확인한다.
2. 해당 프로젝트의 README에서 소개, 현재 초점과 확정 문서 목록을 확인한다.
3. Codex 입력창에 원하는 작업을 자연어로 요청한다.
4. 변경안이 만들어지면 Approval Queue에서 내용을 검토하고 승인·수정·보류·
   거부 중 하나를 결정한다.

현재 기본 프로젝트는
[십이인연록](workspace/projects/chronicles-of-the-twelve-bonds/README.md)이다.

## 할 수 있는 일

- 새 게임 프로젝트를 만들고 여러 프로젝트 사이에서 작업 대상을 전환한다.
- 프로젝트에 어떤 자료가 있는지 검색하고 요약한다.
- 여러 확정 문서를 비교·취합하고 설정 충돌, 중복 소유, 링크와 변경 영향을
  검토한다.
- 게임 개요, 세계관, 시나리오, 시스템, 콘텐츠, UI와 기술 기획서를 작성한다.
- 기존 확정 문서에 대한 변경·분리·삭제안을 만든다.
- 아직 확정하지 않을 아이디어를 별도로 기록하고, 필요할 때 승인안으로
  전환하거나 보관한다.
- 기획서의 빈 부분을 찾아 사용자 확인이 필요한 사실과 창작 가능한 공백으로
  구분한다.
- 허가된 공백에 복수 대안과 추천안을 만들고 선택 결과를 추적한다.
- 화면 구현 전 시각 명세를 채우고 개발 기준 시안과 설명용 참고 이미지를
  구분한다.
- 일반 시나리오와 인게임 스크립트를 작성하고 독립 검수를 거친다.
- 승인된 변경을 적용하고 결정과 버전 이력을 남긴다.
- 승인된 기획을 Unity 개발 명세로 만들고 공식 Unity MCP 개발 agent에
  인계한 뒤 코드 변경과 컴파일 결과를 관리한다.

## 자주 확인할 자료

| 목적 | 위치 | 설명 |
|---|---|---|
| 프로젝트 선택 | [Project Registry](workspace/project_registry.md) | 등록 프로젝트와 현재 기본 프로젝트 |
| 프로젝트 현황 | [십이인연록 README](workspace/projects/chronicles-of-the-twelve-bonds/README.md) | 소개, 현재 초점, 확정 문서와 작업 기록 링크 |
| 프로젝트 기준 | [Project Brief](workspace/projects/chronicles-of-the-twelve-bonds/project_brief.md) | 장르, 핵심 경험, 현재 목표와 제약 |
| 확정 기획 문서 | [Design Index](workspace/projects/chronicles-of-the-twelve-bonds/design/README.md) | 승인 적용된 게임 자료 목록 |
| 미확정 아이디어 | [Temporary Ideas](workspace/projects/chronicles-of-the-twelve-bonds/ideas/temporary_ideas.md) | 아직 확정하지 않은 메모와 아이디어 |
| 검토할 변경안 | [Approval Queue](workspace/projects/chronicles-of-the-twelve-bonds/approvals/approval_queue.md) | 모든 승인안을 상태별로 연결한 목록 |
| 결정 기록 | [Decision Log](workspace/projects/chronicles-of-the-twelve-bonds/decisions/decision_log.md) | 승인·보류·수정·거부 결정 이력 |
| 적용 기록 | [Version History](workspace/projects/chronicles-of-the-twelve-bonds/versions/version_history.md) | 확정 문서에 실제 반영된 변경 이력 |

다른 프로젝트를 선택했다면 위 경로의
`workspace/projects/chronicles-of-the-twelve-bonds/`를 해당 프로젝트 루트로
바꾸어 확인한다.

## 확정 자료와 제안의 차이

프로젝트 자료는 성격에 따라 분리된다.

| 구분 | 의미 | 위치 |
|---|---|---|
| 확정 자료 | 승인과 적용이 끝난 현재 게임 사실 | `design/` |
| 승인안 | 확정 문서에 반영하기 전 변경 Draft | `approvals/items/` |
| 임시 아이디어 | 발전 여부를 아직 정하지 않은 메모 | `ideas/temporary_ideas.md` |
| 결정·버전 기록 | 무엇을 결정했고 실제로 무엇이 바뀌었는지에 대한 이력 | `decisions/`, `versions/` |
| 창작 규칙 | 프로젝트에서 창작할 때 따르는 행동 기준이며 게임 사실은 아님 | `agents/rules/` |

Approval Queue에 들어간 내용은 아직 게임의 확정 설정이 아니다. 사용자가
대안을 선택하거나 창작을 허가한 것도 승인과는 다르다. 최종적으로 승인한
Draft가 적용되어 `design/` 문서에 들어가야 현재 프로젝트 사실이 된다.

## 기본 작업 흐름

```text
사용자 요청
  → 대상 프로젝트와 관련 확정 자료 확인
  → 신규 작성·변경·삭제·검색 등 작업 유형 판정
  → 필요한 초안과 영향 검토
  → 개별 승인 문서를 pending으로 등록
  → 사용자 결정
  → 승인된 경우 적용 직전 원본 재확인
  → 확정 문서 반영
  → Decision Log와 Version History 기록
```

자료 검색이나 요약처럼 확정 문서를 바꾸지 않는 요청은 승인 절차 없이 바로
답할 수 있다. 확정 문서를 생성·수정·삭제하는 요청은 승인안을 거친다.

## 승인 상태와 결정 방법

| 상태 | 의미 |
|---|---|
| `pending` | 사용자의 검토와 결정을 기다리는 상태 |
| `approved` | 사용자가 승인했지만 아직 확정 문서에 적용하지 않은 상태 |
| `applied` | 확정 문서 반영과 이력 기록까지 끝난 상태 |
| `needs_reconfirmation` | 원본이나 영향 범위가 달라져 갱신과 재승인이 필요한 상태 |
| `on_hold` | 사용자가 판단이나 적용을 보류한 상태 |
| `change_requested` | 사용자가 Draft 수정을 요청한 상태 |
| `rejected` | 사용자가 제안을 거부하고 종료한 상태 |

승인할 때는 대상 ID와 행동을 명확하게 말한다.

```text
APPR-20260807-001을 승인하고 적용해줘.
```

다음 표현은 의견으로만 취급하며 승인으로 보지 않는다.

```text
괜찮네.
좋아 보여.
이 방향이 마음에 들어.
```

수정·보류·거부도 ID와 원하는 상태를 함께 말하는 것이 안전하다.

```text
APPR-20260807-001의 보상 부분을 수정해줘.
APPR-20260807-001은 보류해줘.
APPR-20260807-001을 거부해줘.
```

## 자연어 요청 예시

### 프로젝트 생성과 전환

```text
새 게임 프로젝트를 만들어줘. 제목과 폴더 이름에 필요한 정보가 부족하면 먼저
확인하고, 아직 필요하지 않은 기획 문서나 창작 규칙은 미리 만들지 마.
```

```text
이번 작업 대상을 프로젝트 목록에 있는 다른 게임으로 전환해줘.
전환한 뒤에는 이전 프로젝트의 설정이나 에셋을 섞지 마.
```

### 자료 검색과 질문

```text
십이인연록에 현재 어떤 확정 기획 문서가 있는지 역할별로 알려줘.
```

```text
십이인연록의 전투 판정 규칙을 확정 문서에서 찾아 요약해줘.
미확정 아이디어나 과거 승인 Draft는 현재 사실로 사용하지 마.
```

### 자료 취합과 충돌 검토

```text
이 프로젝트의 확정 문서에서 전투, 성장과 보상 관련 내용을 찾아 하나의 표로
취합해줘. 현재 문서는 수정하지 마.
```

```text
이 변경안이 기존 설정과 충돌하는지 검토해줘. 용어 불일치, 같은 사실의 중복
소유, 잘못된 문서 위치, 링크 단절과 영향받는 후속 문서를 함께 확인해줘.
```

### 아이디어 기록

```text
남부 지역에서 비가 올 때만 나타나는 상인을 아이디어로 기록해줘.
아직 확정 문서나 승인안으로 만들지는 마.
```

임시 아이디어는 `active` 상태로 유지하면서 내용을 보완할 수 있다. 사용자가
정식 기획 변경으로 발전시키라고 요청하면 관련 확정 자료를 다시 확인해
승인안으로 전환하고 아이디어는 `converted`로 남긴다. 더 이상 검토하지 않을
아이디어는 `archived`로 보관한다. 승인안으로 전환한 것만으로 확정되거나
적용되는 것은 아니다.

### 신규 기획서 작성

```text
십이인연록의 확정 자료를 바탕으로 남부 지역 콘텐츠 기획서 초안을 만들어줘.
관련 자료와 충돌 가능성을 확인하고 확정 문서는 바로 수정하지 마.
```

### 기존 문서 변경

```text
십이인연록의 전투 시스템에 속성 상성 규칙을 추가하는 변경안을 만들어줘.
기존 설정과 영향받는 문서를 먼저 확인하고 승인안으로 보여줘.
```

### 기획 공백과 창작 대안

```text
이 시스템 기획서에서 빠진 정보를 분류해줘.
내가 직접 정해야 하는 사실과 창작으로 채울 수 있는 공백을 구분하고,
아직 창작 대안은 만들지 마.
```

```text
GAP-SYSTEM-001과 GAP-SYSTEM-003은 창작으로 채워줘.
각각 복수 대안과 추천 이유를 보여주고 아직 확정 문서에는 적용하지 마.
```

### 시나리오와 인게임 스크립트

```text
십이인연록의 확정 자료를 바탕으로 남부 지역 메인 시나리오 초안을 작성해줘.
원안에 충실한 Draft와 더 나은 전개 제안은 분리해서 보여줘.
```

```text
확정된 프롤로그 시나리오를 기준으로 다음 챕터의 인게임 스크립트를 작성해줘.
원본과 달라진 구조와 새로 창작한 구체 내용은 구분해서 공개해줘.
```

### 문서 삭제

```text
오래된 전투 기획서 삭제를 검토해줘.
바로 삭제하지 말고 링크 단절, 설정 유실과 대체 문서를 확인한 승인안을 만들어줘.
```

### 승인 적용

```text
APPR-20260807-001을 승인하고 적용해줘.
적용 직전에 대상 원본을 다시 확인하고 달라졌다면 적용하지 마.
```

## 창작 요청에서 알아둘 점

- Codex는 프로젝트 자료만으로 확정할 수 없는 플랫폼, 엔진, 예산, 일정,
  외부 계약과 실제 에셋 ID를 임의로 사실화하지 않는다.
- 사용자에게 받아야 하는 사실은 `TBD`로 남긴다.
- 밸런스 수치는 검증과 재조정 조건이 있는 임시 가설로만 제안한다.
- 프로젝트에서 해당 분야의 창작 기준이 처음 필요하면 Codex가 먼저 설정
  계획을 보여줄 수 있다. 계획만으로 파일이 생기지는 않으며 사용자가 구현을
  요청해야 활성화된다.
- 창작 기준 구현은 창작 실행이나 확정 문서 변경을 자동으로 승인하지 않는다.
- 시나리오와 인게임 스크립트는 작성 결과를 별도 관점에서 검수한 뒤 제시한다.

<details>
<summary><strong>부록 A — 문서 역할과 소유 범위</strong></summary>

하나의 게임 사실은 하나의 상세 문서만 원본으로 소유한다. 다른 문서는 짧은
요약과 링크만 가진다.

| 역할 | 표준 위치 | 소유하는 내용 |
|---|---|---|
| 게임 개요 | `design/game/` | 게임 정체성, 핵심 경험, 상위 루프, 거시 진행과 문서 지도 |
| 세계관 | `design/world/` | 세계 구조, 정사, 인물, 세력, 장소와 오브젝트 |
| 시나리오 | `design/narrative/` | 사건 순서, Scene, 선택, 분기, 정보 공개와 엔딩 |
| 인게임 스크립트 | `design/narrative/scripts/` | 플레이어 노출 대사·지문·선택지와 씬 구현 명세 |
| 시스템 | `design/systems/` | 규칙, 상태 변화, 판정, 예외와 밸런스 |
| 콘텐츠 | `design/content/` | 지역, 퀘스트, 아이템, 적, 보상과 배치 |
| UI | `design/ui/` | 화면, 입력, 표시 정보와 UI 상태 |
| 기술 | `design/technical/` | 런타임 책임, 데이터, 저장과 연동 계약 |

게임 개요는 모든 상세 설정을 복제하는 종합 문서가 아니다. 상세 정보는 담당
문서가 소유하고 게임 개요에는 전체 경험과 문서 지도를 유지한다.

</details>

<details>
<summary><strong>부록 B — 창작 규칙과 전문 검수</strong></summary>

프로젝트별 창작 기준은 Project Creative Agent Rule(PCA)로 관리한다. PCA는
전문 작성자가 특정 프로젝트에서 어떤 자료를 보고 어느 범위까지 창작할지를
정하는 행동 규칙이다. 세계관이나 시스템의 확정 사실을 보관하지 않는다.

새 프로젝트에 모든 PCA를 미리 만들지 않는다. 시스템, 시나리오, 대본처럼
실제로 창작이 필요한 분야가 생길 때 해당 분야 규칙만 설정한다. 일치하는
규칙이 없으면 Codex는 창작을 시작하지 않고 목적, 범위, 참고 자료, 금지사항,
창작 방향과 검수 기준이 채워진 설정 계획을 먼저 제안한다.

사용자가 설정 계획을 구현해 달라고 요청하면 규칙이 활성화된다. 새 창작과
수정은 현재 활성 규칙을 사용한다. 과거 결과는 생성 당시 규칙 버전과 검수
상태를 유지하며 규칙이 바뀌었다는 이유만으로 자동 무효화하지 않는다.

전문 역할은 다음 책임으로 나뉜다.

- 일반 기획: 누락 분류, 허가된 GAP의 대안 작성과 필요 시 독립 검수
- 일반 시나리오: 원안 기반 Draft와 별도 개선안을 작성하고 독립 검수
- 인게임 스크립트: 플레이어 노출 문장과 씬 명세를 작성하고 독립 검수
- 메인 Codex: 프로젝트와 근거 확정, 사용자 권한 확인, 승인안 저장과 적용

전문 작성자와 검수자는 확정 문서나 승인 기록을 직접 수정하지 않는다.

</details>

<details>
<summary><strong>부록 C — 창작 내용의 출처 표시</strong></summary>

AI가 제안한 내용을 확정 사실과 구분하기 위해 작업 종류별 표시를 사용한다.

| 표시 | 적용 대상 |
|---|---|
| `CP-*` | 시스템·콘텐츠·UI 등 일반 기획에서 선택한 창작 결정 |
| Scenario Improvement Review | 일반 시나리오의 사건 순서·분기·동기 개선 제안 |
| `CW-*` | 인게임 스크립트의 새 대사, 지문, ID와 구체 연출 |
| `NR-*` | 인게임 스크립트가 상위 시나리오의 순서·공개·분기·동기를 바꾼 부분 |
| `TBD` | 사용자 사실이나 선행 결정이 없어 확정할 수 없는 값 |

일반 기획의 창작 공백은 먼저 GAP 목록으로 공개한다. 사용자가 정확한 GAP을
허가한 뒤에만 대안을 만들며, 저·중위험은 두 개, 고위험은 세 개를 기본으로
한다. 사용자가 선택한 안만 Draft에 들어가고 선택되지 않은 대안은 이력에만
남는다. 창작 허가와 대안 선택은 최종 승인이 아니다.

</details>

<details>
<summary><strong>부록 D — 승인 적용, 재확인과 에셋</strong></summary>

승인안은 `APPR-YYYYMMDD-NNN-<content-slug>.md` 형식의 개별 문서로 보관한다.
Approval Queue에는 모든 항목을 상태별 링크로 표시하고 각 상태 안에서 오래된
승인 ID부터 정렬한다. 상태가 바뀌어도 개별 파일 경로는 이동하지 않는다.

Git 저장소가 아니어도 승인안을 작성하고 적용할 수 있다. 변경안 작성 당시의
대상 파일·섹션 SHA-256 또는 신규 경로의 부재 상태를 기준으로 적용 직전 원본을
재확인한다. Git 커밋은 사용할 수 있을 때만 함께 기록하는 선택 정보다.

적용 직전에는 승인안 작성 당시의 기준과 현재 원본을 다시 비교한다. 내용이나
영향 범위가 달라졌으면 기존 승인을 사용하지 않고 `needs_reconfirmation`으로
전환한다. 갱신된 Draft를 사용자가 다시 명시적으로 승인해야 적용할 수 있다.

개발 기준 시안은 `assets/mockups/`, 설명·흐름·분위기 참고 이미지는
`assets/references/`로 분리한다. 검토 중에는 `approvals/`, 승인 적용 후에는
`design/` 아래의 같은 역할 폴더를 사용한다. reference 이미지는 그대로 구현할
시안이 아니다. 적용 시 파일 동일성, canonical 참조와 이력 기록을 확인한 뒤
해당 검토본만 제거한다.

문서 생성·삭제·이동이나 담당 역할 변경으로 여러 문서와 색인을 함께 바꿔야
하면 하나의 원자적인 `restructure` 승인안으로 처리한다. 일부 문서만 적용하지
않는다.

</details>

<details>
<summary><strong>부록 E — 저장소 구조와 내부 참고 자료</strong></summary>

```text
AGENTS.md                  Codex의 최상위 운영 규칙
README.md                  사람을 위한 사용 안내

.codex/agents/             공용 전문 에이전트 역할
docs/workflows/            작업별 실행 절차
docs/skills/               전문 작성·검토 품질 규칙
docs/templates/            승인안과 기획 문서 형식
tests/                     작업장 무결성 자동 검사

workspace/
  project_registry.md      프로젝트 목록과 기본 프로젝트
  projects/<project>/
    README.md              프로젝트 랜딩 페이지
    project_brief.md       프로젝트 기준과 제약
    agents/                프로젝트별 창작 규칙
    design/                확정 기획 자료
      assets/mockups/      승인 적용된 개발 기준 시안
      assets/references/   승인 적용된 설명·참고 이미지
    ideas/                 미확정 아이디어
    approvals/             승인안과 검토 에셋
      assets/mockups/      검토 중 개발 기준 시안
      assets/references/   검토 중 설명·참고 이미지
    decisions/             결정 이력
    versions/              적용 이력
    development/           Unity 개발 명세와 실행 기록
```

내부 규칙을 유지보수할 때는 다음 문서에서 시작한다.

- [AGENTS.md](AGENTS.md): 최상위 권한·승인·출처 규칙
- [Document Change Workflow](docs/workflows/document_change.md): 문서 요청 분기
- [Approval Queue Workflow](docs/workflows/approval_queue.md): 승인 상태와 적용
- [Visual Specification](docs/skills/visual_specification.md): 시각 명세와 시안 준비 판정
- [Project Creative Agent Setup](docs/workflows/project_creative_agent_setup.md): 프로젝트별 창작 규칙
- [Specialist Handoff](docs/workflows/specialist_agent_handoff.md): 전문 역할 인계
- [Unity Development](docs/workflows/unity_development.md): 공식 Unity MCP 개발 인계와 실행 결과
- [Behavior Testing](docs/workflows/behavior_testing.md): 합성 테스트 출처와 격리

`docs/dev-log/`는 과거 개발 기록이며 현재 규칙의 근거로 사용하지 않는다.

</details>

<details>
<summary><strong>부록 F — 자동 검증</strong></summary>

외부 패키지 없이 다음 명령으로 무결성 테스트를 실행한다.

```bash
python -m unittest discover -s tests -v
```

전체 검증은 문서를 수정할 때마다 자동으로 실행하지 않는다. 사용자가 전체
작업장 검증을 요청하거나 Codex가 전체 상태 확인이 필요하다고 판단한 경우에만
위 명령을 사용한다. `scripts/workspace_validation.py`는 테스트가 내부에서
가져다 쓰는 모듈이므로 사람이든 에이전트든 직접 실행하지 않는다.

자동 검사는 프로젝트 구조, 로컬 링크, 승인 ID·파일명·상태·정렬, 적용 승인과
결정·버전 이력 연결, 프로젝트별 창작 규칙의 경로·범위·버전·SHA-256, 전문
인계 계약과 합성 테스트 출처·격리를 확인한다.

에이전트의 실제 대화 행동을 시험할 때는 등록 프로젝트를 직접 사용하지 않고
먼저 Behavior Test Manifest에 대상 행동, 합성 데이터 출처와 격리 방식을
기록한다. 기본적으로 `tests/fixtures/behavior/sample-game/`을 사용하고 실제
프로젝트 구조가 꼭 필요할 때만 시스템 임시 디렉터리에 복사한다. 합성 입력은
`[TEST FIXTURE: SYNTHETIC]`으로 표시하며 실제 프로젝트 사실로 채택하지 않는다.
결과에는 데이터 출처, 실행 환경, 원본 변경 여부와 실제 프로젝트 사실로의
채택 여부를 함께 기록한다.

</details>

<details>
<summary><strong>부록 G — Unity 개발 연계</strong></summary>

Unity 개발 요청은 기획 작업과 실행 작업을 분리한다. GamePM Codex는 승인된
기획 문서에서 개발 명세를 만들고, 별도 `unity_developer`가 공식 Unity MCP로
실제 프로젝트를 조사·구현·컴파일한다. 게임 동작을 정하는 값이 부족하면
임의로 정하지 않고 사용자 확인과 필요한 기획 승인을 먼저 요청한다.

```text
승인된 기획 + 사용자 요청
  → Unity Development Spec Draft
  → 필요한 화면의 Visual Specification 작성
  → 시안 생성·사람 검토·승인 적용
  → ready Unity Development Spec
  → unity_developer + 공식 Unity MCP
  → C#·scene·prefab·component 변경
  → compile·console 확인
  → 사람 플레이 테스트
  → 성공 확인 또는 rollback
```

실제 코드는 Unity 프로젝트에만 둔다. GamePM 프로젝트의 `development/specs/`에는
개발 명세, `development/runs/`에는 변경 파일·SHA-256·컴파일 결과와 사람 검증
상태, `development/artifact_index.md`에는 등급별 산출물의 위치·소유 방식·현재
상태를 기록한다. Unity 프로젝트의 기계별 절대 경로와 복구용 코드 backup은
Git에서 제외된 `.gamepm/`에 보관한다.

로컬 Unity 프로젝트는 기계별 공통 상위 폴더 아래에서 프로젝트별 하위 폴더로
분리한다. 개발 요청에 해당하는 Unity 프로젝트가 없으면 에이전트가 확정된
Editor 버전과 template으로 유효한 프로젝트를 생성하고 Pipeline을 설치한다.
빈 폴더만 MCP 대상으로 지정하지 않으며 생성에 필요한 2D/3D·render pipeline
결정이 없으면 먼저 사용자에게 확인한다.

개발 명세에서는 기존 Scene에 통합할지, 별도·추가 Scene으로 만들지 정하고
Build Settings와 시작 Scene 변경 여부를 명시한다. 이 결정이 비어 있으면 Unity
구현을 시작하지 않는다.

현재 Unity MCP가 다른 프로젝트를 가리키면 에이전트가 프로젝트별 로컬 매핑을
읽어 Codex MCP 경로를 자동으로 변경한다. 설정이 바뀐 뒤에는 앱을 바로
재시작하지 않고 새 Codex 작업(새 채팅)에서 저장된 개발 ID를 이어간다. 새
작업에서도 MCP 대상이 갱신되지 않았을 때만 앱을 완전히 재시작한다.

컴파일 성공은 기능 검증 완료가 아니다. 플레이 감각과 실제 기능은 사용자가
Unity에서 직접 확인하고, 성공을 명시하기 전까지 상태는
`needs_human_test`로 유지한다. 공식 연결이 없거나 명세가 불완전하면 구현을
시작하지 않으며 `eval`과 `eval_file`은 사용하지 않는다.

구현 보고서는 기존 파일을 개별 SHA-256으로, 신규 대량 파일을 root manifest로
기록한다. 사람 검수에서 성공했다면 “`DEV-...-RUN-...` 성공으로 확정해줘.”라고
회신한다. 문제가 있으면 실행 ID, 문제 기능·Scene, 재현 순서와 Console 오류를
전달한다.

기본 자동 검증은 compile과 신규 Console 오류 확인에서 끝난다. Play Mode
조작, 버튼 입력과 화면 캡처는 사용자가 해당 실행에서 요청하거나 사람 검수에서
발견한 문제를 재현할 때만 선택적으로 수행한다.

화면을 포함한 production 개발은 설명용 reference 이미지가 아니라 승인 적용된
시각 명세와 `design/assets/mockups/`의 직접 대응 시안을 사용한다. 시각 명세는
화면 목적·문구·정보 위계·상태·배치·색상·해상도 대응과 사람 합격 기준을 먼저
확정하며, 준비가 끝나기 전에는 시안 이미지를 생성하지 않는다.

Unity 실행 전에는 MCP 대상·Editor·Pipeline을 먼저 확인하며, 이 preflight가
끝나기 전에는 실행 ID를 만들지 않는다. 연결 시험과 폐기 가능한 prototype을
제외한 일반 개발은 실제 적용 수준으로 다룬다. 반복·일괄 작업에 Editor 자동화가
필요하면 일회성 도구는 source snapshot과 행동 기록을 남기고 최종 compile 전에
삭제하며, 확인된 반복 import·생성·build 도구만 프로젝트에 유지한다.

개발 등급은 연결·쓰기 경로만 확인하는 `connection_test`, 기능·흐름을 확인하는
`prototype`, 승인된 기획과 실제 에셋을 통합하는 `production`으로 구분한다.
prototype 결과를 같은 명세나 실행에서 production으로 조용히 전환하지 않는다.
사용자가 정식 적용을 요청하면 승인된 기획·에셋·시각 기준을 다시 확인한 새
production 명세와 별도 실행을 만든다.

connection test와 prototype 결과물도 자동 삭제하지 않고 사용자가 정리를 요청할
때까지 보존한다. “이 프로젝트의 prototype을 전부 삭제해줘”라고 요청하면
산출물 색인과 실행 보고서의 SHA-256·후속 의존성을 확인한 뒤 안전한 항목만
정리하며 production과 변경된 공용 파일은 보호한다.

`cleanup`과 `rollback`은 목적이 다르다. cleanup은 더 이상 필요하지 않은
connection test·prototype 산출물을 명시적으로 정리하는 작업이다. rollback은
특정 구현 실행에 문제가 있을 때 해당 실행의 backup과 현재 파일 SHA-256을
대조해 변경을 복구하는 작업이며 production에도 사용할 수 있다. 공용 파일이
후속 실행에서 바뀌었거나 다른 기능이 사용 중이면 임의로 되돌리지 않고
차단된 대상을 보고한다.

```text
DEV-20260817-002-RUN-001의 변경을 rollback해줘.
현재 파일 해시와 후속 실행 의존성을 먼저 확인해줘.
```

- [Unity Development Workflow](docs/workflows/unity_development.md): 개발 인계,
  권한, 구현, 검증과 rollback 규칙
- [Unity Development Spec](docs/templates/unity_development_spec.md): 개발 명세
  형식
- [Unity Implementation Report](docs/templates/unity_implementation_report.md):
  실행 결과 형식
- [Unity Artifact Index](docs/templates/unity_artifact_index.md): 등급별 산출물
  색인 형식

</details>
