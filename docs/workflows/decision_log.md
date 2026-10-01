# Decision Log Record

결정 기록의 생성 시점과 상태 연결은
`docs/workflows/approval_queue.md`가 소유한다. 기록 형식은
`docs/templates/decision_log_entry.md`만 사용하며 기존 항목을 덮어쓰지 않고
append-only로 추가한다.

저장 위치:
`workspace/projects/<project_slug>/decisions/decision_log.md`
