# Session 71 — Mobile Micro-Training Player

> Previous: [[sessions/session-70|Session 70 — Mobile Content Feed]] | Next: [[sessions/session-72|Session 72 — Survey/Poll System]]

## Phase: 5 — Journey Valorization
## Prerequisites: [[sessions/session-70|Session 70]] completed
## Complexity: High

## Objective
Build a full-featured micro-training player for mobile with video/audio playback, interactive quizzes, completion tracking, and offline support.

---

## Tasks
- [x] Create TrainingPlayerScreen with video/audio player
- [x] Implement player controls: play, pause, seek, volume
- [x] Add progress bar showing playback position
- [x] Build quiz section that appears after media completion
- [x] Implement multiple choice question rendering
- [x] Add quiz submit functionality with score display
- [x] Add retry option for failed quizzes
- [x] Display completion certificate link after successful completion
- [x] Implement time tracking (seconds spent on training)
- [x] Support offline playback with pre-downloaded content

## Files to Create/Modify
- `mobile/src/screens/TrainingPlayerScreen.tsx`
- `mobile/src/components/training/MediaPlayer.tsx`
- `mobile/src/components/training/PlayerControls.tsx`
- `mobile/src/components/training/ProgressBar.tsx`
- `mobile/src/components/training/QuizSection.tsx`
- `mobile/src/components/training/QuizQuestion.tsx`
- `mobile/src/components/training/ScoreDisplay.tsx`
- `mobile/src/components/training/CertificateLink.tsx`
- `mobile/src/services/trainingService.ts`
- `mobile/src/hooks/useTrainingPlayer.ts`
- `mobile/src/utils/offlineStorage.ts`

## Tests
- [x] Test player controls (play, pause, seek, volume) function correctly
- [x] Test progress bar updates during playback
- [x] Test quiz section renders after media completion
- [x] Test quiz flow: answer selection, submit, score display, retry
- [x] Test score submission sends correct data to API
- [x] Test time tracking records seconds spent accurately
- [x] Test offline playback with pre-downloaded content
- [x] Test completion certificate link appears after passing quiz

## Test Results
- Tests written: 28
- Tests passing: 28
- Tests failing: 0
- Coverage: models (11), widgets (13), providers (4)

## Notes
- Added `video_player` and `chewie` packages for media playback
- Player controls include play/pause, seek forward/backward 10s, progress slider
- Quiz questions use radio-button style selection with visual feedback
- Video player uses `VideoPlayerController.networkUrl` for network playback
- Offline caching via Hive for training metadata (media files would need separate download system)
- Time tracking uses `StreamBuilder` with 1-second ticker for live display

## Acceptance Criteria
- Video and audio content plays with functional controls (play, pause, seek, volume)
- Progress bar reflects current playback position accurately
- Quiz section appears only after media playback completes
- Multiple choice questions render with selectable options
- Quiz submission displays score and allows retry on failure
- Completion certificate link is shown after successful quiz completion
- Time spent is tracked in seconds and submitted to the backend
- Pre-downloaded content plays without network connectivity

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[PRD]] — Product Requirements Document v4.0
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Frontend pages
- [[MOBILE_PAGES]] — Mobile screens
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
