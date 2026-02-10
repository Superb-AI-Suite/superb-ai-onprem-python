# 배포 프로세스 (Release Process)

이 문서는 superb-ai-onprem-python SDK의 배포 프로세스를 설명합니다.

## 📋 전제 조건

- GitHub CLI (`gh`) 설치 및 인증 완료
- Git 설정 완료
- Repository에 대한 Push 권한
- Main 브랜치 머지 권한 (또는 PR 승인 권한)

## 🎯 빠른 배포 요청

배포가 필요할 때는 이 문서의 내용을 참고하여 다음과 같이 요청하세요:

**예시:**
```
"배포해줘. RELEASE_PROCESS.md 따라서"
```

또는 더 구체적으로:
```
"지금 변경사항 git add부터 release note 작성까지 배포 프로세스 진행해줘"
```

## 🚀 배포 단계

### 1. 변경사항 확인

```bash
git status
git diff
```

### 2. Feature Branch 생성 및 작업

```bash
# 새 기능 브랜치 생성
git checkout -b features/your-feature-name

# 또는 버그 수정
git checkout -b fix/your-fix-name
```

### 3. 변경사항 커밋

```bash
# 변경된 파일 추가
git add <files>

# 또는 모든 변경사항 추가
git add .

# 커밋 (의미있는 메시지 작성)
git commit -m "feat: Add new feature description"
# 또는
git commit -m "fix: Fix bug description"
```

**커밋 메시지 컨벤션:**
- `feat:` - 새로운 기능 추가
- `fix:` - 버그 수정
- `docs:` - 문서 변경
- `test:` - 테스트 코드 추가/수정
- `refactor:` - 코드 리팩토링
- `chore:` - 빌드 프로세스 또는 도구 변경

### 4. 테스트 실행

```bash
# 전체 테스트 실행
CLEANUP=1 RUN_MODEL_WORKFLOW_TESTS=1 pipenv run pytest tests/models/test_workflow.py -v

# 특정 테스트만 실행
pipenv run pytest tests/models/test_workflow.py::test_model_lifecycle_workflow -v
```

### 5. Branch Push 및 PR 생성

```bash
# Branch push
git push -u origin features/your-feature-name

# PR 본문을 echo로 작성 (권장 방법)
echo "## Summary" > /tmp/pr_body.md
echo "Your feature description" >> /tmp/pr_body.md
echo "" >> /tmp/pr_body.md
echo "## Changes" >> /tmp/pr_body.md
echo "- Change 1" >> /tmp/pr_body.md
echo "- Change 2" >> /tmp/pr_body.md
echo "" >> /tmp/pr_body.md
echo "## Testing" >> /tmp/pr_body.md
echo "- Test description" >> /tmp/pr_body.md

# PR 생성 (GitHub CLI 사용)
gh pr create --title "feat: Your feature title" --body-file /tmp/pr_body.md
```

**참고:** 
- **권장: echo 방식** - 긴 내용도 안정적으로 처리되며 터미널이 멈추지 않음
- PR 본문이 짧으면 `--body "..."` 직접 사용도 가능합니다
- ❌ `python3 -c` 방식은 긴 내용에서 터미널이 멈추거나 깨질 수 있어 권장하지 않음
- ❌ heredoc 방식도 터미널 출력 문제가 있어 피하는 것을 권장

⏸️ **여기서 잠시 멈춤! PR 생성 완료**

### 6. PR 리뷰 및 머지 (수동)

**사용자가 직접 수행:**
1. GitHub에서 PR 확인
2. 코드 리뷰
3. 필요시 추가 수정
4. PR 머지 실행

```bash
# GitHub에서 Merge 버튼 클릭
# 또는 CLI 사용
gh pr merge <PR번호> --squash
```

**머지 후 AI에게 알림:**
```
"머지했어" 또는 "다음 단계 진행해"
```

### 7. Main Branch 업데이트 (자동)

```bash
# Main branch로 이동
git checkout main

# 최신 변경사항 pull
git pull origin main
```

### 8. 버전 태그 생성

현재 버전 확인:
```bash
git tag -l | sort -V | tail -1
```

새 버전 태그 생성 (Semantic Versioning):
```bash
# Major version (호환성 깨지는 변경): v1.0.0 -> v2.0.0
# Minor version (새 기능 추가): v1.5.0 -> v1.6.0
# Patch version (버그 수정): v1.5.2 -> v1.5.3

git tag v1.6.1 -m "Release v1.6.1: Brief description"
```

**버전 번호 가이드:**
- **Major (X.0.0)**: API 호환성이 깨지는 변경
- **Minor (1.X.0)**: 하위 호환성 유지하면서 기능 추가
- **Patch (1.6.X)**: 버그 수정 및 사소한 개선

### 9. 태그 Push

```bash
git push origin v1.6.1
```

### 10. GitHub Release 생성

```bash
# 릴리즈 노트를 echo로 작성 (권장 방법)
echo "## 🎉 What's New in v1.6.1" > /tmp/release_notes.md
echo "" >> /tmp/release_notes.md
echo "### ✨ New Features" >> /tmp/release_notes.md
echo "- Feature 1" >> /tmp/release_notes.md
echo "- Feature 2" >> /tmp/release_notes.md
echo "" >> /tmp/release_notes.md
echo "### 🐛 Bug Fixes" >> /tmp/release_notes.md
echo "- Fix 1" >> /tmp/release_notes.md
echo "- Fix 2" >> /tmp/release_notes.md
echo "" >> /tmp/release_notes.md
echo "### 📝 Changes" >> /tmp/release_notes.md
echo "- Change 1" >> /tmp/release_notes.md
echo "- Change 2" >> /tmp/release_notes.md
echo "" >> /tmp/release_notes.md
echo "### 🔧 Technical Details" >> /tmp/release_notes.md
echo "**Modified Files:**" >> /tmp/release_notes.md
echo "- path/to/file1.py" >> /tmp/release_notes.md
echo "- path/to/file2.py" >> /tmp/release_notes.md
echo "" >> /tmp/release_notes.md
echo "### ✅ Testing" >> /tmp/release_notes.md
echo "- ✅ All tests passing" >> /tmp/release_notes.md
echo "- ✅ Manual testing completed" >> /tmp/release_notes.md
echo "" >> /tmp/release_notes.md
echo "### 🔄 Backward Compatibility" >> /tmp/release_notes.md
echo "This release is **100% backward compatible**." >> /tmp/release_notes.md
echo "" >> /tmp/release_notes.md
echo "---" >> /tmp/release_notes.md
echo "**Full Changelog**: https://github.com/Superb-AI-Suite/superb-ai-onprem-python/compare/v1.6.0...v1.6.1" >> /tmp/release_notes.md

# 릴리즈 생성 (파일 사용)
gh release create v1.6.1 --title "v1.6.1 - Release Title" --notes-file /tmp/release_notes.md
```

**참고:**
- **권장: echo 방식** - 긴 내용도 안정적으로 처리되며 터미널이 멈추지 않음
- 릴리즈 노트가 짧으면 `--notes "..."` 직접 사용도 가능합니다
- ❌ `python3 -c` 방식은 긴 내용에서 터미널이 멈추거나 깨질 수 있어 권장하지 않음

### 11. Release 확인

```bash
# 브라우저에서 릴리즈 페이지 열기
open https://github.com/Superb-AI-Suite/superb-ai-onprem-python/releases/tag/v1.6.1

# 또는 CLI로 확인
gh release view v1.6.1
```

## 📝 릴리즈 노트 템플릿

```markdown
## 🎉 What's New in vX.Y.Z

### ✨ New Features
- Feature description with details
- Another feature

### 🐛 Bug Fixes
- Bug fix description
- Another bug fix

### 📝 API Changes
\`\`\`python
# 코드 예제
from spb_onprem import ModelService

# 사용 예시
\`\`\`

### 🔧 Technical Details
**Modified Files:**
- \`file1.py\`
- \`file2.py\`

**Implementation Details:**
- Detail 1
- Detail 2

### ✅ Testing
- ✅ Test description
- ✅ Coverage details

### 🔄 Backward Compatibility
[호환성 여부 명시]

### 📚 Documentation
- Link to related docs

---
**Full Changelog**: https://github.com/Superb-AI-Suite/superb-ai-onprem-python/compare/vX.Y.Z-1...vX.Y.Z
```

## 🔧 트러블슈팅

### Main Branch가 Protected인 경우

Main branch에 직접 push가 불가능한 경우:
1. Feature branch 생성
2. PR 생성 및 머지
3. Main branch pull 후 태그 생성

### 태그를 잘못 생성한 경우

```bash
# 로컬 태그 삭제
git tag -d v1.6.1

# 원격 태그 삭제
git push origin :refs/tags/v1.6.1

# 올바른 태그 재생성
git tag v1.6.1 -m "Correct message"
git push origin v1.6.1
```

### Release를 수정해야 하는 경우

```bash
# Release 수정
gh release edit v1.6.1 --notes "Updated release notes"
```

## 📋 체크리스트

배포 전 확인사항:

- [ ] 모든 변경사항이 커밋되었는가?
- [ ] 테스트가 모두 통과하는가?
- [ ] PR이 리뷰되고 머지되었는가?
- [ ] Main branch가 최신 상태인가?
- [ ] 버전 번호가 Semantic Versioning을 따르는가?
- [ ] 릴리즈 노트에 모든 변경사항이 포함되었는가?
- [ ] 하위 호환성이 유지되는가?
- [ ] API 변경사항이 문서화되었는가?

## 🔗 유용한 링크

- [Semantic Versioning](https://semver.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [GitHub CLI Documentation](https://cli.github.com/manual/)
- [Repository Releases](https://github.com/Superb-AI-Suite/superb-ai-onprem-python/releases)

## 💡 팁

- 작은 단위로 자주 커밋하고 배포하는 것이 좋습니다
- 릴리즈 노트는 사용자 관점에서 작성합니다
- Breaking changes는 명확하게 표시합니다
- 예제 코드를 포함하면 사용자가 이해하기 쉽습니다

## 📚 실제 배포 케이스 스터디

### Case 1: 새로운 기능 추가 (v1.6.0)

**상황:** training_annotations와 contents validation 기능 추가

**진행 과정:**
1. Feature branch 생성: `features/add-annotation-statistics-field-to-the-model`
2. 코드 작성 및 테스트
3. Git add & commit
4. **AI가 PR 생성 (PR #69)**
5. **사용자가 GitHub에서 PR 리뷰 및 머지**
6. **사용자가 "머지했어"라고 알림**
7. **AI가 Main branch checkout & pull**
8. **AI가 버전 태그 생성: `v1.6.0` (Minor version up - 새 기능 추가)**
9. **AI가 태그 push**
10. **AI가 GitHub Release 생성 (새 기능 설명 포함)**

**배포 요청 예시:**
```
"training_annotations 기능 추가했어. PR 생성까지 해줘"
```
**PR 머지 후:**
```
"머지했어. v1.6.0으로 릴리즈 해줘"
```

### Case 2: 버그 수정 (v1.6.1)

**상황:** v1.6.0에서 GraphQL mutation에 파라미터 누락 발견

**진행 과정:**
1. Main branch 보호로 인해 직접 push 불가
2. Fix branch 생성: `fix/add-missing-graphql-parameters`
3. 수정 및 커밋
4. **AI가 PR 생성 (PR #70)**
5. **사용자가 GitHub에서 PR 리뷰 및 머지**
6. **사용자가 "다음 단계 진행해"라고 알림**
7. **AI가 Main branch checkout & pull**
8. **AI가 버전 태그 생성: `v1.6.1` (Patch version up - 버그 수정)**
9. **AI가 태그 push**
10. **AI가 GitHub Release 생성 (버그 수정 내용 명시)**

**배포 요청 예시:**
```
"GraphQL 파라미터 누락 수정했어. PR까지 만들어줘"
```
**PR 머지 후:**
```
"다음 단계 진행해"
```

### Case 3: Main Branch가 Protected인 경우

**상황:** Main branch에 직접 push가 막혀있음

**해결 방법:**
```bash
# 1. Feature/Fix branch 생성
git checkout -b fix/your-fix-name

# 2. 변경사항 커밋
git add .
git commit -m "fix: Description"

# 3. Branch push
git push -u origin fix/your-fix-name

# 4. PR 생성
gh pr create --title "fix: Title" --body "Description"

# ⏸️ 여기서 멈춤! 사용자가 PR 머지

# 5. 사용자가 PR 머지 후 "다음 단계 진행해"라고 알림

# 6. 버전 태그 및 릴리즈 생성 (이후 자동)
```

**배포 요청 예시:**
```
"수정 완료. PR 생성해줘"
```
**PR 머지 후:**
```
"머지했어. 릴리즈 해줘"
```

## 🤖 자동화된 배포 요청 방법

AI에게 배포를 요청할 때는 다음 형식을 사용하세요:

### 기본 요청 (PR 생성까지)
```
"배포해줘. RELEASE_PROCESS.md 따라서"
```

이렇게 요청하면:
1. AI가 PR 생성까지 자동 진행
2. PR 링크를 알려줌
3. **사용자가 GitHub에서 PR 리뷰 및 머지**
4. 머지 후 "머지했어" 또는 "다음 단계 진행해"라고 알림
5. AI가 버전 태그 및 릴리즈 생성

### 상세 요청
```
"[변경 내용 설명]. git add부터 PR 생성까지 진행해줘"
```

### PR 머지 후 릴리즈 요청
```
"PR 머지했어. 릴리즈 진행해줘"
```
또는
```
"다음 단계 진행해"
```

### 버전 지정 요청
```
"버그 수정했어. v1.6.3로 패치 릴리즈 해줘"
```

## 📝 AI가 자동으로 처리하는 것들

### Phase 1: PR 생성까지 (자동)
1. ✅ Git status 확인 및 변경사항 확인
2. ✅ 적절한 branch 생성 (필요시)
3. ✅ Git add 및 commit (적절한 메시지와 함께)
4. ✅ Branch push
5. ✅ PR 생성

### Phase 2: PR 머지 (수동 - 사용자가 직접)
6. ⏸️ **사용자가 GitHub에서 PR 리뷰 및 머지** (AI는 대기)
   - PR 확인 및 리뷰
   - 필요시 추가 수정
   - PR 머지 실행
   - AI에게 "머지했어" 또는 "다음 단계 진행해" 알림

### Phase 3: 릴리즈 생성 (자동)
7. ✅ Main branch 최신화
8. ✅ Semantic Versioning에 맞는 버전 태그 생성
9. ✅ 태그 push
10. ✅ 릴리즈 노트 자동 생성
11. ✅ GitHub Release 생성
12. ✅ 브라우저에서 릴리즈 페이지 열기

## 🎯 배포 완료 확인

배포가 완료되면 다음을 확인하세요:

1. ✅ GitHub Release 페이지에서 릴리즈 노트 확인
2. ✅ 버전 태그가 올바르게 생성되었는지 확인
3. ✅ Changelog가 정확한지 확인
4. ✅ 필요시 문서 업데이트
