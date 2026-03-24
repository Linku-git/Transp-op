# Session 71 — Mobile Micro-Training Player

> Previous: [[sessions/session-70|Session 70 — Mobile Content Feed]] | Next: [[sessions/session-72|Session 72 — Survey/Poll System]]

## Phase: 5 — Journey Valorization
## Prerequisites: [[sessions/session-70|Session 70]] completed
## Complexity: High

## Objective
Build a full-featured micro-training player for mobile with video/audio playback, interactive quizzes, completion tracking, and offline support.

---

## Tasks
- [ ] Create TrainingPlayerScreen with video/audio player
- [ ] Implement player controls: play, pause, seek, volume
- [ ] Add progress bar showing playback position
- [ ] Build quiz section that appears after media completion
- [ ] Implement multiple choice question rendering
- [ ] Add quiz submit functionality with score display
- [ ] Add retry option for failed quizzes
- [ ] Display completion certificate link after successful completion
- [ ] Implement time tracking (seconds spent on training)
- [ ] Support offline playback with pre-downloaded content

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
- [ ] Test player controls (play, pause, seek, volume) function correctly
- [ ] Test progress bar updates during playback
- [ ] Test quiz section renders after media completion
- [ ] Test quiz flow: answer selection, submit, score display, retry
- [ ] Test score submission sends correct data to API
- [ ] Test time tracking records seconds spent accurately
- [ ] Test offline playback with pre-downloaded content
- [ ] Test completion certificate link appears after passing quiz

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
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Frontend pages
- [[MOBILE_PAGES]] — Mobile screens
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
