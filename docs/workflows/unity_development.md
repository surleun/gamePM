# Unity Development Workflow

## Purpose

승인된 게임 기획을 Unity 개발 명세로 변환하고, 별도 `unity_developer` agent가
공식 Unity MCP를 통해 실제 Unity 프로젝트를 구현·컴파일한 뒤 메인 Codex가
변경 결과를 기록하도록 한다. 이 문서는 개발 인계, 권한, 구현, 검증, 반환과
rollback의 유일한 상세 원본이다.

## Role Boundary

- 메인 Codex는 대상 게임 프로젝트를 확정하고, 승인 적용된 `design/`과 현재
  사용자 요청을 바탕으로 개발 명세를 작성하며, Unity 개발 결과를 저장한다.
- `unity_developer`는 완성된 명세를 구현하는 실행 agent다. 지정된 Unity
  프로젝트와 해당 실행의 로컬 backup만 수정하며 GamePM의 `design/`,
  `approvals/`, `ideas/`, `decisions/`, `versions/`를 수정하지 않는다.
- 공식 Unity MCP는 실행 중인 Editor의 상태·장면·컴포넌트·로그·명령 표면을
  제공하고 작업 결과를 반환한다. 코드 판단과 C# 내용 작성은 연결된
  `unity_developer`가 담당한다.
- 메인 Codex와 `unity_developer`는 게임 기획 결정을 새로 확정하거나 승인된
  기획을 구현 편의상 바꾸지 않는다.

## Project And Local Unity Resolution

1. `docs/workflows/project_workspace.md`로 GamePM 프로젝트를 확정한다.
2. 기계별 Unity 프로젝트 공통 상위 경로와 프로젝트별 절대 경로는 추적 문서에
   쓰지 않고 Git에서 제외된 `.gamepm/unity-projects.json`에 저장한다.
   `projects_root` 바로 아래에 GamePM 프로젝트별 Unity 폴더를 하나씩 분리한다.
   새 매핑의 기본 하위 폴더명은 GamePM `project_id`다. 이미 등록된 명시적
   하위 폴더가 공통 상위 경로 안의 유효한 Unity 프로젝트라면 그 매핑을
   보존한다.
3. 매핑된 Unity 루트가 없으면 메인 Codex가 빈 폴더만 만들고 연결하지 않는다.
   승인된 기획·완성 중인 개발 명세와 현재 사용자 입력에서 Unity Editor 버전,
   실제 template ID, 대상 플랫폼을 확정하고 다음 순서로 유효한 Unity 프로젝트를
   만든다.
   - 공통 상위 폴더가 없으면 먼저 생성한다.
   - `unity templates list`로 해당 Editor의 실제 template ID를 확인한다.
   - `unity projects create "<project_id>" --path "<projects_root>"
     --editor-version <confirmed_version> --template <confirmed_template>`로
     `Assets/`, `Packages/manifest.json`, `ProjectSettings/`를 가진 하위 프로젝트를
     생성한다.
   - 사용자가 별도로 요청하지 않은 Git·원격 저장소·Unity Version Control은
     만들거나 강요하지 않는다.
   - 생성에 필요한 Editor 버전·2D/3D·render pipeline·template을 근거에서
     확정할 수 없으면 임의의 빈 폴더나 기본 project를 만들지 않고
     `blocked_missing_development_decision`으로 사용자에게 확인한다.
4. 생성했거나 기존에 매핑된 Unity 루트에 `Assets/`,
   `Packages/manifest.json`, `ProjectSettings/`가 모두 있는지 확인한다. 존재하는
   대상 폴더가 이 구조를 갖추지 못했으면 덮어쓰기·삭제·중첩 생성을 하지 않고
   `blocked_invalid_unity_project`로 중단한다.
5. 유효한 새 프로젝트에는 `unity pipeline install --project-path
   "<unity_project_root>"`로 `com.unity.pipeline`을 설치하고 Editor를 연다.
   프로젝트 생성과 필수 구조·Pipeline을 확인한 뒤에만 프로젝트별 매핑을
   저장한다.
6. 저장소 밖의 프로젝트는 구현 전에 해당 경로가 Codex의 writable root로
   열려 있거나 사용자가 정확한 경로의 쓰기 권한을 승인해야 한다. 여러 기존
   후보가 있고 매핑이 없으면 임의로 선택하지 않고 사용자에게 확인한다.

`.gamepm/unity-projects.json`의 형태는 다음과 같다.

```json
{
  "projects_root": "machine-local common parent absolute path",
  "projects": {
    "PROJECT-ID": {
      "unity_project_ref": "stable machine-local reference",
      "unity_project_root": "machine-local child project absolute path"
    }
  }
}
```

`projects_root` 자체는 Unity 프로젝트가 아니며 MCP 대상으로 사용하지 않는다.
MCP에는 `Assets/`, `Packages/manifest.json`, `ProjectSettings/`를 가진 정확한
하위 `unity_project_root`만 전달한다.

## MCP Target Alignment And Preflight

메인 Codex는 Unity 개발 명세를 구현에 넘기기 전에 현재 작업에 노출된 공식
Unity MCP 대상과 선택된 `unity_project_root`를 일치시킨다.

1. 현재 Unity MCP tool namespace에서 `editor_status`를 읽어 실제 Editor의
   프로젝트 경로를 확인한다. 설정 파일의 `enabled`만으로 대상 일치를
   주장하지 않는다.
2. 실제 MCP 프로젝트 경로가 선택된 `unity_project_root`와 정확히 같으면 현재
   작업에서 명세 작성과 `unity_developer` 인계를 계속한다.
3. MCP가 다른 프로젝트에 연결되어 있거나 현재 tool namespace에 Unity 도구가
   없으면 메인 Codex가 현재 사용자 요청, 대상 프로젝트·Unity project ref와
   미결정을 `development/specs/`의 Draft 또는 ready 명세에 먼저 저장하고 다음
   명령으로 Codex의 Unity MCP 대상을 자동 전환한다.

   ```text
   unity mcp configure codex --project-path "<unity_project_root>" --yes
   codex mcp get unity --json
   ```

   두 번째 명령의 `args`에 정확한 `--project-path`와 대상 경로가 있는지
   확인한다. 경로 전환 뒤 현재 작업에 이미 노출된 이전 Unity MCP 도구로는
   어떤 구현 mutation도 수행하지 않는다.
4. 설정 전환이 끝나면 사용자에게 Codex 앱을 종료하라고 요구하지 않고 먼저
   **새 Codex 작업(새 채팅)**을 열어 저장된 개발 ID를 계속하라고 안내한다.
   새 작업은 시작 시 갱신된 MCP 설정과 도구 목록을 다시 읽는다.
5. 새 작업에서는 Unity MCP tool namespace 존재 여부와 `editor_status`의 정확한
   프로젝트 경로를 다시 확인한다. 둘 다 일치해야 `unity_developer`를 호출한다.
   새 작업에서도 이전 대상이 남아 있을 때만 Codex 앱 완전 재시작을 안내한다.
6. 설정 쓰기 실패, 대상 Editor 미실행, Pipeline 미연결 또는 새 작업의 경로
   불일치는 `blocked_unity_mcp_unavailable`이다. CLI의 live mutation이나 다른
   MCP로 우회하지 않는다.

이 확인은 implementation run을 만들기 전의 preflight다. tool namespace,
Editor `ready`, 정확한 프로젝트 경로와 Pipeline 연결이 모두 확인되기 전에는
실행 ID와 backup root를 발급하거나 `unity_developer`를 호출하지 않는다.
mutation 전 preflight 실패는 개발 명세만 `blocked`로 유지하고 실행 보고서를
만들지 않는다. 실행이 시작된 뒤 연결이 끊기거나 실패한 경우에만 해당 RUN의
결과를 기록한다.

## Development Records

첫 Unity 개발 요청이 생길 때만 다음 구조를 만든다.

```text
workspace/projects/<project_slug>/development/
  artifact_index.md
  specs/   DEV-YYYYMMDD-NNN-<content-slug>.md
  runs/    DEV-YYYYMMDD-NNN-RUN-NNN.md

.gamepm/unity-backups/<project_id>/<development_id>/<run_id>/
```

- 명세는 `docs/templates/unity_development_spec.md`, 실행 결과는
  `docs/templates/unity_implementation_report.md`, 산출물 색인은
  `docs/templates/unity_artifact_index.md` 형식을 사용한다.
- 실제 C#·Unity asset의 canonical 사본은 Unity 프로젝트에만 둔다. 명세나
  실행 보고서에 전체 코드 복사본을 저장하지 않는다.
- 실행 보고서에는 변경 파일, 작업 종류, 변경 전·후 SHA-256, 요약, MCP 작업,
  개발 등급 준수 결과, 컴파일 결과와 사람 검증 상태만 기록한다.
- Git은 선택 사항이다. Git이 없는 Unity 프로젝트도 파일 backup과 SHA-256을
  사용해 구현하고 되돌릴 수 있다.
- 실행 ID는 MCP preflight와 ready 명세가 모두 확인된 뒤 발급한다. 연결 설정과
  명세 준비 중의 실패는 RUN을 소비하지 않는다.
- 산출물 색인은 새 등급 계약으로 첫 실행을 기록할 때 생성한다. 기존 개발
  명세·실행 보고서는 수정하거나 소급 등록하지 않는다.

## Development Level And Artifact Contract

- 개발 등급은 `connection_test | prototype | production` 중 하나다. 사용자가
  연결 시험을 명시하면 `connection_test`, 폐기 가능한 임시 기능을 명시하면
  `prototype`, 그 밖의 실제 개발 요청은 `production`을 기본값으로 사용한다.
- 작업 유형은 `implement | cleanup` 중 하나다. `cleanup`은 기존
  `connection_test` 또는 `prototype` 산출물의 명시적 정리 요청에만 사용하며
  `production` 정리에는 사용할 수 없다.
- 명세에는 등급 선정 근거, 같은 값의 산출물 분류, 통합 방식, 전용 경로, 공용
  파일 변경, placeholder, 보존 정책, 정리 그룹, 승격 조건과 등급별 완료 조건을
  모두 기록한다. 해당 없는 값도 비워 두지 않고 `없음 | 해당 없음`으로 적는다.
- 모든 등급의 산출물은 `preserve_until_explicit_cleanup`으로 보존하며 background
  삭제를 수행하지 않는다. 정리 그룹은 `connection_test`, `prototype`, production의
  `none`만 허용한다.
- `connection_test`는 연결·작성·compile 경로 확인이 목적이다. 기본적으로 별도
  Unity 프로젝트나 `Assets/GamePM/ConnectionTests/<development_id>/` 같은 전용
  경로에 격리하고 임시 표현을 허용한다.
- `prototype`은 기능·흐름 검증용이다. 기본적으로
  `Assets/GamePM/Prototypes/<development_id>/` 같은 전용 경로에 격리하며
  placeholder 목록·허용 범위·폐기 시점과 새 production 명세로 승격할 조건을
  명시한다.
- `production`은 실제 통합 대상, 승인된 게임 동작, 필요한 실제 에셋과 사람
  합격 기준이 채워져야 한다. prototype 전용 경로나 미승인 placeholder를
  사용하지 않는다.
- prototype 산출물을 같은 명세나 실행에서 production으로 조용히 전환하지
  않는다. 사용자 요청과 근거를 반영한 새 production 명세·실행을 만들고, 이전
  산출물은 색인에서 `promoted`로 연결한다.
- 화면을 포함한 `production` 작업은 `docs/skills/visual_specification.md`의
  절차를 거쳐 승인 적용된 시각 명세와 직접 대응하는
  `design/assets/mockups/` 시안이 필요하다. `design/assets/references/` 이미지는
  설명·흐름·분위기 참고일 뿐 배치·스타일·완성도 근거로 사용하지 않는다.
- `prototype`은 placeholder와 폐기 조건을 명세한 경우에만 reference 이미지를
  참고할 수 있으며 production 시각 품질을 주장하지 않는다.
- 기술 preflight는 해당 구현에 직접 필요한 package와 package 기본 resource,
  input system, render pipeline, 시스템 의존성만 확인한다. 전체 프로젝트를
  포괄적으로 조사하거나 이 단계에서 mutation하지 않는다.
- 누락된 기술 의존성은 설치·import 방법과 영향 경로를 명세의 구현 단계로
  올린다. 게임 동작을 바꾸는 선택이 필요하면
  `blocked_missing_development_decision`으로 중단한다.
- scene 통합 방식은 `existing_scene | standalone_scene | additive_scene |
  build_entry | not_applicable` 중 하나로 정하고, Build Settings 변경 여부와
  시작 scene 순서를 별도로 적는다. 근거 없이 기존 시작 scene을 제거하거나
  순서를 바꾸지 않는다.

## Artifact Index And Explicit Cleanup

`development/artifact_index.md`는 Unity 산출물의 운영 색인이다. 실제 코드와
asset의 정본이나 실행 보고서의 파일 manifest를 복제하지 않는다. 메인 Codex만
다음 필드를 기록·갱신한다.

- 실행 ID, 작업 유형, 개발 등급과 정리 그룹
- Unity project ref와 `isolated | shared` 소유 방식
- 구현 보고서와 그 안의 정확한 파일·subtree manifest
- `active | promoted | removed | blocked` 상태와 정리 실행 링크

새 구현 보고서가 등급 계약 `pass`이고 메인 Codex 대조를 통과하면 색인에
등록한다. source 실행 보고서는 이후 정리에서도 수정하지 않는다. 사람의 성공
확인 여부와 산출물 보존 여부는 별개이며, `needs_human_test` 상태도 `active`로
등록할 수 있다.

사용자가 “이 프로젝트의 prototype을 전부 삭제해줘”처럼 명시적으로 요청한
경우에만 다음 순서로 정리한다.

1. GamePM 프로젝트와 정리 그룹을 확정하고, 색인의 해당 그룹 `active` 항목만
   후보로 선택한다. 폴더명 검색만으로 삭제 대상을 정하지 않는다.
2. 새 Unity Development Spec을 `작업 유형: cleanup`, 대상 개발 등급으로 만들고
   후보 실행 ID와 원본 구현 보고서를 열거한다. `production` 항목은 제외한다.
3. 원본 보고서의 파일·subtree manifest, 현재 SHA-256, backup, 후속 실행과
   production 의존성을 재확인한다.
4. `isolated` 전용 파일·폴더는 현재 해시가 기록과 일치할 때 제거한다. 기존 공용
   파일은 현재 해시가 원본 실행의 변경 후 해시와 같고 후속 실행이 의존하지 않을
   때만 해당 backup으로 복원한다.
5. 해시 불일치, 후속 변경, production 사용 또는 소유 범위 불명확 항목은
   삭제하지 않고 색인에 `blocked`와 이유를 기록한다. 안전 차단을 우회하려고
   범위를 넓히지 않는다.
6. 허용된 정리는 `unity_developer`가 공식 Unity MCP로 수행한다. 정리 대상도
   변경 전에 새 cleanup 실행 backup과 SHA-256을 남긴다.
7. refresh·compile·신규 Console error 0과 Editor 정상 상태를 확인한 별도 cleanup
   실행 보고서를 저장한다. 원본 보고서는 보존하고 색인만 `removed | blocked`와
   cleanup 실행 링크로 갱신한다.

정리 후에도 runtime 기능 성공은 사람이 확인한다. 후보가 없으면 Unity mutation
없이 “정리 대상 없음”을 반환하며, 실행 ID를 만들지 않는다.

특정 RUN을 backup으로 되돌리는 기존 rollback은 종류별 산출물 일괄 정리가
아니다. 원래 `implement` 명세의 Recovery로 처리하고 production에도 사용할 수
있다. `cleanup`은 artifact index의 connection test·prototype 그룹 정리에만 쓴다.

## Specification Gate

메인 Codex는 구현 전에 완성된 Unity Development Spec을 만든다.

1. 근거는 승인 적용된 canonical `design/`, 현재 사용자 요청과 대상 Unity
   프로젝트의 실제 기술 상태로 제한한다.
2. 미승인 아이디어·승인 Draft·다른 프로젝트 자료를 구현 근거로 사용하지
   않는다. 사용자가 미승인 제안의 prototype을 명시적으로 요청하면 정본
   구현과 분리된 범위·경로·폐기 조건을 먼저 확정한다.
3. 입력, 수치, 규칙, 성공·실패 조건, 저장 데이터와 플레이어 노출 동작처럼
   게임 경험을 바꾸는 누락은 `design_decision_gap`이다. 임의로 채우지 않고
   `blocked_missing_development_decision`으로 중단해 사용자 확인과 필요한
   기획 승인 적용을 먼저 진행한다.
4. 클래스명, 파일 분리, private helper, 기존 패턴에 맞춘 namespace처럼 게임
   경험을 바꾸지 않는 가역적 선택은 `implementation_choice`다.
   `unity_developer`가 현재 코드 구조에 맞춰 선택하고 실행 보고서에 공개할 수
   있다.
5. 엔진 버전·패키지·입력 시스템·렌더 파이프라인·기존 이동 방식·대상
   scene/prefab처럼 구현 경로를 바꾸는 기술 사실은 추정하지 않고 Unity
   프로젝트에서 확인한다.
6. 범위, 제외 대상, 대상 파일·오브젝트, 의존성, 금지 조건, 사람 검증 절차와
   rollback 기준이 채워져야 상태를 `ready`로 바꾼다.
7. `자동 Play Mode·입력·화면 검증`의 기본값은 `아니요`다. 사용자가 해당
   실행에서 자동 검증을 명시적으로 요청한 경우에만 `예`로 두고, 정확한 검증
   범위와 결과물 보존 방식을 명세에 적는다.
8. 작업 유형, 개발 등급, 등급 선정 근거와 `Development Level Contract`, 기술
   preflight 결과, scene 통합 방식과 Build Settings 변경이 모두 명세에 있어야
   한다. 산출물 분류와 등급은 같아야 하고, 보존 정책·정리 그룹은 위 등급 계약과
   일치해야 한다. 해당 없는 항목은 비워 두지 않고 `해당 없음`으로 표시한다.
9. Editor 도구의 반복 사용이 이미 확인됐다면 재사용 대상과 유지 경로를
   명세에 적는다. 아직 필요 여부를 모르면 추측해서 도구를 계획하지 않는다.
10. 화면을 포함한 `production`은 적용된 Visual Specification 경로·SHA-256과
    `design/assets/mockups/` 시안 경로·SHA-256이 모두 있어야 한다. reference
    이미지만 있으면 `blocked_missing_development_decision`으로 중단한다.
11. `prototype`은 placeholder 목록·허용·교체·폐기 조건과 production 승격
    조건이 있어야 한다. `production` 명세에 prototype 전용 경로나 남아 있는
    placeholder가 있으면 `ready`로 바꾸지 않는다.
12. `cleanup`은 대상 artifact index 항목, 원본 구현 보고서, 현재 해시·후속
    의존성 재확인과 허용·차단 범위가 있어야 한다. `production` 정리나 색인 밖
    대상을 포함하면 `blocked_missing_development_handoff`로 중단한다.

작성 중인 `draft | blocked` 명세는 실행 ID가 `preflight 전 미발급`인 동안
미완성 필드를 허용한다. 실제 RUN ID가 있으면 preflight는 반드시 `pass`여야
한다. 새 RUN 보고서는 같은 개발 ID의 명세와 통과한 preflight가 없으면 작업장
무결성 검사에서 차단한다.

## Required Invocation

메인 Codex는 다음 방식으로 새 실행을 시작한다.

```text
agent_type: unity_developer
fork_turns: "none"
message: <완성된 Unity Development Spec과 실행 식별값>
```

- 프로젝트, Unity project ref, 개발 ID, 실행 ID, 명세 경로, 구현 범위, 금지
  조건과 기대 반환 형식이 없거나 충돌하면
  `blocked_missing_development_handoff`로 중단한다.
- `model`과 `reasoning_effort`를 임의로 덮어쓰지 않는다.
- `unity_developer` 대신 일반 agent나 서드파티 Unity MCP로 조용히 대체하지
  않는다.
- 공식 Unity MCP가 설치·연결되어 있지 않거나 대상 Editor를 식별할 수 없으면
  `blocked_unity_mcp_unavailable`을 반환한다. 이 상태에서 구현을 시작하지
  않는다.
- 인계에는 추적 문서의 Unity project ref와 별도로 실행 시 확인한 정확한 로컬
  Unity 프로젝트 루트가 있어야 한다. `unity_developer`는 첫 mutation 전에
  MCP `editor_status` 경로가 이 루트와 같은지 검증한다.

## Editor Tool Decision And Lifecycle

Editor 도구는 MCP 명령을 우회하는 수단이 아니라, 공식 MCP로 생성·compile·실행하는
Unity Editor C# 자동화다. 다음 순서로 필요성을 판단한다.

1. 공식 MCP에 동일 목적의 전용 명령이 있으면 직접 사용한다.
2. 소수 GameObject·component·property의 독립적인 변경이면 MCP를 직접 사용한다.
3. 대량 반복, 데이터 parsing·변환, 복잡한 serialized reference 연결, 여러 변경의
   일괄 성공이 필요하거나 MCP에 해당 고수준 API가 없을 때만 Editor 도구를
   고려한다.
4. package 설치·scene 저장처럼 이미 지원되는 단일 작업을 감싸거나, 안전장치
   우회, 범위 밖 수정, 미확정 게임 결정을 넣기 위해 Editor 도구를 만들지 않는다.
5. 경계가 애매하면 MCP 직접 사용을 기본값으로 한다.

도구를 만들기로 했다면 생성 전에 다음 중 하나로 분류한다.

- `temporary_tool`: 현재 RUN의 일회성 authoring·import·migration 도구다. 확정된
  두 번째 사용처가 없거나 판단 근거가 없으면 이 분류를 사용한다.
- `retained_editor_tool`: 같은 데이터 형식의 반복 import, 여러 scene·level의
  재생성, 매 build 실행 또는 사용자가 명시한 프로젝트 도구처럼 확인된 재사용
  대상이 있을 때만 사용한다. “나중에 쓸 수도 있음”은 근거가 아니다.

임시 도구는 `Assets/Editor/GamePMTemp/<run_id>/` 안에만 만들고, 재사용 도구는
`Assets/Editor/<feature>/`의 프로젝트 정식 경로에 둔다. 임시 도구 실행 후에는
결과 scene·prefab·asset을 저장한 다음 source와 meta를 아래 실행 backup에
복사하고 SHA-256을 기록한다.

```text
.gamepm/unity-backups/<project_id>/<development_id>/<run_id>/temporary-tools/
  <Unity 프로젝트 상대 경로>
```

snapshot 뒤에는 임시 도구와 빈 run 전용 폴더를 공식 MCP로 제거하고 asset
refresh를 수행한다. 최종 compile은 이 삭제 이후에 실행한다. 안전하게 정리하지
못한 임시 경로가 있으면 `needs_human_test`로 넘기지 않고 `blocked` 상태와 잔존
경로를 보고한다. 재사용 도구는 구체적인 다음 사용처, 입력, 실행 방법과 유지
이유를 보고서에 남긴다.

삭제한 임시 source 전체를 실행 보고서에 복제하지 않는다. 보고서에는 입력,
주요 Unity API, 수행 행동, 생성·수정 대상, 실행 결과, 최종 삭제 여부와 source
snapshot 경로·SHA를 사람이 이해할 수 있게 기록한다. 비밀값과 인증정보는
source, snapshot, 보고서 어디에도 저장하지 않는다.

## Implementation Procedure

`unity_developer`는 다음 순서만 따른다.

1. 인계 필드와 GamePM 프로젝트·Unity project ref, 작업 유형·개발 등급·산출물
   계약의 일관성을 검증한다.
2. 공식 Unity MCP로 대상 Editor와 명세에 직접 관련된 Unity 버전, package,
   scene·component와 console 기준 상태만 확인한다.
3. 명세에 지정된 기존 코드와 직접 의존 코드만 읽고 현재 구조와 확장 지점을
   찾는다. Unity API가 불확실하면 공식 도구가 제공하는 현재 API·명령 정보를
   우선한다.
4. 변경·삭제할 기존 파일을 실행 backup에 복사하고 SHA-256을 기록한다. 새
   파일은 `new_file`로 기록해 rollback 때 제거할 수 있게 한다.
5. `implement`는 명세 범위에서 C#·scene·prefab·component를 구현한다. `cleanup`은
   명세에 확정된 전용 파일 제거와 검증된 공용 파일 backup 복원만 수행한다.
   Editor 자동화가 필요하면 위 판단 기준과 수명주기를 먼저 적용한다. Unity
   프로젝트 밖의 파일, GamePM 정본과 사용자 비밀값을 수정하지 않는다.
6. 임시 Editor 도구를 사용했다면 결과를 저장하고 source·meta snapshot과 SHA를
   남긴 뒤 도구를 제거한다. 재사용 도구는 확인된 재사용 근거와 정식 경로를
   기록한다.
7. 공식 Unity MCP로 asset refresh와 최종 script compile을 요청하고 새 compiler
   error와 console error를 확인한다. `eval`과 `eval_file`은 사용하지 않는다.
8. 명세 범위 안의 명확한 컴파일 오류만 수정한다. 세 번의 수정 주기 뒤에도
   실패하면 범위를 넓히지 않고 `failed_compile`로 반환한다.
9. compile 성공, 새 compiler error 0, 새 Console error 0과 Editor 정상 상태를
   확인하면 기본 자동 검증을 종료한다. 자동 검증이 `아니요`인 실행에서는
   Play Mode 진입, 입력 실행, 상태 assertion, 해상도별 캡처, 이미지 분석과
   검증 전용 Editor code 생성을 수행하지 않는다.
10. 자동 기능 검증은 명세에 사용자의 명시적 요청이 기록된 경우, 또는 사람이
   보고한 문제를 재현·진단하는 새 실행에서만 범위 한정해 수행한다. 수행한
   Play Mode·입력·화면 검증과 결과물 보존 여부를 실행 보고서에 공개한다.
11. 요청 등급과 실제 적용 등급, 계약 `pass | blocked`, 산출물 소유 범위·상태,
   placeholder, 보존·정리 근거와 사람 확인 대기를 포함한 실행 보고서를
   반환한다. Unity 프로젝트의 문서나 GamePM 기록은 직접 저장하지 않는다.

## Return And Main-Agent Check

`unity_developer` 반환에는 다음이 있어야 한다.

- 개발 ID, 실행 ID, Unity project ref와 사용한 공식 MCP 연결
- 읽은 근거와 실제 확인한 Unity 상태
- 변경·생성·삭제 파일과 scene/prefab/component 작업
- 파일별 변경 전·후 SHA-256과 backup 위치
- 신규 subtree의 root·파일 수·정렬된 manifest SHA와 rollback root
- agent가 선택한 `implementation_choice`와 이유
- Editor 도구의 분류·필요 근거·주요 행동·최종 처리와 snapshot
- compile 결과, 실행 전부터 있던 오류와 새 오류의 구분
- 자동 Play Mode·입력·화면 검증의 수행 여부와 근거
- 작업 유형, 개발 등급 계약 준수 결과, 산출물 분류·정리 그룹·소유 방식과 상태
- 전용 소유 파일·폴더, 기존 공용 파일 변경, 남은 placeholder와 보존·정리 근거
- 미해결 항목, 사람 플레이 테스트 절차와 rollback 가능 여부

메인 Codex는 명세 범위, 대상 경로, 금지 조건, 보고서의 SHA-256·backup·compile
결과를 대조한다. 정상적인 완전한 보고를 받은 뒤 hierarchy·component·입력·화면
상태를 Unity MCP로 반복 조회하지 않는다. 보고가 누락되거나 서로 모순되거나
새 오류를 주장할 때만 필요한 항목을 범위 한정해 다시 확인한다. 대조가 끝나면
실행 보고서를 `development/runs/`에 저장하고, 새 등급 계약을 사용한 실행만
`development/artifact_index.md`에 등록하거나 cleanup 결과로 갱신한다. 기존 실행
보고서는 다시 쓰지 않는다.

메인 Codex도 명세에 명시된 요청이나 사람의 문제 보고가 없으면 별도의
Play Mode·입력·화면 검증을 시작하지 않는다. 자동 검증을 하지 않은 runtime
동작과 화면은 실패로 간주하지 않고 사람 확인 항목으로 인계한다.

컴파일 성공은 기능 성공이 아니다. 메인 Codex와 `unity_developer`는 사람의
플레이 확인 전 `accepted`, `검증 완료` 또는 같은 의미의 표현을 사용하지
않는다. 정상 컴파일 뒤 기본 상태는 `needs_human_test`다.

## Human Test, Acceptance And Rollback

- 사용자는 실행 보고서의 절차로 실제 게임을 플레이하고 성공 또는 수정
  요청을 전달한다.
- runtime 오류, 버튼·입력 연결, 화면 배치, 조작감과 미감은 기본적으로 이
  사람 플레이 테스트에서 확인한다.
- 사용자가 해당 개발 ID·실행 ID의 성공을 명시하면 상태를 `accepted`로
  기록한다. 애매한 긍정 표현은 성공 판정으로 사용하지 않는다.
- 실행 보고서는 사용자가 복사해 돌려줄 수 있는 실행 ID, `성공 | 문제 있음`,
  문제 scene·기능, 재현 순서, Console 오류와 첨부 화면 필드를 제공한다. 성공
  안내에는 “`DEV-...-RUN-...` 성공으로 확정해줘.” 형식을 함께 제시한다.
- 사용자가 “처음으로 돌려줘”라고 요청하면 대상 개발·실행을 확정한 뒤 기존
  파일을 backup에서 복원하고 해당 실행의 새 파일을 제거한다. 여러 실행 중
  대상을 식별할 수 없으면 먼저 ID를 확인한다.
- rollback도 `unity_developer`가 수행하고 공식 Unity MCP로 refresh·compile한
  결과를 새 실행 보고서에 기록한다.
- `accepted` backup은 성공 확인일로부터 30일 동안 보존한다. 30일이 지난
  backup은 사용자가 cleanup을 요청하거나 후속 유지보수에서 정확한 대상을
  확인한 경우에만 삭제하며, 자동 background 삭제를 가정하지 않는다.

## Output

- Unity Development Spec 또는 차단 상태
- `unity_developer` 호출용 완성 인계
- Unity Implementation Report
- 현재 상태: `draft | blocked | ready | implementing | failed_compile |
  needs_human_test | accepted | rolled_back`
- 사용자가 해야 할 다음 행동
