from pathlib import Path
from hashlib import sha256
import shutil
from tempfile import TemporaryDirectory, gettempdir
import unittest

from scripts.workspace_validation import (
    ProjectRecord,
    ProvenanceRecord,
    SPECIALIST_AGENT_TYPES,
    format_issues,
    navigation_markdown_files,
    parse_approval_records,
    parse_project_creative_agent_rule,
    source_reconfirmation_sha256,
    validate_applied_approval_references,
    validate_asset_role_directories,
    validate_approval_records,
    validate_behavior_test_manifest,
    validate_duplicate_ai_rule_lines,
    validate_markdown_links,
    validate_project_creative_agents,
    validate_project_registry,
    validate_project_structure,
    validate_provenance_record,
    validate_unity_artifact_index,
    validate_unity_development_run_links,
    validate_unity_development_spec,
    validate_unity_implementation_report,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = REPO_ROOT / "workspace/project_registry.md"


class WorkspaceFixture:
    """각 테스트가 독립적으로 바꿀 수 있는 최소 작업장."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.project_id = "sample-project"
        self.project_relative_root = f"workspace/projects/{self.project_id}/"
        self.project_root = self.root / self.project_relative_root
        self.registry_path = self.root / "workspace/project_registry.md"
        self.queue_path = self.project_root / "approvals/approval_queue.md"
        self.approval_item_path = (
            self.project_root
            / "approvals/items/2026/APPR-20260724-001-sample-approval.md"
        )
        self.decision_path = self.project_root / "decisions/decision_log.md"
        self.version_path = self.project_root / "versions/version_history.md"
        self.creative_index_rows: list[str] = []
        self.creative_snapshot_rows: list[str] = []

    def create(self, approval_status: str = "applied") -> "WorkspaceFixture":
        self._write(self.root / "README.md", "# Fixture Workspace\n")
        self._write_registry([(self.project_id, self.project_relative_root)])

        for directory in (
            "design",
            "ideas",
            "approvals/assets",
            "decisions",
            "versions",
        ):
            (self.project_root / directory).mkdir(parents=True, exist_ok=True)

        self._write(
            self.project_root / "README.md",
            "# Sample Project\n\n[Brief](project_brief.md)\n",
        )
        self._write(self.project_root / "project_brief.md", "# Project Brief\n")
        self._write(
            self.project_root / "tbd_tracker.md",
            "# TBD 입력·추적\n\n[Brief](project_brief.md)\n",
        )
        self._write(
            self.project_root / "design/README.md",
            "# Design\n\n[Brief](../project_brief.md)\n",
        )
        self._write(
            self.project_root / "ideas/temporary_ideas.md",
            "# Temporary Ideas\n",
        )
        self._write_approval_queue(approval_status)
        self._write(
            self.decision_path,
            "# Decision Log\n\n"
            "## Entries\n\n"
            "- 관련 승인 큐: `APPR-20260724-001`\n",
        )
        self._write(
            self.version_path,
            "# Version History\n\n"
            "## Entries\n\n"
            "- 관련 승인 큐: `APPR-20260724-001`\n",
        )
        return self

    @property
    def project(self) -> ProjectRecord:
        return ProjectRecord(self.project_id, self.project_relative_root)

    def _write_registry(self, projects: list[tuple[str, str]]) -> None:
        rows = "\n".join(
            f"| `{project_id}` | 샘플 | Sample | active | `{root}` |"
            for project_id, root in projects
        )
        self._write(
            self.registry_path,
            "# Project Registry\n\n"
            "## Projects\n\n"
            "| 프로젝트 ID | 한국어명 | 영어명 | 상태 | 프로젝트 루트 |\n"
            "|---|---|---|---|---|\n"
            f"{rows}\n\n"
            "## Rules\n",
        )

    def _write_approval_queue(self, status: str) -> None:
        status_heading = {
            "pending": "Pending",
            "approved": "Approved",
            "applied": "Applied",
            "needs_reconfirmation": "Needs Reconfirmation",
            "on_hold": "On Hold",
            "change_requested": "Change Requested",
            "rejected": "Rejected",
        }[status]
        self._write(
            self.queue_path,
            "# Approval Queue\n\n"
            f"## {status_heading}\n\n"
            "- [APPR-20260724-001: 샘플 승인]"
            "(items/2026/APPR-20260724-001-sample-approval.md)\n",
        )
        self._write(
            self.approval_item_path,
            "# APPR-20260724-001: 샘플 승인\n\n"
            "## Metadata\n\n"
            "- ID: APPR-20260724-001\n"
            f"- 상태: {status}\n\n"
            "## Draft\n\n"
            "```markdown\n"
            "### APPR-19990101-999: 코드 예시 속 가짜 항목\n"
            "- ID: APPR-19990101-999\n"
            "- 상태: applied\n"
            "```\n",
        )

    def write_creative_rule(
        self,
        rule_slug: str = "system_creation",
        *,
        project_id: str | None = None,
        agent_id: str | None = None,
        canonical_role: str = "system",
        base_agent_type: str = "design_creative_planner",
        review_policy: str = "independent_high_risk",
        selector_type: str = "exact",
        target_path: str = "design/systems/core.md",
        operations: tuple[str, ...] | None = None,
        status: str = "active",
        version: int = 1,
        indexed: bool = True,
        missing_field: str | None = None,
    ) -> Path:
        project_id = project_id or self.project_id
        agent_id = agent_id or f"PCA-{project_id}-{rule_slug}"
        agents_root = self.project_root / "agents"
        rules_root = agents_root / "rules"
        rules_root.mkdir(parents=True, exist_ok=True)
        rule_path = rules_root / f"{rule_slug}.md"
        if operations is None:
            operations = (
                ("generate_options", "incorporate_selection")
                if base_agent_type == "design_creative_planner"
                else ("author", "revise", "restructure", "incorporate_selection")
            )

        metadata = {
            "프로젝트 창작 에이전트 ID": f"`{agent_id}`",
            "프로젝트 ID": f"`{project_id}`",
            "규칙 슬러그": f"`{rule_slug}`",
            "상태": f"`{status}`",
            "버전": f"`{version}`",
            "분야": "`sample_system`",
            "canonical document role": f"`{canonical_role}`",
            "경로 선택자": f"`{selector_type}`",
            "대상 경로": f"`{target_path}`",
            "허용 작업": f"`{', '.join(operations)}`",
            "기본 agent_type": f"`{base_agent_type}`",
            "검수 정책": f"`{review_policy}`",
        }
        if missing_field in metadata:
            metadata.pop(missing_field)
        metadata_text = "\n".join(
            f"- {key}: {value}" for key, value in metadata.items()
        )
        def rule_field(key: str, value: str) -> str:
            return "" if missing_field == key else f"- {key}: {value}\n"

        reviewer = (
            "scenario_reviewer"
            if base_agent_type in {"scenario_designer", "scenario_writer"}
            else (
                "design_creative_reviewer"
                if review_policy
                in {"independent_high_risk", "independent_always"}
                else "main"
            )
        )
        self._write(
            rule_path,
            "[TEST FIXTURE: SYNTHETIC]\n\n"
            "# Project Creative Agent Rule\n\n"
            "## Metadata\n\n"
            f"{metadata_text}\n\n"
            "## Applicability\n\n"
            f"{rule_field('적용 요청', '합성 시스템 창작')}"
            f"{rule_field('포함 범위', '합성 GAP')}"
            f"{rule_field('제외 범위', '합성 범위 밖 사실')}"
            f"{rule_field('중단 조건', '합성 근거 충돌')}\n"
            "## Authoring Procedure\n\n"
            f"{rule_field('입력 확인', '합성 입력 확인')}"
            f"{rule_field('출처 충돌·GAP 처리', '충돌은 중단하고 GAP은 분리')}"
            f"{rule_field('Draft·대안 작성 순서', 'Draft 뒤 대안 작성')}"
            f"{rule_field('검수·수정 반복', '필수 finding 해소까지 반복')}"
            f"{rule_field('완료 조건', '합성 검수 통과')}\n"
            "## Creative Direction\n\n"
            f"{rule_field('창작 목표', '합성 검증')}"
            f"{rule_field('기대 플레이 경험', '합성 경험')}"
            f"{rule_field('우선 원칙', '근거 우선')}"
            f"{rule_field('허용하는 판단', '합성 대안')}"
            f"{rule_field('핵심 tradeoff', '범위와 다양성')}"
            f"{rule_field('금지 요소', '미확정 사실 단정')}\n"
            "## Sources\n\n"
            f"{rule_field('필수 근거 파일', 'project_brief.md')}"
            f"{rule_field('출처 우선순위', '사용자 입력, 확정 문서')}"
            f"{rule_field('규칙이 소유하지 않는 canonical facts', '게임 사실')}"
            f"{rule_field('금지된 자료', '다른 프로젝트 자료')}\n"
            "## Authority Boundary\n\n"
            f"{rule_field('허용된 제안 범위', '합성 GAP 대안')}"
            f"{rule_field('임의 창작 금지', 'canonical fact')}"
            f"{rule_field('반드시 `TBD`로 둘 항목', '미확정 사실')}"
            f"{rule_field('별도 승인 제안으로 분리할 항목', 'canonical 변경')}\n"
            "## Output And Provenance\n\n"
            f"{rule_field('기대 산출물', '합성 대안')}"
            f"{rule_field('provenance 체계', 'CP-*')}"
            f"{rule_field('대안·Draft 처리', '선택 전 분리')}"
            f"{rule_field('수치 검증 조건', 'provisional')}\n"
            "## Review Contract\n\n"
            f"- 적용 검수 정책: `{review_policy}`\n"
            f"- reviewer: `{reviewer}`\n"
            f"{rule_field('필수 검수 항목', '합성 출처와 범위')}"
            f"{rule_field('통과 기준', '합성 검증')}"
            f"{rule_field('필수 수정 routing', '원 작성 agent로 반환')}\n"
            "## Rule Mismatch And Replanning\n\n"
            f"{rule_field('범위 불일치 상태', 'blocked_creative_rule_mismatch')}"
            f"{rule_field('규칙 참조 무결성 상태', 'blocked_creative_rule_integrity')}"
            f"{rule_field('과거 결과 처리', 'pinned_rule_grandfathered')}"
            f"{rule_field('자동 재검수', '금지')}"
            f"{rule_field('현재 규칙 재검수 조건', '사용자의 명시적 재검수 요청')}"
            f"{rule_field('자동 개정', '금지')}"
            f"{rule_field('개정 조건', '사용자의 명시적 요청')}\n"
            "## Change History\n\n| 버전 | 날짜 | 변경 |\n|---|---|---|\n"
            f"| {version} | 2026-07-31 | 합성 생성 |\n",
        )

        rule_link = (
            f"[규칙](rules/{rule_slug}.md)" if indexed else "색인 링크 없음"
        )
        self.creative_index_rows.append(
            f"| `{agent_id}` | `sample_system` | `{canonical_role}` | "
            f"`{selector_type}` | `{target_path}` | "
            f"`{', '.join(operations)}` | `{base_agent_type}` | "
            f"`{review_policy}` | {version} | `{status}` | {rule_link} |"
        )
        self._write_creative_index(agents_root)
        return rule_path

    def archive_creative_rule(
        self,
        rule_path: Path,
        *,
        indexed_sha256: str | None = None,
    ) -> Path:
        rule = parse_project_creative_agent_rule(rule_path)
        snapshot_path = (
            self.project_root
            / "agents/rules/archive"
            / rule.rule_slug
            / f"v{rule.version}.md"
        )
        snapshot_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(rule_path, snapshot_path)
        digest = indexed_sha256 or sha256(snapshot_path.read_bytes()).hexdigest()
        self.creative_snapshot_rows.append(
            f"| `{rule.agent_id}` | {rule.version} | `{digest}` | "
            f"[snapshot](rules/archive/{rule.rule_slug}/v{rule.version}.md) |"
        )
        self._write_creative_index(self.project_root / "agents")
        return snapshot_path

    def _write_creative_index(self, agents_root: Path) -> None:
        self._write(
            agents_root / "README.md",
            "[TEST FIXTURE: SYNTHETIC]\n\n"
            "# Project Creative Agents\n\n"
            f"- 프로젝트 ID: `{self.project_id}`\n\n"
            "## Rules\n\n"
            "| 프로젝트 창작 에이전트 ID | 분야 | canonical role | "
            "경로 선택자 | 대상 경로 | 허용 작업 | 기본 agent_type | "
            "검수 정책 | 버전 | 상태 | 규칙 |\n"
            "|---|---|---|---|---|---|---|---|---:|---|---|\n"
            f"{chr(10).join(self.creative_index_rows)}\n\n"
            "## Archived Rule Snapshots\n\n"
            "| 프로젝트 창작 에이전트 ID | 버전 | SHA-256 | snapshot |\n"
            "|---|---:|---|---|\n"
            f"{chr(10).join(self.creative_snapshot_rows) or '| `없음` |  |  |  |'}\n",
        )

    @staticmethod
    def _write(path: Path, text: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


class ProjectRegistryTests(unittest.TestCase):
    def test_TBD_추적_문서가_없으면_필수_파일_누락이다(self) -> None:
        with TemporaryDirectory() as temp_dir:
            fixture = WorkspaceFixture(Path(temp_dir)).create()
            tracker = fixture.project_root / "tbd_tracker.md"
            tracker.unlink()

            issues = validate_project_structure(fixture.project, fixture.root)

            self.assertEqual(["missing-project-file"], [issue.code for issue in issues])
            self.assertIn("tbd_tracker.md", str(issues[0]))

    def test_정상_레지스트리와_프로젝트_구조를_읽는다(self) -> None:
        with TemporaryDirectory() as temp_dir:
            fixture = WorkspaceFixture(Path(temp_dir)).create()

            projects, registry_issues = validate_project_registry(
                fixture.registry_path,
                fixture.root,
            )
            structure_issues = validate_project_structure(projects[0], fixture.root)

            self.assertEqual(1, len(projects))
            self.assertEqual([], registry_issues, format_issues(registry_issues))
            self.assertEqual([], structure_issues, format_issues(structure_issues))

    def test_빈_레지스트리를_실패로_판정한다(self) -> None:
        with TemporaryDirectory() as temp_dir:
            fixture = WorkspaceFixture(Path(temp_dir))
            fixture._write(
                fixture.registry_path,
                "# Project Registry\n\n## Projects\n\n## Rules\n",
            )

            projects, issues = validate_project_registry(
                fixture.registry_path,
                fixture.root,
            )

            self.assertEqual([], projects)
            self.assertEqual(["empty-registry"], [issue.code for issue in issues])

    def test_중복_프로젝트_ID를_실패로_판정한다(self) -> None:
        with TemporaryDirectory() as temp_dir:
            fixture = WorkspaceFixture(Path(temp_dir))
            fixture._write_registry(
                [
                    ("sample-project", "workspace/projects/sample-project/"),
                    ("sample-project", "workspace/projects/another-project/"),
                ]
            )

            _, issues = validate_project_registry(
                fixture.registry_path,
                fixture.root,
            )

            self.assertIn("duplicate-project-id", [issue.code for issue in issues])

    def test_저장소_프로젝트_영역_밖의_루트를_실패로_판정한다(self) -> None:
        with TemporaryDirectory() as temp_dir:
            fixture = WorkspaceFixture(Path(temp_dir))
            fixture._write_registry([("sample-project", "../outside-project/")])

            _, issues = validate_project_registry(
                fixture.registry_path,
                fixture.root,
            )

            self.assertEqual(
                ["project-root-outside-workspace"],
                [issue.code for issue in issues],
            )

    def test_필수_프로젝트_파일_누락을_실패로_판정한다(self) -> None:
        with TemporaryDirectory() as temp_dir:
            fixture = WorkspaceFixture(Path(temp_dir)).create()
            fixture.queue_path.unlink()

            issues = validate_project_structure(fixture.project, fixture.root)

            self.assertEqual(["missing-project-file"], [issue.code for issue in issues])
            self.assertIn("approval_queue.md", str(issues[0]))


class ProjectCreativeAgentRuleTests(unittest.TestCase):
    def test_창작_규칙이_없는_프로젝트도_정상이다(self) -> None:
        with TemporaryDirectory() as temp_dir:
            fixture = WorkspaceFixture(Path(temp_dir)).create()

            issues = validate_project_creative_agents(fixture.project, fixture.root)

            self.assertEqual([], issues, format_issues(issues))

    def test_유효한_분야별_창작_규칙을_읽는다(self) -> None:
        with TemporaryDirectory() as temp_dir:
            fixture = WorkspaceFixture(Path(temp_dir)).create()
            rule_path = fixture.write_creative_rule()

            rule = parse_project_creative_agent_rule(rule_path)
            issues = validate_project_creative_agents(fixture.project, fixture.root)

            self.assertEqual("PCA-sample-project-system_creation", rule.agent_id)
            self.assertEqual("independent_high_risk", rule.review_policy)
            self.assertEqual([], issues, format_issues(issues))

    def test_창작_규칙_필수_필드가_빠지면_실패한다(self) -> None:
        with TemporaryDirectory() as temp_dir:
            fixture = WorkspaceFixture(Path(temp_dir)).create()
            fixture.write_creative_rule(missing_field="검수 정책")

            issues = validate_project_creative_agents(fixture.project, fixture.root)

            self.assertIn(
                "missing-project-creative-rule-field",
                [issue.code for issue in issues],
            )

    def test_창작_규칙_작성_절차가_빠지면_실패한다(self) -> None:
        with TemporaryDirectory() as temp_dir:
            fixture = WorkspaceFixture(Path(temp_dir)).create()
            fixture.write_creative_rule(missing_field="Draft·대안 작성 순서")

            issues = validate_project_creative_agents(fixture.project, fixture.root)

            self.assertIn(
                "missing-project-creative-rule-field",
                [issue.code for issue in issues],
            )

    def test_다른_프로젝트_ID의_규칙을_실패로_판정한다(self) -> None:
        with TemporaryDirectory() as temp_dir:
            fixture = WorkspaceFixture(Path(temp_dir)).create()
            fixture.write_creative_rule(project_id="another-project")

            issues = validate_project_creative_agents(fixture.project, fixture.root)
            codes = [issue.code for issue in issues]

            self.assertIn("project-creative-rule-project-mismatch", codes)
            self.assertIn("invalid-project-creative-agent-id", codes)

    def test_시나리오_창작은_항상_독립_검수여야_한다(self) -> None:
        with TemporaryDirectory() as temp_dir:
            fixture = WorkspaceFixture(Path(temp_dir)).create()
            fixture.write_creative_rule(
                rule_slug="scenario_creation",
                canonical_role="scenario",
                base_agent_type="scenario_designer",
                review_policy="self_and_main",
            )

            issues = validate_project_creative_agents(fixture.project, fixture.root)

            self.assertIn(
                "scenario-independent-review-required",
                [issue.code for issue in issues],
            )

    def test_색인에_없는_창작_규칙을_실패로_판정한다(self) -> None:
        with TemporaryDirectory() as temp_dir:
            fixture = WorkspaceFixture(Path(temp_dir)).create()
            fixture.write_creative_rule(indexed=False)

            issues = validate_project_creative_agents(fixture.project, fixture.root)

            self.assertIn(
                "unindexed-project-creative-rule",
                [issue.code for issue in issues],
            )

    def test_중복_프로젝트_창작_에이전트_ID를_실패로_판정한다(self) -> None:
        with TemporaryDirectory() as temp_dir:
            fixture = WorkspaceFixture(Path(temp_dir)).create()
            first_rule = fixture.write_creative_rule()
            duplicate_id = parse_project_creative_agent_rule(first_rule).agent_id
            fixture.write_creative_rule(
                rule_slug="content_creation",
                agent_id=duplicate_id,
                canonical_role="content",
            )

            issues = validate_project_creative_agents(fixture.project, fixture.root)

            self.assertIn(
                "duplicate-project-creative-agent-id",
                [issue.code for issue in issues],
            )

    def test_색인의_모든_routing_메타데이터를_규칙과_대조한다(self) -> None:
        replacements = {
            0: "`PCA-sample-project-wrong`",
            1: "`wrong_domain`",
            2: "`content`",
            3: "`subtree`",
            4: "`design/content/`",
            5: "`incorporate_selection`",
            6: "`scenario_designer`",
            7: "`self_and_main`",
            8: "9",
            9: "`retired`",
        }
        for column, replacement in replacements.items():
            with self.subTest(column=column), TemporaryDirectory() as temp_dir:
                fixture = WorkspaceFixture(Path(temp_dir)).create()
                fixture.write_creative_rule()
                cells = fixture.creative_index_rows[0].strip("|").split("|")
                cells[column] = f" {replacement} "
                fixture.creative_index_rows[0] = f"|{'|'.join(cells)}|"
                fixture._write_creative_index(fixture.project_root / "agents")

                issues = validate_project_creative_agents(
                    fixture.project,
                    fixture.root,
                )

                self.assertIn(
                    "project-creative-index-metadata-mismatch",
                    [issue.code for issue in issues],
                )

    def test_exact와_subtree의_겹치는_active_규칙을_실패시킨다(self) -> None:
        with TemporaryDirectory() as temp_dir:
            fixture = WorkspaceFixture(Path(temp_dir)).create()
            fixture.write_creative_rule(
                rule_slug="system_tree",
                selector_type="subtree",
                target_path="design/systems/",
                operations=("generate_options",),
            )
            fixture.write_creative_rule(
                rule_slug="system_exact",
                selector_type="exact",
                target_path="design/systems/core.md",
                operations=("generate_options",),
            )

            issues = validate_project_creative_agents(fixture.project, fixture.root)

            self.assertIn(
                "overlapping-active-project-creative-rules",
                [issue.code for issue in issues],
            )

    def test_exact끼리와_subtree끼리의_중복도_실패시킨다(self) -> None:
        cases = (
            (
                "exact",
                "design/systems/core.md",
                "exact",
                "design/systems/core.md",
            ),
            (
                "subtree",
                "design/systems/",
                "subtree",
                "design/systems/combat/",
            ),
        )
        for left_type, left_path, right_type, right_path in cases:
            with self.subTest(
                left_type=left_type,
                right_type=right_type,
            ), TemporaryDirectory() as temp_dir:
                fixture = WorkspaceFixture(Path(temp_dir)).create()
                fixture.write_creative_rule(
                    rule_slug="left_rule",
                    selector_type=left_type,
                    target_path=left_path,
                    operations=("generate_options",),
                )
                fixture.write_creative_rule(
                    rule_slug="right_rule",
                    selector_type=right_type,
                    target_path=right_path,
                    operations=("generate_options",),
                )

                issues = validate_project_creative_agents(
                    fixture.project,
                    fixture.root,
                )

                self.assertIn(
                    "overlapping-active-project-creative-rules",
                    [issue.code for issue in issues],
                )

    def test_같은_경로라도_허용_작업이_다르면_공존한다(self) -> None:
        with TemporaryDirectory() as temp_dir:
            fixture = WorkspaceFixture(Path(temp_dir)).create()
            fixture.write_creative_rule(
                rule_slug="system_options",
                operations=("generate_options",),
            )
            fixture.write_creative_rule(
                rule_slug="system_selection",
                operations=("incorporate_selection",),
            )

            issues = validate_project_creative_agents(fixture.project, fixture.root)

            self.assertEqual([], issues, format_issues(issues))

    def test_같은_경로와_작업도_canonical_role이_다르면_공존한다(self) -> None:
        with TemporaryDirectory() as temp_dir:
            fixture = WorkspaceFixture(Path(temp_dir)).create()
            fixture.write_creative_rule(
                rule_slug="system_rule",
                canonical_role="system",
            )
            fixture.write_creative_rule(
                rule_slug="content_rule",
                canonical_role="content",
            )

            issues = validate_project_creative_agents(fixture.project, fixture.root)

            self.assertEqual([], issues, format_issues(issues))

    def test_retired_규칙은_active_범위_중복에서_제외한다(self) -> None:
        with TemporaryDirectory() as temp_dir:
            fixture = WorkspaceFixture(Path(temp_dir)).create()
            fixture.write_creative_rule(rule_slug="system_active")
            fixture.write_creative_rule(
                rule_slug="system_retired",
                status="retired",
            )

            issues = validate_project_creative_agents(fixture.project, fixture.root)

            self.assertEqual([], issues, format_issues(issues))

    def test_위험한_대상_경로와_agent_작업_불일치를_실패시킨다(self) -> None:
        with TemporaryDirectory() as temp_dir:
            fixture = WorkspaceFixture(Path(temp_dir)).create()
            fixture.write_creative_rule(
                target_path="../outside.md",
                base_agent_type="scenario_designer",
                canonical_role="scenario",
                review_policy="independent_always",
                operations=("dance",),
            )

            issues = validate_project_creative_agents(fixture.project, fixture.root)
            codes = [issue.code for issue in issues]

            self.assertIn("invalid-project-creative-target-path", codes)
            self.assertIn("invalid-project-creative-operations", codes)
            self.assertIn("project-creative-agent-operation-mismatch", codes)

    def test_이전_규칙_snapshot의_버전과_SHA를_검증한다(self) -> None:
        with TemporaryDirectory() as temp_dir:
            fixture = WorkspaceFixture(Path(temp_dir)).create()
            rule_path = fixture.write_creative_rule()
            fixture.archive_creative_rule(rule_path)
            fixture._write(
                rule_path,
                rule_path.read_text(encoding="utf-8").replace(
                    "- 버전: `1`",
                    "- 버전: `2`",
                    1,
                ),
            )
            cells = fixture.creative_index_rows[0].strip("|").split("|")
            cells[8] = " 2 "
            fixture.creative_index_rows[0] = f"|{'|'.join(cells)}|"
            fixture._write_creative_index(fixture.project_root / "agents")

            issues = validate_project_creative_agents(fixture.project, fixture.root)

            self.assertEqual([], issues, format_issues(issues))

    def test_archive_snapshot_변조를_실패시킨다(self) -> None:
        with TemporaryDirectory() as temp_dir:
            fixture = WorkspaceFixture(Path(temp_dir)).create()
            rule_path = fixture.write_creative_rule()
            snapshot_path = fixture.archive_creative_rule(rule_path)
            fixture._write(
                rule_path,
                rule_path.read_text(encoding="utf-8").replace(
                    "- 버전: `1`",
                    "- 버전: `2`",
                    1,
                ),
            )
            cells = fixture.creative_index_rows[0].strip("|").split("|")
            cells[8] = " 2 "
            fixture.creative_index_rows[0] = f"|{'|'.join(cells)}|"
            fixture._write_creative_index(fixture.project_root / "agents")
            fixture._write(
                snapshot_path,
                snapshot_path.read_text(encoding="utf-8") + "\n변조\n",
            )

            issues = validate_project_creative_agents(fixture.project, fixture.root)

            self.assertIn(
                "project-creative-snapshot-sha256-mismatch",
                [issue.code for issue in issues],
            )

    def test_색인에_없는_archive_snapshot을_실패시킨다(self) -> None:
        with TemporaryDirectory() as temp_dir:
            fixture = WorkspaceFixture(Path(temp_dir)).create()
            rule_path = fixture.write_creative_rule(version=2)
            snapshot_path = (
                fixture.project_root
                / "agents/rules/archive/system_creation/v1.md"
            )
            fixture._write(
                snapshot_path,
                rule_path.read_text(encoding="utf-8").replace(
                    "- 버전: `2`",
                    "- 버전: `1`",
                    1,
                ),
            )

            issues = validate_project_creative_agents(fixture.project, fixture.root)

            self.assertIn(
                "unindexed-project-creative-snapshot",
                [issue.code for issue in issues],
            )

    def test_agents_루트의_공통_창작_문서를_금지한다(self) -> None:
        with TemporaryDirectory() as temp_dir:
            fixture = WorkspaceFixture(Path(temp_dir)).create()
            fixture.write_creative_rule()
            fixture._write(
                fixture.project_root / "agents/creative_direction.md",
                "# 금지된 공통 창작 규칙\n",
            )

            issues = validate_project_creative_agents(fixture.project, fixture.root)

            self.assertIn(
                "project-creative-common-rule-forbidden",
                [issue.code for issue in issues],
            )


class MarkdownLinkTests(unittest.TestCase):
    def test_TBD_추적_문서의_깨진_원본_링크를_검출한다(self) -> None:
        with TemporaryDirectory() as temp_dir:
            fixture = WorkspaceFixture(Path(temp_dir)).create()
            tracker = fixture.project_root / "tbd_tracker.md"
            fixture._write(tracker, "# TBD 입력·추적\n\n[원본](missing-source.md)\n")

            paths = navigation_markdown_files(fixture.root, [fixture.project])
            issues = validate_markdown_links(paths, fixture.root)

            self.assertIn(tracker.resolve(), paths)
            self.assertEqual(["broken-markdown-link"], [issue.code for issue in issues])
            self.assertIn("missing-source.md", str(issues[0]))

    def test_정상_탐색_문서의_링크가_통과한다(self) -> None:
        with TemporaryDirectory() as temp_dir:
            fixture = WorkspaceFixture(Path(temp_dir)).create()

            paths = navigation_markdown_files(fixture.root, [fixture.project])
            issues = validate_markdown_links(paths, fixture.root)

            self.assertEqual([], issues, format_issues(issues))

    def test_깨진_로컬_링크를_실패로_판정한다(self) -> None:
        with TemporaryDirectory() as temp_dir:
            fixture = WorkspaceFixture(Path(temp_dir)).create()
            fixture._write(
                fixture.project_root / "README.md",
                "# Sample\n\n[없는 문서](missing.md)\n",
            )

            paths = navigation_markdown_files(fixture.root, [fixture.project])
            issues = validate_markdown_links(paths, fixture.root)

            self.assertEqual(["broken-markdown-link"], [issue.code for issue in issues])
            self.assertIn("missing.md", str(issues[0]))

    def test_저장소_밖으로_나가는_링크를_실패로_판정한다(self) -> None:
        with TemporaryDirectory() as temp_dir:
            fixture = WorkspaceFixture(Path(temp_dir)).create()
            fixture._write(
                fixture.project_root / "README.md",
                "# Sample\n\n[외부 파일](../../../../outside.md)\n",
            )

            paths = navigation_markdown_files(fixture.root, [fixture.project])
            issues = validate_markdown_links(paths, fixture.root)

            self.assertEqual(
                ["link-outside-repository"],
                [issue.code for issue in issues],
            )

    def test_코드_블록과_외부_URL은_링크_검사에서_제외한다(self) -> None:
        with TemporaryDirectory() as temp_dir:
            fixture = WorkspaceFixture(Path(temp_dir)).create()
            fixture._write(
                fixture.project_root / "README.md",
                "# Sample\n\n"
                "[외부](https://example.com/not-checked)\n\n"
                "```markdown\n"
                "[예시](missing-example.md)\n"
                "```\n",
            )

            paths = navigation_markdown_files(fixture.root, [fixture.project])
            issues = validate_markdown_links(paths, fixture.root)

            self.assertEqual([], issues, format_issues(issues))


class ApprovalRecordTests(unittest.TestCase):
    def test_승인_제목과_Metadata_ID가_일치하면_통과한다(self) -> None:
        with TemporaryDirectory() as temp_dir:
            fixture = WorkspaceFixture(Path(temp_dir)).create()

            issues = validate_approval_records(fixture.queue_path)

            self.assertEqual([], issues, format_issues(issues))

    def test_승인_ID_중복을_실패로_판정한다(self) -> None:
        with TemporaryDirectory() as temp_dir:
            fixture = WorkspaceFixture(Path(temp_dir)).create()
            duplicate_path = (
                fixture.project_root
                / "approvals/items/2026/APPR-20260724-002-duplicate-approval.md"
            )
            fixture._write(
                duplicate_path,
                "# APPR-20260724-001: 중복 승인\n\n"
                "## Metadata\n\n"
                "- ID: APPR-20260724-001\n"
                "- 상태: applied\n",
            )
            with fixture.queue_path.open("a", encoding="utf-8") as queue:
                queue.write(
                    "- [APPR-20260724-002: 중복 승인]"
                    "(items/2026/APPR-20260724-002-duplicate-approval.md)\n"
                )

            issues = validate_approval_records(fixture.queue_path)

            self.assertIn("duplicate-approval-id", [issue.code for issue in issues])

    def test_제목과_Metadata_ID_불일치를_실패로_판정한다(self) -> None:
        with TemporaryDirectory() as temp_dir:
            fixture = WorkspaceFixture(Path(temp_dir)).create()
            text = fixture.approval_item_path.read_text(encoding="utf-8")
            fixture.approval_item_path.write_text(
                text.replace(
                    "- ID: APPR-20260724-001",
                    "- ID: APPR-20260724-002",
                    1,
                ),
                encoding="utf-8",
            )

            issues = validate_approval_records(fixture.queue_path)

            self.assertEqual(["approval-id-mismatch"], [issue.code for issue in issues])

    def test_코드_블록_속_승인_예시는_항목으로_세지_않는다(self) -> None:
        with TemporaryDirectory() as temp_dir:
            fixture = WorkspaceFixture(Path(temp_dir)).create()

            records = parse_approval_records(fixture.queue_path)
            approval_issues = validate_approval_records(fixture.queue_path)

            self.assertEqual(1, len(records))
            self.assertEqual([], approval_issues, format_issues(approval_issues))

    def test_Queue와_개별_문서의_상태가_다르면_실패한다(self) -> None:
        with TemporaryDirectory() as temp_dir:
            fixture = WorkspaceFixture(Path(temp_dir)).create()
            text = fixture.approval_item_path.read_text(encoding="utf-8")
            fixture.approval_item_path.write_text(
                text.replace("- 상태: applied", "- 상태: pending", 1),
                encoding="utf-8",
            )

            issues = validate_approval_records(fixture.queue_path)

            self.assertIn(
                "approval-status-section-mismatch",
                [issue.code for issue in issues],
            )

    def test_Queue에_없는_개별_승인_문서를_실패로_판정한다(self) -> None:
        with TemporaryDirectory() as temp_dir:
            fixture = WorkspaceFixture(Path(temp_dir)).create()
            fixture._write(
                fixture.project_root
                / "approvals/items/2026/APPR-20260724-002-unlisted-approval.md",
                "# APPR-20260724-002: 누락 승인\n\n"
                "## Metadata\n\n"
                "- ID: APPR-20260724-002\n"
                "- 상태: applied\n",
            )

            issues = validate_approval_records(fixture.queue_path)

            self.assertIn("unlisted-approval-item", [issue.code for issue in issues])

    def test_내용_슬러그가_없는_승인_파일명을_실패로_판정한다(self) -> None:
        with TemporaryDirectory() as temp_dir:
            fixture = WorkspaceFixture(Path(temp_dir)).create()
            invalid_path = (
                fixture.approval_item_path.parent / "APPR-20260724-001.md"
            )
            fixture.approval_item_path.rename(invalid_path)
            queue_text = fixture.queue_path.read_text(encoding="utf-8")
            fixture.queue_path.write_text(
                queue_text.replace(
                    "APPR-20260724-001-sample-approval.md",
                    "APPR-20260724-001.md",
                ),
                encoding="utf-8",
            )

            issues = validate_approval_records(fixture.queue_path)

            self.assertIn(
                "approval-filename-id-mismatch",
                [issue.code for issue in issues],
            )

    def test_같은_상태의_승인_링크가_작성_순서와_다르면_실패한다(self) -> None:
        with TemporaryDirectory() as temp_dir:
            fixture = WorkspaceFixture(Path(temp_dir)).create()
            fixture._write(
                fixture.project_root
                / "approvals/items/2026/APPR-20260724-002-second-approval.md",
                "# APPR-20260724-002: 두 번째 승인\n\n"
                "## Metadata\n\n"
                "- ID: APPR-20260724-002\n"
                "- 상태: applied\n",
            )
            fixture.queue_path.write_text(
                "# Approval Queue\n\n"
                "## Applied\n\n"
                "- [APPR-20260724-002: 두 번째 승인]"
                "(items/2026/APPR-20260724-002-second-approval.md)\n"
                "- [APPR-20260724-001: 샘플 승인]"
                "(items/2026/APPR-20260724-001-sample-approval.md)\n",
                encoding="utf-8",
            )

            issues = validate_approval_records(fixture.queue_path)

            self.assertIn("approval-items-out-of-order", [issue.code for issue in issues])


class AppliedApprovalReferenceTests(unittest.TestCase):
    def test_applied_승인에_결정과_버전_기록이_있으면_통과한다(self) -> None:
        with TemporaryDirectory() as temp_dir:
            fixture = WorkspaceFixture(Path(temp_dir)).create()

            issues = validate_applied_approval_references(
                fixture.project,
                fixture.root,
            )

            self.assertEqual([], issues, format_issues(issues))

    def test_applied_승인의_결정_기록_누락을_실패로_판정한다(self) -> None:
        with TemporaryDirectory() as temp_dir:
            fixture = WorkspaceFixture(Path(temp_dir)).create()
            fixture.decision_path.write_text("# Decision Log\n", encoding="utf-8")

            issues = validate_applied_approval_references(
                fixture.project,
                fixture.root,
            )

            self.assertEqual(
                ["applied-approval-missing-decision"],
                [issue.code for issue in issues],
            )
            self.assertIn("APPR-20260724-001", str(issues[0]))

    def test_applied_승인의_버전_기록_누락을_실패로_판정한다(self) -> None:
        with TemporaryDirectory() as temp_dir:
            fixture = WorkspaceFixture(Path(temp_dir)).create()
            fixture.version_path.write_text("# Version History\n", encoding="utf-8")

            issues = validate_applied_approval_references(
                fixture.project,
                fixture.root,
            )

            self.assertEqual(
                ["applied-approval-missing-version"],
                [issue.code for issue in issues],
            )
            self.assertIn("APPR-20260724-001", str(issues[0]))

    def test_pending_승인에는_결정과_버전_기록을_강제하지_않는다(self) -> None:
        with TemporaryDirectory() as temp_dir:
            fixture = WorkspaceFixture(Path(temp_dir)).create(approval_status="pending")
            fixture.decision_path.write_text("# Decision Log\n", encoding="utf-8")
            fixture.version_path.write_text("# Version History\n", encoding="utf-8")

            issues = validate_applied_approval_references(
                fixture.project,
                fixture.root,
            )

            self.assertEqual([], issues, format_issues(issues))


class BehaviorTestProvenanceTests(unittest.TestCase):
    def test_표시된_합성_데이터를_테스트_가정으로_분류하면_통과한다(
        self,
    ) -> None:
        record = ProvenanceRecord(
            content=(
                "[TEST FIXTURE: SYNTHETIC] "
                "샘플 마을의 종은 비가 올 때만 울린다."
            ),
            category="test_fixture_assumption",
            origin="synthetic_test_fixture",
            evidence="[TEST FIXTURE: SYNTHETIC] BT-SAMPLE-001",
        )

        issues = validate_provenance_record(record, Path("Task Packet"))

        self.assertEqual([], issues, format_issues(issues))

    def test_합성_데이터를_사용자_사실로_분류하면_실패한다(self) -> None:
        record = ProvenanceRecord(
            content="[TEST FIXTURE: SYNTHETIC] 샘플 설정",
            category="user_fact",
            origin="synthetic_test_fixture",
            evidence="[TEST FIXTURE: SYNTHETIC] BT-SAMPLE-001",
        )

        issues = validate_provenance_record(record, Path("Task Packet"))

        self.assertIn(
            "synthetic-misclassified-as-project-fact",
            [issue.code for issue in issues],
        )

    def test_현재_사용자_입력은_사용자_사실로_분류할_수_있다(self) -> None:
        record = ProvenanceRecord(
            content="사용자가 현재 발화에서 제공한 사실",
            category="user_fact",
            origin="current_user_input",
            evidence="현재 사용자 발화",
        )

        issues = validate_provenance_record(record, Path("Task Packet"))

        self.assertEqual([], issues, format_issues(issues))

    def test_출처가_누락되면_실패한다(self) -> None:
        record = ProvenanceRecord(
            content="출처 없는 문장",
            category="user_fact",
            origin="",
            evidence="",
        )

        issues = validate_provenance_record(record, Path("Task Packet"))
        codes = [issue.code for issue in issues]

        self.assertIn("missing-or-invalid-provenance-origin", codes)
        self.assertIn("missing-provenance-evidence", codes)

    def test_합성_데이터의_표시가_누락되면_실패한다(self) -> None:
        record = ProvenanceRecord(
            content="표시 없는 샘플 설정",
            category="test_fixture_assumption",
            origin="synthetic_test_fixture",
            evidence="BT-SAMPLE-001",
        )

        issues = validate_provenance_record(record, Path("Task Packet"))

        self.assertIn(
            "missing-synthetic-test-label",
            [issue.code for issue in issues],
        )


class BehaviorTestManifestTests(unittest.TestCase):
    MANIFEST_PATH = (
        REPO_ROOT / "tests/fixtures/behavior/synthetic_manifest.md"
    )

    def test_전용_합성_픽스처_매니페스트가_통과한다(self) -> None:
        issues = validate_behavior_test_manifest(self.MANIFEST_PATH, REPO_ROOT)

        self.assertEqual([], issues, format_issues(issues))

    def test_필수_결과_보고가_빠지면_실패한다(self) -> None:
        with TemporaryDirectory() as temp_dir:
            manifest = Path(temp_dir) / "manifest.md"
            text = self.MANIFEST_PATH.read_text(encoding="utf-8")
            manifest.write_text(
                text.replace(
                    "데이터 출처, 실행 환경, 원본 변경, 실제 프로젝트 사실로 채택",
                    "데이터 출처",
                ),
                encoding="utf-8",
            )

            issues = validate_behavior_test_manifest(manifest, REPO_ROOT)

            self.assertIn(
                "missing-behavior-result-report-field",
                [issue.code for issue in issues],
            )

    def test_저장소_안의_실행_경로를_선언하면_실패한다(self) -> None:
        with TemporaryDirectory() as temp_dir:
            manifest = Path(temp_dir) / "manifest.md"
            text = self.MANIFEST_PATH.read_text(encoding="utf-8")
            manifest.write_text(
                text.replace(
                    "<system-temp>/gamepm-behavior-sample",
                    str(REPO_ROOT / "workspace/projects/sample-game"),
                ),
                encoding="utf-8",
            )

            issues = validate_behavior_test_manifest(manifest, REPO_ROOT)

            self.assertIn(
                "behavior-test-work-path-not-isolated",
                [issue.code for issue in issues],
            )

    def test_합성_데이터를_실제_사실로_채택하면_실패한다(self) -> None:
        with TemporaryDirectory() as temp_dir:
            manifest = Path(temp_dir) / "manifest.md"
            text = self.MANIFEST_PATH.read_text(encoding="utf-8")
            manifest.write_text(
                text.replace(
                    "- 실제 프로젝트 사실로 채택: `아님`",
                    "- 실제 프로젝트 사실로 채택: `채택`",
                ),
                encoding="utf-8",
            )

            issues = validate_behavior_test_manifest(manifest, REPO_ROOT)

            self.assertIn(
                "synthetic-test-adoption-forbidden",
                [issue.code for issue in issues],
            )

    def test_실행_복사본을_바꿔도_전용_픽스처_원본은_그대로다(self) -> None:
        source = REPO_ROOT / "tests/fixtures/behavior/sample-game"
        before = {
            path.relative_to(source): path.read_bytes()
            for path in source.rglob("*")
            if path.is_file()
        }

        with TemporaryDirectory(dir=gettempdir()) as temp_dir:
            copied = Path(temp_dir) / "sample-game"
            shutil.copytree(source, copied)
            copied_brief = copied / "project_brief.md"
            copied_brief.write_text(
                copied_brief.read_text(encoding="utf-8")
                + "\n테스트 실행 복사본에서만 추가한 문장\n",
                encoding="utf-8",
            )

        after = {
            path.relative_to(source): path.read_bytes()
            for path in source.rglob("*")
            if path.is_file()
        }
        self.assertEqual(before, after)


class CurrentWorkspaceIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.projects, cls.registry_issues = validate_project_registry(
            REGISTRY_PATH,
            REPO_ROOT,
        )

    def test_현재_등록_프로젝트의_구조가_유효하다(self) -> None:
        issues = list(self.registry_issues)
        for project in self.projects:
            issues.extend(validate_project_structure(project, REPO_ROOT))

        self.assertEqual([], issues, format_issues(issues))

    def test_현재_프로젝트_창작_규칙과_snapshot이_유효하다(self) -> None:
        issues = []
        for project in self.projects:
            issues.extend(validate_project_creative_agents(project, REPO_ROOT))

        self.assertEqual([], issues, format_issues(issues))

    def test_현재_탐색_문서의_로컬_링크가_유효하다(self) -> None:
        paths = navigation_markdown_files(REPO_ROOT, self.projects)
        issues = validate_markdown_links(paths, REPO_ROOT)

        self.assertEqual([], issues, format_issues(issues))

    def test_현재_승인_ID가_유효하고_중복되지_않는다(self) -> None:
        issues = []
        for project in self.projects:
            queue_path = (
                REPO_ROOT
                / project.root
                / "approvals/approval_queue.md"
            )
            issues.extend(validate_approval_records(queue_path))

        self.assertEqual([], issues, format_issues(issues))

    def test_현재_applied_승인이_결정과_버전_기록에_연결된다(self) -> None:
        issues = []
        for project in self.projects:
            issues.extend(validate_applied_approval_references(project, REPO_ROOT))

        self.assertEqual([], issues, format_issues(issues))


class ApprovalSafetyContractTests(unittest.TestCase):
    def test_모호한_승인_표현은_미적용_안내를_요구한다(self) -> None:
        agents_rules = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        approval_workflow = (
            REPO_ROOT / "docs/workflows/approval_queue.md"
        ).read_text(encoding="utf-8")

        self.assertIn("Explicitly tell the user that nothing was", agents_rules)
        self.assertIn("keep the current\n  approval state unchanged", agents_rules)
        self.assertIn("아무 변경도 적용하지", approval_workflow)
        self.assertIn("현재 승인 상태를 유지", approval_workflow)
        self.assertIn("승인하고 적용해줘", approval_workflow)

    def test_원본_재확인은_Git_없이_파일_해시로_동작한다(self) -> None:
        approval_workflow = (
            REPO_ROOT / "docs/workflows/approval_queue.md"
        ).read_text(encoding="utf-8")
        approval_template = (
            REPO_ROOT / "docs/templates/approval_item.md"
        ).read_text(encoding="utf-8")
        change_template = (
            REPO_ROOT / "docs/templates/change_proposal.md"
        ).read_text(encoding="utf-8")

        for required_text in (
            "file_sha256 | git_and_file_sha256",
            "기준 Git 커밋: `해당 없음 | <commit>`",
            "작성 당시 기준 상태",
            "text_lf | raw_bytes | 해당 없음",
        ):
            with self.subTest(template_text=required_text):
                self.assertIn(required_text, approval_template)
                self.assertIn(required_text, change_template)

        for required_text in (
            "Git은 필수가 아니며",
            "Git 커밋이 달라졌다는 사실만으로 불일치로 판정하지 않는다",
            "이미 `applied`인 과거 항목은 소급해 무효화하거나",
        ):
            with self.subTest(workflow_text=required_text):
                self.assertIn(required_text, approval_workflow)

        self.assertNotIn(
            "Git 커밋만으로\n  비교 대상을 식별할 수 없는 항목은 적용하지 않는다",
            approval_workflow,
        )


class SourceReconfirmationHashTests(unittest.TestCase):
    def test_text_lf는_BOM과_줄바꿈_차이를_정규화한다(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            lf_path = root / "lf.md"
            crlf_path = root / "crlf.md"
            lf_path.write_bytes("첫 줄\n둘째 줄\n".encode("utf-8"))
            crlf_path.write_bytes(
                b"\xef\xbb\xbf" + "첫 줄\r\n둘째 줄\r\n".encode("utf-8")
            )

            self.assertEqual(
                source_reconfirmation_sha256(lf_path, "text_lf"),
                source_reconfirmation_sha256(crlf_path, "text_lf"),
            )

    def test_raw_bytes는_바이트_차이를_보존한다(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            lf_path = root / "lf.bin"
            crlf_path = root / "crlf.bin"
            lf_path.write_bytes(b"a\nb")
            crlf_path.write_bytes(b"a\r\nb")

            self.assertNotEqual(
                source_reconfirmation_sha256(lf_path, "raw_bytes"),
                source_reconfirmation_sha256(crlf_path, "raw_bytes"),
            )

    def test_지원하지_않는_해시_방식은_거부한다(self) -> None:
        with TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "source.md"
            path.write_text("본문", encoding="utf-8")

            with self.assertRaises(ValueError):
                source_reconfirmation_sha256(path, "unknown")


class SpecialistAgentHandoffContractTests(unittest.TestCase):
    def test_전문_에이전트_호출은_완성된_인계와_none_fork를_요구한다(
        self,
    ) -> None:
        agents_rules = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        workflow = (
            REPO_ROOT / "docs/workflows/specialist_agent_handoff.md"
        ).read_text(encoding="utf-8")
        packet_template = (
            REPO_ROOT / "docs/templates/specialist_task_packet.md"
        ).read_text(encoding="utf-8")

        self.assertIn("complete Specialist Task Packet", agents_rules)
        self.assertIn('fork_turns: "none"', agents_rules)
        self.assertIn('omitted or `"all"`', agents_rules)
        self.assertIn("Required Specialist Task Packet", workflow)
        self.assertIn("Required Invocation Mode", workflow)
        self.assertIn("Main-Agent Return Check", workflow)
        self.assertIn("부모 대화 전체를 Task Packet에 복사하지 않는다", workflow)
        self.assertIn("같은 오류가 반복", workflow)
        self.assertIn("Task Packet 준비 단계에도", workflow)
        self.assertIn("전체 `design/` 트리를 열거", workflow)
        self.assertIn(
            "Approval Queue, 임시 아이디어, Decision Log와 Version History",
            workflow,
        )

        for required_section in (
            "## Routing",
            "## Project Creative Agent Rule",
            "## User Intent",
            "## Material Conversation Context",
            "## Authority Boundary",
            "## Sources And Inputs",
            "## Expected Handoff",
            "## Invocation",
        ):
            with self.subTest(section=required_section):
                self.assertIn(required_section, packet_template)

        for agent_name in SPECIALIST_AGENT_TYPES:
            with self.subTest(packet_target_agent=agent_name):
                self.assertIn(agent_name, packet_template)
                self.assertIn(agent_name, workflow)

    def test_공통_계약이_전문_에이전트_안전장치의_상세_원본이다(self) -> None:
        workflow = (
            REPO_ROOT / "docs/workflows/specialist_agent_handoff.md"
        ).read_text(encoding="utf-8")

        for required_text in (
            "## Shared Specialist Contract",
            "프로젝트를 다시 선택하지 않는다",
            "current_user_input",
            "prior_user_input",
            "confirmed_document",
            "proposal_input",
            "synthetic_test_fixture",
            "[TEST FIXTURE: SYNTHETIC]",
            "blocked_missing_handoff",
            "blocked_test_provenance",
            "blocked_missing_creative_rule",
            "blocked_creative_rule_mismatch",
            "blocked_creative_rule_integrity",
            "Minimal Source Rule",
            "항상 read-only",
            "Do not spawn further subagents",
        ):
            with self.subTest(shared_contract=required_text):
                self.assertIn(required_text, workflow)

    def test_모든_전문_에이전트는_공통_계약을_참조한다(self) -> None:
        for agent_name in (
            "design_creative_planner",
            "design_creative_reviewer",
            "scenario_designer",
            "scenario_reviewer",
            "scenario_writer",
        ):
            with self.subTest(agent=agent_name):
                agent_config = (
                    REPO_ROOT / f".codex/agents/{agent_name}.toml"
                ).read_text(encoding="utf-8")

                self.assertIn(
                    "docs/workflows/specialist_agent_handoff.md",
                    agent_config,
                )
                self.assertIn("Shared specialist contract", agent_config)
                self.assertIn("blocked_missing_handoff", agent_config)
                self.assertIn("Task Packet", agent_config)
                self.assertIn("spawn further", agent_config)
                self.assertNotIn("Provenance gate:", agent_config)
                self.assertNotIn("Required task contract:", agent_config)

    def test_창작_전문_에이전트가_프로젝트_규칙_게이트를_검증한다(
        self,
    ) -> None:
        workflow = (
            REPO_ROOT / "docs/workflows/project_creative_agent_setup.md"
        ).read_text(encoding="utf-8")
        agents_rules = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        packet_template = (
            REPO_ROOT / "docs/templates/specialist_task_packet.md"
        ).read_text(encoding="utf-8")
        setup_template = (
            REPO_ROOT / "docs/templates/project_creative_agent_setup_plan.md"
        ).read_text(encoding="utf-8")

        for required_text in (
            "blocked_missing_creative_rule",
            "blocked_creative_rule_mismatch",
            "blocked_creative_rule_integrity",
            "Archived Rule Snapshots",
            "과거 결과를 자동 재검수·수정·무효화하지 않으며",
            "Automatic Setup Design",
            "에이전트가 보충한 항목",
            "사용자가 아무 메시지도 보내지 않은 상태에서 파일을 자동 저장하지 않는다",
            "`independent_high_risk`를",
            "구현 완료 보고",
        ):
            with self.subTest(text=required_text):
                self.assertIn(required_text, workflow)

        self.assertIn("are PCA-gated", agents_rules)
        self.assertIn(
            "docs/workflows/project_creative_agent_setup.md",
            agents_rules,
        )
        for duplicated_detail in (
            "ask only material preference questions",
            "does not automatically invalidate",
            "agents/rules/archive/<rule_slug>/v<version>.md",
        ):
            with self.subTest(duplicated_detail=duplicated_detail):
                self.assertNotIn(duplicated_detail, agents_rules)

        for required_text in (
            "## Field Guide And Decisions",
            "## Complete Rule Specification",
            "## Agent-Supplied Defaults",
            "## Persistence And Resume",
            "명시적 구현 요청",
        ):
            with self.subTest(setup_text=required_text):
                self.assertIn(required_text, setup_template)

        rule_template = (
            REPO_ROOT / "docs/templates/project_creative_agent_rule.md"
        ).read_text(encoding="utf-8")
        self.assertIn("## Authoring Procedure", rule_template)

        for required_text in (
            "프로젝트 창작 에이전트 ID",
            "규칙 경로",
            "규칙 버전",
            "규칙 SHA-256",
            "규칙 기준",
            "검수 정책",
        ):
            with self.subTest(packet_field=required_text):
                self.assertIn(required_text, packet_template)

        for agent_name in (
            "design_creative_planner",
            "design_creative_reviewer",
            "scenario_designer",
            "scenario_reviewer",
            "scenario_writer",
        ):
            with self.subTest(agent=agent_name):
                agent_config = (
                    REPO_ROOT / f".codex/agents/{agent_name}.toml"
                ).read_text(encoding="utf-8")
                self.assertIn(
                    "docs/workflows/project_creative_agent_setup.md",
                    agent_config,
                )
                self.assertIn("blocked_missing_creative_rule", agent_config)
                self.assertIn("blocked_creative_rule_mismatch", agent_config)
                self.assertIn("blocked_creative_rule_integrity", agent_config)


class AiRuleOwnershipTests(unittest.TestCase):
    def test_규칙별_canonical_owner가_상세_계약을_보유한다(self) -> None:
        contracts = {
            "docs/workflows/specialist_agent_handoff.md": (
                "## Shared Specialist Contract",
                "blocked_missing_handoff",
                "blocked_test_provenance",
                "## Minimal Source Rule",
            ),
            "docs/workflows/project_creative_agent_setup.md": (
                "유일한 상세",
                "blocked_missing_creative_rule",
                "blocked_creative_rule_mismatch",
                "blocked_creative_rule_integrity",
                "Archived Rule Snapshots",
            ),
            "docs/skills/document_completion.md": (
                "GAP 발견",
                "creative_fillable | user_fact | dependency",
                "## Classification",
            ),
            "docs/skills/design_creative_completion.md": (
                "## Phase Order",
                "### generate_options",
                "### incorporate_selection",
                "## Creative Proposal Log",
            ),
            "docs/skills/visual_specification.md": (
                "유일한 상세 원본",
                "### resolve_gaps",
                "### ready_for_mockup",
                "## Mockup Handoff",
            ),
            "docs/skills/scenario_review.md": (
                "유일한 상세 원본",
                "Scenario Improvement Review",
                "## Selection And Approval",
            ),
            "docs/workflows/write_ingame_script.md": (
                "유일한 상세 원본",
                "## Writer Identity",
                "## Narrative Revision Rules",
                "## Creative Disclosure Rules",
            ),
            "docs/workflows/approval_queue.md": (
                "유일한 상세 원본",
                "## Status",
                "## Apply Approved Item Steps",
                "## Source Reconfirmation Rules",
                "## Asset Promotion Rules",
            ),
            "docs/workflows/document_structure.md": (
                "## Canonical Document Roles",
                "## Ownership Rules",
                "## Restructure Principles",
            ),
            "docs/workflows/unity_development.md": (
                "유일한 상세 원본",
                "## Specification Gate",
                "## Implementation Procedure",
                "## Return And Main-Agent Check",
                "## Human Test, Acceptance And Rollback",
                "## Artifact Index And Explicit Cleanup",
            ),
        }

        for relative_path, required_texts in contracts.items():
            text = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
            for required_text in required_texts:
                with self.subTest(owner=relative_path, text=required_text):
                    self.assertIn(required_text, text)

    def test_소비자는_원본을_참조하고_라우터는_하위_절차를_소유하지_않는다(
        self,
    ) -> None:
        for agent_name in SPECIALIST_AGENT_TYPES:
            config = (
                REPO_ROOT / f".codex/agents/{agent_name}.toml"
            ).read_text(encoding="utf-8")
            with self.subTest(agent=agent_name):
                self.assertIn(
                    "docs/workflows/specialist_agent_handoff.md",
                    config,
                )
                self.assertIn(
                    "docs/workflows/project_creative_agent_setup.md",
                    config,
                )

        for relative_path in (
            "docs/workflows/write_design_doc.md",
            "docs/workflows/propose_change.md",
        ):
            workflow = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
            classify_at = workflow.index("docs/skills/document_completion.md")
            create_at = workflow.index(
                "docs/skills/design_creative_completion.md"
            )
            with self.subTest(workflow=relative_path):
                self.assertLess(classify_at, create_at)
                self.assertNotIn("## Option Generation", workflow)
                self.assertNotIn("## Creative Proposal Log", workflow)

        router = (
            REPO_ROOT / "docs/workflows/document_change.md"
        ).read_text(encoding="utf-8")
        intake = (
            REPO_ROOT / "docs/workflows/intake.md"
        ).read_text(encoding="utf-8")
        for forbidden in (
            "## Subagent Orchestration",
            "## Creative Completion Subflow",
            "### General Scenario Pipeline",
            "### In-Game Script Pipeline",
            "Writer's Brief",
        ):
            with self.subTest(router_detail=forbidden):
                self.assertNotIn(forbidden, router)
        self.assertNotIn("## Intent Types", intake)
        self.assertIn("AGENTS.md", intake)

    def test_출력_필드는_template이_소유한다(self) -> None:
        consumers = {
            "docs/skills/document_completion.md": (
                "docs/templates/approval_item.md",
                "Creative Completion Review",
            ),
            "docs/skills/design_creative_completion.md": (
                "docs/templates/approval_item.md",
                "Creative Proposal Log",
            ),
            "docs/skills/visual_specification.md": (
                "docs/templates/visual_specification.md",
                "docs/skills/document_completion.md",
                "docs/skills/design_creative_completion.md",
                "docs/workflows/approval_queue.md",
            ),
            "docs/workflows/specialist_agent_handoff.md": (
                "docs/templates/approval_item.md",
                "Subagent Review",
            ),
            "docs/workflows/write_ingame_script.md": (
                "docs/templates/ingame_script.md",
                "docs/templates/approval_item.md",
            ),
            "docs/workflows/decision_log.md": (
                "docs/templates/decision_log_entry.md",
            ),
            "docs/workflows/version_history.md": (
                "docs/templates/version_entry.md",
            ),
            "docs/workflows/unity_development.md": (
                "docs/templates/unity_development_spec.md",
                "docs/templates/unity_implementation_report.md",
                "docs/templates/unity_artifact_index.md",
            ),
        }
        for relative_path, references in consumers.items():
            text = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
            for reference in references:
                with self.subTest(consumer=relative_path, reference=reference):
                    self.assertIn(reference, text)

    def test_시나리오_작성은_원본_충분성과_사용자_고지를_강제한다(self) -> None:
        def section(text: str, heading: str) -> str:
            start = text.index(heading)
            next_heading = text.find("\n## ", start + len(heading))
            if next_heading == -1:
                return text[start:]
            return text[start:next_heading]

        def table_header(text: str, first_column: str) -> tuple[str, ...]:
            prefix = f"| {first_column} |"
            header = next(
                line.strip()
                for line in text.splitlines()
                if line.strip().startswith(prefix)
            )
            return tuple(cell.strip() for cell in header.strip("|").split("|"))

        completion = (
            REPO_ROOT / "docs/skills/document_completion.md"
        ).read_text(encoding="utf-8")
        packet = (
            REPO_ROOT / "docs/templates/specialist_task_packet.md"
        ).read_text(encoding="utf-8")
        handoff = (
            REPO_ROOT / "docs/workflows/specialist_agent_handoff.md"
        ).read_text(encoding="utf-8")
        script_workflow = (
            REPO_ROOT / "docs/workflows/write_ingame_script.md"
        ).read_text(encoding="utf-8")
        scenario_review = (
            REPO_ROOT / "docs/skills/scenario_review.md"
        ).read_text(encoding="utf-8")
        approval_template = (
            REPO_ROOT / "docs/templates/approval_item.md"
        ).read_text(encoding="utf-8")
        change_template = (
            REPO_ROOT / "docs/templates/change_proposal.md"
        ).read_text(encoding="utf-8")
        agents_rules = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")

        register = section(completion, "## Requirement Register")
        self.assertEqual(
            (
                "필드",
                "필수 내용",
            ),
            table_header(register, "필드"),
        )
        for field in (
            "provenance",
            "source locator",
            "충족 판단 기준",
            "창작 권한",
        ):
            self.assertIn(f"| {field} |", register)

        sufficiency = section(completion, "## Source Sufficiency Gate")
        covered_row = next(
            line for line in sufficiency.splitlines() if line.startswith("| `covered`")
        )
        for evidence in ("원본 locator", "Draft 충족 위치", "검증 결과", "모두"):
            self.assertIn(evidence, covered_row)

        unsupported = section(completion, "## Unsupported Assertion Gate")
        for invariant in ("새 인물·관계·동행", "CW-*", "required_revision", "blocked"):
            self.assertIn(invariant, unsupported)

        packet_contract = section(packet, "## Source Sufficiency Contract")
        self.assertEqual(
            (
                "조건 ID",
                "목표·제약·검증 조건",
                "provenance",
                "정확한 source locator",
                "적용 이유",
                "충족 판단·검증 방법",
                "창작 허용 범위",
            ),
            table_header(packet_contract, "조건 ID"),
        )

        expected_gap_header = (
            "GAP ID",
            "상태",
            "영향",
            "현재 처리",
            "필요한 결정·선행 작업",
            "사용자 질문",
        )
        for template in (approval_template, change_template):
            notice = section(template, "## Source Sufficiency And User Notice")
            self.assertEqual(
                expected_gap_header,
                table_header(notice, "GAP ID"),
            )
            completion_review = section(template, "## Creative Completion Review")
            completion_header = table_header(completion_review, "GAP ID")
            self.assertIn("원본 조건·근거", completion_header)
            self.assertIn("유형", completion_header)
            self.assertIn("위험도", completion_header)
            self.assertNotIn("유형", expected_gap_header)
            self.assertNotIn("위험도", expected_gap_header)
        approval_verdict = next(
            line
            for line in approval_template.splitlines()
            if line.startswith("- 충분성 판정:")
        )
        self.assertNotIn("blocked_insufficient_source", approval_verdict)

        entry_check = section(handoff, "## Specialist Entry Check")
        self.assertIn("provenance", entry_check)
        self.assertIn("정확한 locator", entry_check)
        return_check = section(handoff, "## Main-Agent Return Check")
        self.assertIn("실제 사용자에게 전달", return_check)
        self.assertIn("`pending` 승인 항목", return_check)

        ledger = section(script_workflow, "## Script Measurement Ledger")
        self.assertEqual(("항목", "계산 규칙"), table_header(ledger, "항목"))
        for metric in (
            "전체 조건부 노출 line",
            "실제 경로 line",
            "성공·실패 경로",
            "시간 추정",
            "reviewer",
        ):
            self.assertIn(metric, ledger)

        source_review = section(scenario_review, "## Source Sufficiency Review")
        self.assertIn("두 번 독립 확인", source_review)
        self.assertIn("unsupported assertion", source_review)
        self.assertIn("재계산", source_review)
        self.assertIn("verdict `blocked`", source_review)

        routing = section(completion, "## Finding Routing")
        self.assertIn("`required_revision`", routing)
        self.assertIn("reviewer verdict는 `blocked`", routing)
        self.assertIn("같은 writer 호출을 반복하지 않고", routing)
        self.assertIn("고지 누락", routing)
        self.assertIn("reviewer `pass`", routing)
        self.assertIn("불일치는 `required_revision`", ledger)

        self.assertNotIn(
            "`blocking` 또는 `required_revision`이 있으면",
            script_workflow,
        )
        self.assertIn("verdict가 `revision_required`", script_workflow)
        self.assertIn("`required_revision` finding", script_workflow)
        self.assertIn("verdict가 `blocked`", script_workflow)
        self.assertIn("writer를 반복 호출하지 않는다", script_workflow)
        self.assertIn("verdict\n    routing은 개별 finding 문구보다 우선", script_workflow)

        unsupported = section(completion, "## Unsupported Assertion Gate")
        self.assertIn("`blocked_missing_handoff`", unsupported)
        self.assertIn("`required_revision`", unsupported)
        self.assertIn("reviewer는\n  `blocked`", unsupported)

        writer_config = (
            REPO_ROOT / ".codex/agents/scenario_writer.toml"
        ).read_text(encoding="utf-8")
        reviewer_config = (
            REPO_ROOT / ".codex/agents/scenario_reviewer.toml"
        ).read_text(encoding="utf-8")
        designer_config = (
            REPO_ROOT / ".codex/agents/scenario_designer.toml"
        ).read_text(encoding="utf-8")
        for config in (writer_config, reviewer_config, designer_config):
            self.assertIn("docs/skills/document_completion.md", config)
        self.assertIn("Script Measurement Ledger", writer_config)
        self.assertIn("CW or NR disclosure never grants authority", writer_config)
        self.assertIn("independently recalculate", reviewer_config)

        project_rule_path = (
            REPO_ROOT
            / "workspace/projects/chronicles-of-the-twelve-bonds/agents/rules"
            / "ingame-script-authoring.md"
        )
        project_rule = parse_project_creative_agent_rule(project_rule_path)
        project_rule_text = project_rule_path.read_text(encoding="utf-8")
        self.assertEqual("2", project_rule.version)
        self.assertIn("Script Measurement Ledger", project_rule_text)
        self.assertIn("CW·NR 표시는 권한을 새로 만들지 않는다", project_rule_text)
        self.assertIn("실제 사용자", agents_rules)

    def test_정확히_같은_장문_AI_규칙이_여러_파일에_복제되지_않는다(
        self,
    ) -> None:
        issues = validate_duplicate_ai_rule_lines(REPO_ROOT)
        self.assertEqual([], issues, format_issues(issues))

    def test_장문_AI_규칙_복제를_검토_대상으로_보고한다(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "docs/workflows").mkdir(parents=True)
            duplicated = (
                "This deliberately long policy sentence is duplicated across "
                "two current AI instruction files for review."
            )
            (root / "AGENTS.md").write_text(duplicated, encoding="utf-8")
            (root / "docs/workflows/a.md").write_text(
                duplicated,
                encoding="utf-8",
            )

            issues = validate_duplicate_ai_rule_lines(root, minimum_length=40)

        self.assertEqual(1, len(issues), format_issues(issues))
        self.assertEqual("duplicate-long-ai-rule", issues[0].code)


class VisualSpecificationContractTests(unittest.TestCase):
    def test_시각_명세는_시안_생성_전_결정과_GAP을_해소한다(self) -> None:
        agents_rules = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        skill = (
            REPO_ROOT / "docs/skills/visual_specification.md"
        ).read_text(encoding="utf-8")
        template = (
            REPO_ROOT / "docs/templates/visual_specification.md"
        ).read_text(encoding="utf-8")

        self.assertIn("docs/skills/visual_specification.md", agents_rules)
        for required_text in (
            "creative_fillable | user_fact | dependency",
            "한 번에 1~3개씩",
            "ready_for_mockup",
            "이미지 생성 도구를\n호출하지 않는다",
            "docs/skills/design_creative_completion.md",
        ):
            with self.subTest(text=required_text):
                self.assertIn(required_text, skill)

        for required_text in (
            "표시 문구",
            "정보 위계",
            "상태·전환",
            "해상도 대응",
            "## Human Acceptance",
        ):
            with self.subTest(field=required_text):
                self.assertIn(required_text, template)

    def test_mockup과_reference는_승인_전후에도_같은_역할_폴더를_쓴다(
        self,
    ) -> None:
        workflow = (
            REPO_ROOT / "docs/workflows/approval_queue.md"
        ).read_text(encoding="utf-8")
        project_workflow = (
            REPO_ROOT / "docs/workflows/project_workspace.md"
        ).read_text(encoding="utf-8")
        approval_template = (
            REPO_ROOT / "docs/templates/approval_item.md"
        ).read_text(encoding="utf-8")

        for required_text in (
            "approvals/assets/mockups/",
            "design/assets/mockups/",
            "approvals/assets/references/",
            "design/assets/references/",
            "역할이 다른 폴더로 교차 승격하지 않는다",
            "에셋 루트인 `approvals/assets/`와 `design/assets/` 바로 아래",
        ):
            with self.subTest(text=required_text):
                self.assertIn(required_text, workflow)

        self.assertIn("mockups/", project_workflow)
        self.assertIn("references/", project_workflow)
        self.assertIn("| 역할 | 검토 경로 | 승인 후 canonical 경로", approval_template)
        self.assertIn("### Asset Relocation Operations", approval_template)

    def test_reference만으로_production_시각_명세를_ready로_만들지_않는다(
        self,
    ) -> None:
        workflow = (
            REPO_ROOT / "docs/workflows/unity_development.md"
        ).read_text(encoding="utf-8")
        spec = (
            REPO_ROOT / "docs/templates/unity_development_spec.md"
        ).read_text(encoding="utf-8")

        for required_text in (
            "적용된 Visual Specification 경로·SHA-256",
            "design/assets/mockups/",
            "reference\n    이미지만 있으면 `blocked_missing_development_decision`",
            "placeholder와 폐기 조건",
        ):
            with self.subTest(text=required_text):
                self.assertIn(required_text, workflow)

        for required_text in (
            "## Visual Design",
            "시각 명세 필요: `아니요 | 예`",
            "적용된 Visual Specification 경로·SHA-256",
            "적용된 개발 기준 시안 경로·SHA-256",
            "production 시각 준비 상태",
        ):
            with self.subTest(field=required_text):
                self.assertIn(required_text, spec)

    def test_기존_이미지_11개는_reference_이동_승인에_해시로_고정된다(
        self,
    ) -> None:
        project_root = (
            REPO_ROOT
            / "workspace/projects/chronicles-of-the-twelve-bonds"
        )
        approval_path = (
            project_root
            / "approvals/items/2026/APPR-20260817-001-asset-role-directory-separation.md"
        )
        approval = approval_path.read_text(encoding="utf-8")
        rows = [
            line
            for line in approval.splitlines()
            if line.startswith("| `reference` | `workspace/projects/")
        ]

        self.assertEqual(11, len(rows))
        state_line = next(
            line for line in approval.splitlines() if line.startswith("- 상태:")
        )
        state = state_line.split(":", 1)[1].strip()
        direct_images = sorted(
            path
            for asset_root in (
                project_root / "approvals/assets",
                project_root / "design/assets",
            )
            for path in asset_root.glob("*")
            if path.is_file()
        )

        source_paths: list[Path] = []
        target_paths: list[Path] = []
        for row in rows:
            columns = [column.strip().strip("`") for column in row.split("|")]
            source = REPO_ROOT / columns[2]
            target = REPO_ROOT / columns[3]
            expected_sha = columns[4]
            source_paths.append(source)
            target_paths.append(target)
            self.assertIn("references", target.parts)

            current = target if state == "applied" else source
            self.assertTrue(current.is_file(), current)
            self.assertEqual(
                expected_sha,
                source_reconfirmation_sha256(current, "raw_bytes"),
            )

        if state == "applied":
            self.assertEqual([], direct_images)
            self.assertTrue(all(not path.exists() for path in source_paths))
        else:
            self.assertEqual(sorted(source_paths), direct_images)
            self.assertTrue(all(not path.exists() for path in target_paths))

        self.assertIn("gameplay_ui_reference_1920x1080_v1.png", approval)
        self.assertIn("visual_novel_ui_reference_1920x1080_v1.png", approval)
        gameplay_ui = (
            project_root / "design/ui/gameplay_ui.md"
        ).read_text(encoding="utf-8")
        game_overview = (
            project_root / "design/game/game_design_overview.md"
        ).read_text(encoding="utf-8")
        if state == "applied":
            self.assertIn("상황별 설명용 참고 이미지", gameplay_ui)
            self.assertIn("../assets/references/", gameplay_ui)
            self.assertNotIn("../assets/gameplay_ui_", gameplay_ui)
            self.assertIn("설명용 참고 이미지", game_overview)
            self.assertIn("DEC-20260817-001", approval)
            self.assertIn("VER-20260817-001", approval)
        else:
            self.assertEqual(
                "352c80073ad1be01cd3d69c9a1e70c5697b7596d5e4ba160351bfcf428ddec94",
                source_reconfirmation_sha256(
                    project_root / "design/ui/gameplay_ui.md",
                    "text_lf",
                ),
            )
            self.assertEqual(
                "fb968cd300941367bb2a7b4eb05306fc8c62d9aa54d24ac71d06985e4ec9807e",
                source_reconfirmation_sha256(
                    project_root / "design/game/game_design_overview.md",
                    "text_lf",
                ),
            )

    def test_승인안에_없는_에셋_루트_이미지는_무결성_오류다(self) -> None:
        with TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            project_root = repo_root / "workspace/projects/sample"
            asset_root = project_root / "approvals/assets"
            (project_root / "approvals/items").mkdir(parents=True)
            asset_root.mkdir(parents=True)
            (asset_root / "unclassified.png").write_bytes(b"image")
            project = ProjectRecord("sample", "workspace/projects/sample")

            issues = validate_asset_role_directories(project, repo_root)

        self.assertEqual(1, len(issues), format_issues(issues))
        self.assertEqual("asset-file-at-role-root", issues[0].code)


class UnityDevelopmentContractTests(unittest.TestCase):
    @staticmethod
    def _complete_unity_spec_text() -> str:
        return (
            "# DEV Test\n\n"
            "- 작업 유형: `implement`\n"
            "- 개발 등급: `connection_test`\n"
            "- 등급 선정 근거: 공식 MCP 연결 확인\n"
            "- 상태: `ready`\n"
            "- scene 통합 방식: `standalone_scene`\n"
            "- Build Settings·시작 scene 변경: `없음`\n"
            "- MCP tool namespace·Editor ready·대상 경로·Pipeline: 공식 MCP·ready·정확한 경로·연결됨\n"
            "- mutation 없는 preflight 결과: `pass`\n"
            "- 산출물 분류: `connection_test`\n"
            "- 통합 방식: `isolated`\n"
            "- 생성·수정할 전용 경로: `Assets/GamePM/ConnectionTests/DEV-TEST/`\n"
            "- 기존 공용 파일 수정 목록: `없음`\n"
            "- placeholder 목록: `없음`\n"
            "- placeholder 허용·교체 조건: `해당 없음`\n"
            "- 보존 정책: `preserve_until_explicit_cleanup`\n"
            "- 정리 그룹: `connection_test`\n"
            "- 승격 조건: `해당 없음`\n"
            "- 등급별 완료 조건: compile 성공과 사람 확인 대기\n"
            "- 실행 ID: `DEV-20260817-001-RUN-001`\n"
        )

    def test_Unity_개발은_기획_전문_agent와_분리된다(self) -> None:
        config = (
            REPO_ROOT / ".codex/agents/unity_developer.toml"
        ).read_text(encoding="utf-8")
        workflow = (
            REPO_ROOT / "docs/workflows/unity_development.md"
        ).read_text(encoding="utf-8")

        self.assertIn('sandbox_mode = "workspace-write"', config)
        self.assertIn("docs/workflows/unity_development.md", config)
        self.assertNotIn("specialist_agent_handoff.md", config)
        self.assertIn("GamePM design, approvals, ideas, decisions", config)
        self.assertIn("프로젝트와 해당 실행의 로컬 backup만", workflow)
        self.assertIn("Codex의 writable root", workflow)

    def test_공식_MCP와_명세_게이트가_강제된다(self) -> None:
        agents_rules = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        workflow = (
            REPO_ROOT / "docs/workflows/unity_development.md"
        ).read_text(encoding="utf-8")
        spec = (
            REPO_ROOT / "docs/templates/unity_development_spec.md"
        ).read_text(encoding="utf-8")

        for required_text in (
            "blocked_missing_development_handoff",
            "blocked_invalid_unity_project",
            "blocked_missing_development_decision",
            "blocked_unity_mcp_unavailable",
            "implementation_choice",
            "공식 Unity MCP",
        ):
            with self.subTest(text=required_text):
                self.assertIn(required_text, workflow)
                self.assertIn(required_text, spec)

        self.assertIn("agent_type: unity_developer", agents_rules)
        self.assertIn('fork_turns: "none"', agents_rules)

    def test_compile과_사람_기능_검증을_구분한다(self) -> None:
        config = (
            REPO_ROOT / ".codex/agents/unity_developer.toml"
        ).read_text(encoding="utf-8")
        workflow = (
            REPO_ROOT / "docs/workflows/unity_development.md"
        ).read_text(encoding="utf-8")
        report = (
            REPO_ROOT / "docs/templates/unity_implementation_report.md"
        ).read_text(encoding="utf-8")

        self.assertIn("컴파일 성공은 기능 성공이 아니다", workflow)
        self.assertIn("needs_human_test", workflow)
        self.assertIn("사람 확인 대기", report)
        self.assertIn("Never claim", config)
        self.assertIn("Do not use `eval` or `eval_file`", config)

    def test_Unity_자동_기능_검증은_기본적으로_사람에게_인계한다(self) -> None:
        config = (
            REPO_ROOT / ".codex/agents/unity_developer.toml"
        ).read_text(encoding="utf-8")
        workflow = (
            REPO_ROOT / "docs/workflows/unity_development.md"
        ).read_text(encoding="utf-8")
        spec = (
            REPO_ROOT / "docs/templates/unity_development_spec.md"
        ).read_text(encoding="utf-8")
        report = (
            REPO_ROOT / "docs/templates/unity_implementation_report.md"
        ).read_text(encoding="utf-8")
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

        for required_text in (
            "compile 성공",
            "새 Console error 0",
            "Editor 정상 상태",
            "Play Mode 진입",
            "입력 실행",
            "해상도별 캡처",
            "검증 전용 Editor code",
            "사용자의 명시적 요청",
            "보고한 문제를 재현·진단",
        ):
            with self.subTest(text=required_text):
                self.assertIn(required_text, workflow)

        self.assertIn("Do not enter Play Mode", config)
        self.assertIn("explicit user request", config)
        self.assertIn(
            "자동 Play Mode·입력·화면 검증: `아니요 | 예`",
            spec,
        )
        self.assertIn(
            "자동 Play Mode·입력·화면 검증 수행: `아니요 | 예`",
            report,
        )
        self.assertIn("자동으로 검증하지 않은 항목", report)
        self.assertIn("기본 자동 검증은 compile과 신규 Console 오류 확인", readme)

    def test_Unity_preflight와_개발_등급_기술_통합_결정이_명세에_연결된다(self) -> None:
        workflow = (
            REPO_ROOT / "docs/workflows/unity_development.md"
        ).read_text(encoding="utf-8")
        spec = (
            REPO_ROOT / "docs/templates/unity_development_spec.md"
        ).read_text(encoding="utf-8")

        for required_text in (
            "implementation run을 만들기 전의 preflight",
            "실행 ID와 backup root를 발급",
            "mutation 전 preflight 실패",
            "connection_test | prototype | production",
            "package 기본 resource",
            "existing_scene | standalone_scene | additive_scene",
            "근거 없이 기존 시작 scene을 제거",
        ):
            with self.subTest(text=required_text):
                self.assertIn(required_text, workflow)

        for required_text in (
            "개발 등급: `connection_test | prototype | production`",
            "## Technical Preflight",
            "scene 통합 방식",
            "Build Settings·시작 scene 변경",
            "mutation 없는 preflight 결과: `pass | blocked`",
            "preflight 전 미발급",
        ):
            with self.subTest(text=required_text):
                self.assertIn(required_text, spec)

    def test_Editor_도구는_필요성을_판단하고_snapshot_후_정리한다(self) -> None:
        config = (
            REPO_ROOT / ".codex/agents/unity_developer.toml"
        ).read_text(encoding="utf-8")
        workflow = (
            REPO_ROOT / "docs/workflows/unity_development.md"
        ).read_text(encoding="utf-8")
        spec = (
            REPO_ROOT / "docs/templates/unity_development_spec.md"
        ).read_text(encoding="utf-8")
        report = (
            REPO_ROOT / "docs/templates/unity_implementation_report.md"
        ).read_text(encoding="utf-8")

        for required_text in (
            "공식 MCP에 동일 목적의 전용 명령",
            "대량 반복, 데이터 parsing·변환",
            "경계가 애매하면 MCP 직접 사용",
            "temporary_tool",
            "retained_editor_tool",
            "나중에 쓸 수도 있음",
            "Assets/Editor/GamePMTemp/<run_id>/",
            "/temporary-tools/",
            "source와 meta",
            "최종 compile은 이 삭제 이후",
        ):
            with self.subTest(text=required_text):
                self.assertIn(required_text, workflow)

        self.assertIn("Prefer a dedicated official MCP operation", config)
        self.assertIn("confirmed repeat use", config)
        self.assertIn("## Editor Tool Policy", spec)
        self.assertIn("## Editor Tools", report)
        self.assertIn("source snapshot·SHA-256", report)
        self.assertIn("남아 있는 run 전용 임시 도구 경로", report)

    def test_Unity_보고서는_대량_생성과_사람_회신을_간결하게_기록한다(self) -> None:
        workflow = (
            REPO_ROOT / "docs/workflows/unity_development.md"
        ).read_text(encoding="utf-8")
        report = (
            REPO_ROOT / "docs/templates/unity_implementation_report.md"
        ).read_text(encoding="utf-8")

        self.assertIn("반복 조회하지 않는다", workflow)
        self.assertIn("보고가 누락되거나 서로 모순", workflow)
        self.assertIn("신규 subtree의 root·파일 수", workflow)
        self.assertIn("## Generated Subtrees", report)
        self.assertIn("정렬된 manifest SHA-256", report)
        self.assertIn("### 사용자 회신 양식", report)
        self.assertIn("결과: 성공 | 문제 있음", report)
        self.assertIn("성공으로 확정해줘", report)

    def test_코드는_Unity에만_두고_보고서는_해시를_관리한다(self) -> None:
        workflow = (
            REPO_ROOT / "docs/workflows/unity_development.md"
        ).read_text(encoding="utf-8")
        report = (
            REPO_ROOT / "docs/templates/unity_implementation_report.md"
        ).read_text(encoding="utf-8")

        self.assertIn("전체 코드 복사본을 저장하지 않는다", workflow)
        self.assertIn("변경 전 SHA-256", report)
        self.assertIn("변경 후 SHA-256", report)
        self.assertIn("backup 보존 기한", report)
        self.assertIn("30일", workflow)

    def test_Unity_프로젝트는_공통_상위_폴더_아래_프로젝트별로_생성된다(self) -> None:
        workflow = (
            REPO_ROOT / "docs/workflows/unity_development.md"
        ).read_text(encoding="utf-8")
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

        for required_text in (
            '"projects_root"',
            '"projects"',
            "unity templates list",
            "unity projects create",
            "빈 폴더만 만들고 연결하지 않는다",
            "Assets/",
            "Packages/manifest.json",
            "ProjectSettings/",
            "사용자가 별도로 요청하지 않은 Git·원격 저장소",
        ):
            with self.subTest(text=required_text):
                self.assertIn(required_text, workflow)

        self.assertIn("공통 상위 폴더 아래에서 프로젝트별 하위 폴더", readme)
        self.assertIn("빈 폴더만 MCP 대상으로 지정하지 않으며", readme)

    def test_다른_Unity_프로젝트는_MCP_경로를_자동_전환하고_새_작업에서_검증한다(self) -> None:
        agents_rules = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        config = (
            REPO_ROOT / ".codex/agents/unity_developer.toml"
        ).read_text(encoding="utf-8")
        workflow = (
            REPO_ROOT / "docs/workflows/unity_development.md"
        ).read_text(encoding="utf-8")
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

        for required_text in (
            'unity mcp configure codex --project-path "<unity_project_root>" --yes',
            "codex mcp get unity --json",
            "현재 tool namespace",
            "새 Codex 작업(새 채팅)",
            "새 작업에서도 이전 대상이 남아 있을 때만",
            "어떤 구현 mutation도 수행하지 않는다",
        ):
            with self.subTest(text=required_text):
                self.assertIn(required_text, workflow)

        self.assertIn("MCP 대상을 전환한다", agents_rules)
        self.assertIn("exactly\n  match the resolved local Unity project root", config)
        self.assertIn("Codex MCP 경로를 자동으로 변경한다", readme)

    def test_Unity_등급_계약과_준수_보고_필드가_연결된다(self) -> None:
        workflow = (
            REPO_ROOT / "docs/workflows/unity_development.md"
        ).read_text(encoding="utf-8")
        spec = (
            REPO_ROOT / "docs/templates/unity_development_spec.md"
        ).read_text(encoding="utf-8")
        report = (
            REPO_ROOT / "docs/templates/unity_implementation_report.md"
        ).read_text(encoding="utf-8")
        config = (
            REPO_ROOT / ".codex/agents/unity_developer.toml"
        ).read_text(encoding="utf-8")

        for required_text in (
            "작업 유형: `implement | cleanup`",
            "등급 선정 근거",
            "## Development Level Contract",
            "보존 정책: `preserve_until_explicit_cleanup`",
            "정리 그룹: `connection_test | prototype | none`",
            "## Artifact Cleanup",
        ):
            with self.subTest(text=required_text):
                self.assertIn(required_text, spec)

        for required_text in (
            "## Development Level Compliance",
            "등급 계약 결과: `pass | blocked`",
            "전용 소유 파일·폴더",
            "기존 공용 파일 변경",
            "산출물 상태: `active | promoted | removed | blocked`",
            "사람 확인 대기 항목",
        ):
            with self.subTest(text=required_text):
                self.assertIn(required_text, report)

        self.assertIn("prototype 전용 경로나 미승인 placeholder", workflow)
        self.assertIn("새 production 명세·실행", workflow)
        self.assertIn("never silently\n  promote a prototype", config)

    def test_Unity_ready_명세의_등급별_필수_계약을_검증한다(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            valid_spec = root / "valid-prototype.md"
            valid_spec.write_text(
                "# DEV Test\n\n"
                "## Metadata\n\n"
                "- 작업 유형: `implement`\n"
                "- 개발 등급: `prototype`\n"
                "- 등급 선정 근거: 기능 흐름 확인\n"
                "- 상태: `ready`\n\n"
                "## Unity Context\n\n"
                "- scene 통합 방식: `standalone_scene`\n"
                "- Build Settings·시작 scene 변경: `없음`\n\n"
                "## Technical Preflight\n\n"
                "- MCP tool namespace·Editor ready·대상 경로·Pipeline: 공식 MCP와 대상 경로 일치\n"
                "- mutation 없는 preflight 결과: `pass`\n\n"
                "## Development Level Contract\n\n"
                "- 산출물 분류: `prototype`\n"
                "- 통합 방식: `isolated`\n"
                "- 생성·수정할 전용 경로: `Assets/GamePM/Prototypes/DEV-TEST/`\n"
                "- 기존 공용 파일 수정 목록: `없음`\n"
                "- placeholder 목록: 임시 버튼\n"
                "- placeholder 허용·교체 조건: prototype 폐기 시 제거하고 실제 에셋으로 교체\n"
                "- 보존 정책: `preserve_until_explicit_cleanup`\n"
                "- 정리 그룹: `prototype`\n"
                "- 승격 조건: 새 production 명세와 실행을 생성\n"
                "- 등급별 완료 조건: compile 성공과 사람 확인 대기\n\n"
                "## Artifact Cleanup\n\n"
                "- 정리 대상 artifact index 항목: `해당 없음`\n"
                "- 원본 구현 보고서: `해당 없음`\n"
                "- 현재 SHA-256·후속 실행 의존성 재확인: `해당 없음`\n"
                "- 정리 허용 범위: `해당 없음`\n"
                "- 차단 항목 처리: `해당 없음`\n\n"
                "## Handoff\n\n"
                "- 실행 ID: `DEV-20260817-001-RUN-001`\n",
                encoding="utf-8",
            )
            self.assertEqual(
                [],
                validate_unity_development_spec(valid_spec),
                format_issues(validate_unity_development_spec(valid_spec)),
            )

            invalid_spec = root / "invalid-prototype.md"
            invalid_spec.write_text(
                valid_spec.read_text(encoding="utf-8")
                .replace("prototype 폐기 시 제거하고 실제 에셋으로 교체", "해당 없음")
                .replace("새 production 명세와 실행을 생성", "해당 없음"),
                encoding="utf-8",
            )
            codes = {
                issue.code for issue in validate_unity_development_spec(invalid_spec)
            }
            self.assertIn("incomplete-unity-prototype-lifecycle", codes)

    def test_새_Unity_기록은_전체_프로젝트_무결성_검사에_포함된다(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            fixture = WorkspaceFixture(Path(temporary_directory)).create()
            spec_path = (
                fixture.project_root
                / "development/specs/DEV-20260817-001-incomplete.md"
            )
            report_path = (
                fixture.project_root
                / "development/runs/DEV-20260817-001-RUN-001.md"
            )
            spec_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.parent.mkdir(parents=True, exist_ok=True)
            spec_path.write_text("# Incomplete Spec\n", encoding="utf-8")
            report_path.write_text("# Incomplete Report\n", encoding="utf-8")

            codes = {
                issue.code
                for issue in validate_project_structure(fixture.project, fixture.root)
            }
            self.assertIn("missing-unity-level-contract-field", codes)
            self.assertIn("missing-unity-level-compliance-field", codes)

    def test_Unity_draft와_blocked는_RUN_미발급이면_미완성을_허용한다(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            for status in ("draft", "blocked"):
                spec_path = root / f"{status}.md"
                spec_path.write_text(
                    "# Incomplete Spec\n\n"
                    f"- 상태: `{status}`\n"
                    "- mutation 없는 preflight 결과: `blocked`\n"
                    "- 실행 ID: `preflight 전 미발급`\n",
                    encoding="utf-8",
                )
                with self.subTest(status=status):
                    self.assertEqual(
                        [],
                        validate_unity_development_spec(spec_path),
                        format_issues(validate_unity_development_spec(spec_path)),
                    )

            minimal_blocked = root / "minimal-blocked.md"
            minimal_blocked.write_text(
                "# Incomplete Spec\n\n- 상태: `blocked`\n",
                encoding="utf-8",
            )
            self.assertEqual(
                [],
                validate_unity_development_spec(minimal_blocked),
                format_issues(validate_unity_development_spec(minimal_blocked)),
            )

    def test_Unity_preflight_통과_전에는_RUN_ID를_발급할_수_없다(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            spec_path = Path(temporary_directory) / "blocked-with-run.md"
            spec_path.write_text(
                "# Blocked Spec\n\n"
                "- 상태: `blocked`\n"
                "- mutation 없는 preflight 결과: `blocked`\n"
                "- 실행 ID: `DEV-20260817-001-RUN-001`\n",
                encoding="utf-8",
            )
            codes = {
                issue.code for issue in validate_unity_development_spec(spec_path)
            }
            self.assertIn("unity-run-issued-before-preflight", codes)
            self.assertIn("unity-blocked-preflight-has-run", codes)

    def test_Unity_ready_명세는_Scene과_Build_Settings_결정을_요구한다(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            valid_spec = root / "valid.md"
            valid_spec.write_text(
                self._complete_unity_spec_text(),
                encoding="utf-8",
            )
            self.assertEqual(
                [],
                validate_unity_development_spec(valid_spec),
                format_issues(validate_unity_development_spec(valid_spec)),
            )

            invalid_scene = root / "invalid-scene.md"
            invalid_scene.write_text(
                self._complete_unity_spec_text().replace(
                    "`standalone_scene`", "`unknown_scene_mode`"
                ),
                encoding="utf-8",
            )
            self.assertIn(
                "invalid-unity-scene-integration",
                {
                    issue.code
                    for issue in validate_unity_development_spec(invalid_scene)
                },
            )

            missing_build_settings = root / "missing-build-settings.md"
            missing_build_settings.write_text(
                self._complete_unity_spec_text().replace(
                    "- Build Settings·시작 scene 변경: `없음`",
                    "- Build Settings·시작 scene 변경:",
                ),
                encoding="utf-8",
            )
            self.assertIn(
                "missing-unity-build-settings-decision",
                {
                    issue.code
                    for issue in validate_unity_development_spec(
                        missing_build_settings
                    )
                },
            )

    def test_Unity_preflight_pass는_연결_근거를_요구한다(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            spec_path = Path(temporary_directory) / "missing-evidence.md"
            spec_path.write_text(
                self._complete_unity_spec_text().replace(
                    "공식 MCP·ready·정확한 경로·연결됨",
                    "",
                ),
                encoding="utf-8",
            )
            codes = {
                issue.code for issue in validate_unity_development_spec(spec_path)
            }
            self.assertIn("missing-unity-preflight-evidence", codes)

    def test_Unity_cleanup은_not_applicable_Scene과_변경없음을_허용한다(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            spec_path = Path(temporary_directory) / "cleanup.md"
            spec_path.write_text(
                self._complete_unity_spec_text()
                .replace("- 작업 유형: `implement`", "- 작업 유형: `cleanup`")
                .replace("`connection_test`", "`prototype`")
                .replace("공식 MCP 연결 확인", "prototype 정리")
                .replace("`standalone_scene`", "`not_applicable`")
                .replace(
                    "`Assets/GamePM/ConnectionTests/DEV-TEST/`",
                    "`Assets/GamePM/Prototypes/DEV-TEST/`",
                )
                .replace(
                    "- placeholder 허용·교체 조건: `해당 없음`",
                    "- placeholder 허용·교체 조건: 정리 시 전용 placeholder 제거",
                )
                .replace(
                    "- 승격 조건: `해당 없음`",
                    "- 승격 조건: 새 production 명세와 실행 필요",
                )
                + "- 정리 대상 artifact index 항목: `DEV-20260817-000-RUN-001`\n"
                "- 원본 구현 보고서: `development/runs/DEV-20260817-000-RUN-001.md`\n"
                "- 현재 SHA-256·후속 실행 의존성 재확인: `pass`\n"
                "- 정리 허용 범위: 전용 prototype 파일 제거\n"
                "- 차단 항목 처리: 해시 불일치 항목 보존 후 blocked 보고\n",
                encoding="utf-8",
            )
            self.assertEqual(
                [],
                validate_unity_development_spec(spec_path),
                format_issues(validate_unity_development_spec(spec_path)),
            )

    def test_Unity_RUN은_대응_명세와_passed_preflight를_요구한다(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            project_root = Path(temporary_directory)
            specs_root = project_root / "development/specs"
            runs_root = project_root / "development/runs"
            specs_root.mkdir(parents=True)
            runs_root.mkdir(parents=True)

            spec_path = specs_root / "DEV-20260817-001-blocked.md"
            spec_path.write_text(
                "# Blocked Spec\n\n"
                "- 상태: `blocked`\n"
                "- mutation 없는 preflight 결과: `blocked`\n"
                "- 실행 ID: `preflight 전 미발급`\n",
                encoding="utf-8",
            )
            report_path = runs_root / "DEV-20260817-001-RUN-001.md"
            report_path.write_text("# Run\n", encoding="utf-8")

            codes = {
                issue.code
                for issue in validate_unity_development_run_links(project_root)
            }
            self.assertIn("unity-run-without-passed-preflight", codes)

            report_without_spec = runs_root / "DEV-20260817-002-RUN-001.md"
            report_without_spec.write_text("# Run\n", encoding="utf-8")
            codes = {
                issue.code
                for issue in validate_unity_development_run_links(project_root)
            }
            self.assertIn("unity-run-without-development-spec", codes)

    def test_Unity_production과_cleanup의_보호_조건을_검증한다(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            spec_path = Path(temporary_directory) / "unsafe-production-cleanup.md"
            spec_path.write_text(
                "# DEV Test\n\n"
                "- 작업 유형: `cleanup`\n"
                "- 개발 등급: `production`\n"
                "- 등급 선정 근거: 실제 적용\n"
                "- 산출물 분류: `production`\n"
                "- 통합 방식: `shared_integration`\n"
                "- 생성·수정할 전용 경로: `Assets/GamePM/Prototypes/DEV-TEST/`\n"
                "- 기존 공용 파일 수정 목록: `없음`\n"
                "- placeholder 목록: 임시 이미지\n"
                "- placeholder 허용·교체 조건: `해당 없음`\n"
                "- 보존 정책: `preserve_until_explicit_cleanup`\n"
                "- 정리 그룹: `none`\n"
                "- 승격 조건: `해당 없음`\n"
                "- 등급별 완료 조건: compile 성공\n"
                "- 정리 대상 artifact index 항목: `해당 없음`\n"
                "- 원본 구현 보고서: `해당 없음`\n"
                "- 현재 SHA-256·후속 실행 의존성 재확인: `해당 없음`\n"
                "- 정리 허용 범위: `해당 없음`\n"
                "- 차단 항목 처리: `해당 없음`\n",
                encoding="utf-8",
            )
            codes = {
                issue.code for issue in validate_unity_development_spec(spec_path)
            }
            self.assertIn("production-uses-prototype-path", codes)
            self.assertIn("production-placeholder-forbidden", codes)
            self.assertIn("production-bulk-cleanup-forbidden", codes)
            self.assertIn("incomplete-unity-cleanup-contract", codes)

    def test_Unity_보고서와_산출물_색인의_등급_일관성을_검증한다(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            report_path = root / "report.md"
            report_path.write_text(
                "# Report\n\n"
                "- 작업 유형: `implement`\n"
                "- 요청 개발 등급: `prototype`\n"
                "- 실제 적용 등급: `prototype`\n"
                "- 등급 계약 결과: `pass`\n"
                "- 산출물 분류: `prototype`\n"
                "- 정리 그룹: `prototype`\n"
                "- 소유 방식: `isolated`\n"
                "- 전용 소유 파일·폴더: `Assets/GamePM/Prototypes/DEV-TEST/`\n"
                "- 기존 공용 파일 변경: `없음`\n"
                "- 남아 있는 placeholder: 임시 버튼·production에서 교체\n"
                "- 산출물 상태: `active`\n"
                "- 보존 또는 정리 근거: 사용자 명시적 정리 전 보존\n"
                "- 실제 자동 검증 수행: `아니요`\n"
                "- 사람 확인 대기 항목: 버튼 동작\n",
                encoding="utf-8",
            )
            self.assertEqual(
                [],
                validate_unity_implementation_report(report_path),
                format_issues(validate_unity_implementation_report(report_path)),
            )

            index_path = root / "artifact_index.md"
            index_path.write_text(
                "# Unity Artifact Index\n\n"
                "- 보존 정책: `preserve_until_explicit_cleanup`\n\n"
                "## Artifacts\n\n"
                "| 실행 ID | 작업 유형 | 개발 등급 | 정리 그룹 | Unity project ref | 소유 방식 | 구현 보고서 | manifest | 상태 | 정리 실행 |\n"
                "|---|---|---|---|---|---|---|---|---|---|\n"
                "| RUN-001 | implement | prototype | prototype | unity-ref | isolated | report.md | Changes | active | 없음 |\n",
                encoding="utf-8",
            )
            self.assertEqual(
                [],
                validate_unity_artifact_index(index_path),
                format_issues(validate_unity_artifact_index(index_path)),
            )

            index_path.write_text(
                index_path.read_text(encoding="utf-8").replace(
                    "| prototype | prototype |", "| production | prototype |"
                ),
                encoding="utf-8",
            )
            codes = {issue.code for issue in validate_unity_artifact_index(index_path)}
            self.assertIn("unity-index-cleanup-group-mismatch", codes)

    def test_Unity_산출물은_명시적_요청과_hash_검증_후에만_정리한다(self) -> None:
        workflow = (
            REPO_ROOT / "docs/workflows/unity_development.md"
        ).read_text(encoding="utf-8")
        index_template = (
            REPO_ROOT / "docs/templates/unity_artifact_index.md"
        ).read_text(encoding="utf-8")
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        current_index = (
            REPO_ROOT
            / "workspace/projects/chronicles-of-the-twelve-bonds/development/artifact_index.md"
        )

        for required_text in (
            "폴더명 검색만으로 삭제 대상을 정하지 않는다",
            "현재 SHA-256",
            "production 의존성을 재확인",
            "삭제하지 않고 색인에 `blocked`",
            "원본 보고서는 보존",
        ):
            with self.subTest(text=required_text):
                self.assertIn(required_text, workflow)

        self.assertIn("사용자의 명시적 정리 요청 전", index_template)
        self.assertIn("prototype을 전부 삭제해줘", readme)
        self.assertEqual(
            [],
            validate_unity_artifact_index(current_index),
            format_issues(validate_unity_artifact_index(current_index)),
        )


class BehaviorTestContractTests(unittest.TestCase):
    def test_동작_테스트_출처와_격리_규칙이_연결되어_있다(self) -> None:
        agents_rules = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        workflow = (
            REPO_ROOT / "docs/workflows/behavior_testing.md"
        ).read_text(encoding="utf-8")
        packet_template = (
            REPO_ROOT / "docs/templates/specialist_task_packet.md"
        ).read_text(encoding="utf-8")

        for required_text in (
            "[TEST FIXTURE: SYNTHETIC]",
            "synthetic_test_fixture",
            "blocked_test_provenance",
            "tests/fixtures/behavior/sample-game/",
            "데이터 출처",
            "실행 환경",
            "원본 변경",
            "실제 프로젝트 사실로 채택",
        ):
            with self.subTest(text=required_text):
                self.assertIn(required_text, agents_rules)
                self.assertIn(required_text, workflow)

        self.assertIn("사실·입력 출처", packet_template)
        self.assertIn("테스트 픽스처 가정", packet_template)
        self.assertIn("current_user_input", packet_template)
        self.assertIn("confirmed_document", packet_template)

    def test_전문_에이전트는_공통_테스트_출처_계약을_참조한다(self) -> None:
        handoff = (
            REPO_ROOT / "docs/workflows/specialist_agent_handoff.md"
        ).read_text(encoding="utf-8")

        for required_text in (
            "blocked_test_provenance",
            "[TEST FIXTURE: SYNTHETIC]",
            "test_fixture_assumption",
            "synthetic_test_fixture",
        ):
            with self.subTest(shared_provenance=required_text):
                self.assertIn(required_text, handoff)

        for agent_name in (
            "design_creative_planner",
            "design_creative_reviewer",
            "scenario_designer",
            "scenario_reviewer",
            "scenario_writer",
        ):
            with self.subTest(agent=agent_name):
                agent_config = (
                    REPO_ROOT / f".codex/agents/{agent_name}.toml"
                ).read_text(encoding="utf-8")

                self.assertIn("blocked_test_provenance", agent_config)
                self.assertIn(
                    "docs/workflows/specialist_agent_handoff.md",
                    agent_config,
                )
                self.assertNotIn("[TEST FIXTURE: SYNTHETIC]", agent_config)
                self.assertNotIn("test_fixture_assumption", agent_config)
                self.assertNotIn("synthetic_test_fixture", agent_config)

    def test_사용자_보고에서_합성_설정을_사용자_사실로_부르지_않는다(
        self,
    ) -> None:
        workflow = (
            REPO_ROOT / "docs/workflows/behavior_testing.md"
        ).read_text(encoding="utf-8")

        self.assertIn(
            "“사용자가 제공한 설정”이 아니라 “테스트\n"
            "픽스처 가정에 대한 출력”",
            workflow,
        )


if __name__ == "__main__":
    unittest.main()
