# Document Structure Workflow

## Purpose

확정 정보의 canonical owner, 역할별 표준 경로와 여러 owner를 함께 바꾸는
`restructure` 원칙을 정한다. 작성·창작·검수·승인 절차는 소유하지 않는다.

## Canonical Document Roles

| 역할 | 타입 | 표준 경로 | 한 줄 책임 |
|---|---|---|---|
| 게임 개요 | `game_overview` | `design/game/` | 게임 정체성, 핵심 경험, 상위 루프·진행과 문서 지도 |
| 세계관 | `world_setting` | `design/world/` | 세계 구조, 역사, 문화, 정사, 인물·세력·장소·오브젝트 |
| 시나리오 | `scenario` | `design/narrative/` | 사건, Scene, 진입·종료, 선택·분기, 공개와 엔딩 |
| 인게임 스크립트 | `scenario` | `design/narrative/scripts/` | 승인 범위의 플레이어 문장, 선택지와 Scene 구현 연결 |
| 시스템 | `system` | `design/systems/` | 플레이 규칙, 입력·출력, 상태 변화, 판정, 밸런스와 예외 |
| 콘텐츠 | `content` | `design/content/` | 지역·노드·퀘스트·아이템·적·보상의 구체 목록과 배치 |
| UI | `ui` | `design/ui/` | 화면, 입력, 표시 정보, 상태와 UI 예외 |
| 기술 | `technical` | `design/technical/` | 런타임 책임, 데이터·저장·연동 계약과 기술 예외 |

프로젝트 창작 규칙은 `agents/rules/`의 행동 설정이며 게임 사실의 canonical
owner가 아니다.

## Ownership Rules

- 하나의 상세 사실은 하나의 owner만 가진다. 다른 문서는 짧은 요약과
  상대경로 링크만 둔다.
- NPC의 정사 설정은 세계관, 특정 사건에서의 행동은 시나리오가 소유한다.
- 퀘스트·아이템·리소스 목록과 배치는 콘텐츠가 소유한다.
- 상위 시나리오는 사건·분기 구조, 인게임 스크립트는 승인된 범위의 표현과
  Scene 연결을 소유한다.
- 세계관 정사나 시스템 규칙을 시나리오·스크립트에서 대신 확정하지 않는다.
- `game_overview`는 상세 저장소가 아니다. 핵심 경험, 디자인 원칙, 상위 루프,
  거시 진행, 목표 범위와 Document Map만 유지한다.

## Classification

1. 사용자 입력을 사실·사건·규칙·콘텐츠·표현·기술 책임 단위로 나눈다.
2. 각 단위를 표의 한 owner에 배정한다.
3. 관련 정본을 검색해 새 문서, 기존 문서, restructure 후보를 판정한다.
4. owner 문서가 없으면 미래 표준 경로를 정하고 상위 문서에는 승인 후 사용할
   요약과 링크만 제안한다.

## Restructure Principles

다음 중 하나면 단일 `restructure` 변경 범위로 다룬다.

- 한 문서에 둘 이상의 canonical role이 섞여 분리·이동이 필요하다.
- 한 변경 때문에 여러 owner의 생성·수정·삭제가 동시에 필요하다.
- 인게임 스크립트의 구조 변경 때문에 상위 시나리오도 함께 바뀐다.
- 문서 생성·삭제·이동·역할·한 줄 책임 변경 때문에 프로젝트 README,
  `design/README.md` 또는 game overview 링크를 함께 고쳐야 한다.

restructure에는 모든 대상의 `create | update | delete`, 최종 owner, 내용 이동,
링크 갱신을 포함한다. 일부 대상만 먼저 적용하지 않는다. 다른 owner의 선행
결정이 아직 적용되지 않았다면 그 부분은 dependency로 분리한다.

## Link Rules

- 프로젝트 README와 `design/README.md`는 존재하는 확정 문서만 링크한다.
- game overview는 모든 현재 확정 상세 문서로 가는 상대 링크를 둔다.
- 상세 문서는 상위 game overview로 돌아가는 링크를 둔다.
- owner나 경로가 바뀌면 관련 색인·요약·링크를 같은 restructure 범위에 둔다.

## New Project Rule

새 프로젝트 README에는 소개, 현재 초점, 작업 기록 링크와 확정 세부 문서가
없음을 기록한다. 빈 확정 기획서를 미리 만들지 않는다.
