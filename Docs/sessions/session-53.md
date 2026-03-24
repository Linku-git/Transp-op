# Session 53 — Profile & Preferences Screen

## Phase: 3 — Mobile MVP
## Prerequisites: [[sessions/session-47|Session 47]]
## Complexity: Low
> Previous: [[sessions/session-52|Session 52]] | Next: [[sessions/session-54|Session 54]]

## Objective
Create profile and preferences screens allowing users to view their information, edit personal details, and manage transport and notification preferences.

---

## Tasks
- [ ] Create ProfileScreen with:
  - [ ] Avatar, name, matricule, site, and shift display
  - [ ] Transport mode badge
  - [ ] Quick stats: total trips, CO2 saved, training modules completed
  - [ ] Menu items: Edit Profile, Preferences, Security, Notifications, Language, Night Mode, About, Logout
- [ ] Create EditProfileScreen: phone number, pickup address with map picker, PMR (reduced mobility) toggle
- [ ] Create PreferencesScreen: transport mode selector, walking distance slider, volunteer driver toggle, notification granularity settings, night mode toggle

## Files to Create/Modify
- `mobile/lib/screens/profile_screen.dart`
- `mobile/lib/screens/edit_profile_screen.dart`
- `mobile/lib/screens/preferences_screen.dart`
- `mobile/lib/widgets/profile_header.dart`
- `mobile/lib/widgets/quick_stats_row.dart`
- `mobile/lib/widgets/transport_mode_badge.dart`
- `mobile/lib/providers/profile_provider.dart`
- `mobile/lib/services/profile_service.dart`
- `mobile/lib/models/user_profile.dart`

## Tests
- [ ] ProfileScreen renders user info correctly (avatar, name, matricule, site, shift)
- [ ] Quick stats display correct values
- [ ] All menu items are visible and navigable
- [ ] EditProfileScreen saves changes to backend
- [ ] Map picker on EditProfileScreen allows selecting pickup address
- [ ] PreferencesScreen updates transport mode, walking distance, and other settings
- [ ] Logout clears session and navigates to login

## Acceptance Criteria
- Profile screen displays all user information accurately
- Transport mode badge reflects current selection
- Quick stats show up-to-date trip count, CO2 savings, and training progress
- All 8 menu items are accessible and navigate to their respective screens
- Edit profile allows updating phone, pickup address (via map), and PMR status
- Preferences screen allows changing transport mode, walking distance, volunteer status, notification settings, and night mode
- Changes are persisted to the backend immediately
- Logout fully clears the session and returns user to the login screen

---
## Related Documentation
- [[PROGRESS]] — Track session completion
- [[MOBILE_PAGES]] — Mobile screens
- [[LOCAL_MOBILE_FUNCTIONALITY]] — Offline strategy
- [[API_ENDPOINTS]] — API reference
- [[ARCHITECTURE]] — System architecture
- [[ROADMAP]] — Project timeline
- [[agents]] — Development workflow
