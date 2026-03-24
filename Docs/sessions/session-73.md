# Session 73 — Mobile Survey Interface

> Previous: [[sessions/session-72|Session 72 — Survey/Poll System]] | Next: [[sessions/session-74|Session 74 — LMS Integration]]

## Phase: 5 — Journey Valorization
## Prerequisites: [[sessions/session-45|Session 45]], [[sessions/session-72|Session 72]] completed
## Complexity: Medium

## Objective
Build the mobile survey interface with dynamic question rendering, progress tracking, offline queuing, and anonymous survey support.

---

## Tasks
- [ ] Create SurveyScreen with survey title and description display
- [ ] Implement dynamic question rendering per type: radio (single choice), checkbox (multiple choice), text input, star rating (1-5), slider
- [ ] Add progress indicator showing current question number out of total (question X of Y)
- [ ] Add submit button with validation
- [ ] Display anonymous indicator when the survey is anonymous
- [ ] Create thank you confirmation screen after submission
- [ ] Implement offline queue: store responses locally if offline, submit automatically on reconnect

## Files to Create/Modify
- `mobile/src/screens/SurveyScreen.tsx`
- `mobile/src/screens/SurveyConfirmationScreen.tsx`
- `mobile/src/components/survey/RadioQuestion.tsx`
- `mobile/src/components/survey/CheckboxQuestion.tsx`
- `mobile/src/components/survey/TextQuestion.tsx`
- `mobile/src/components/survey/RatingQuestion.tsx`
- `mobile/src/components/survey/SliderQuestion.tsx`
- `mobile/src/components/survey/ProgressIndicator.tsx`
- `mobile/src/components/survey/AnonymousIndicator.tsx`
- `mobile/src/services/surveyService.ts`
- `mobile/src/hooks/useSurveyOfflineQueue.ts`
- `mobile/src/navigation/routes.ts`

## Tests
- [ ] Test radio question (single choice) renders and selects correctly
- [ ] Test checkbox question (multiple choice) renders and toggles correctly
- [ ] Test text question renders and accepts input
- [ ] Test star rating question renders 1-5 stars and captures selection
- [ ] Test slider question renders and captures value
- [ ] Test progress indicator shows correct question count
- [ ] Test submission flow from answers to confirmation screen
- [ ] Test offline queue stores response locally and submits on reconnect

## Acceptance Criteria
- Each question type renders with the appropriate input control
- Progress indicator accurately shows the current question position
- Submit button validates that required questions are answered
- Anonymous indicator is visible for anonymous surveys
- Confirmation screen displays after successful submission
- Offline responses are queued locally and automatically submitted when connectivity is restored

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[DATABASE_SCHEMA]] — Database tables
- [[API_ENDPOINTS]] — API reference
- [[FRONTEND_PAGES]] — Frontend pages
- [[MOBILE_PAGES]] — Mobile screens
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
