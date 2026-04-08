import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../widgets/app_scaffold.dart';
import '../screens/placeholder_screen.dart';
import '../screens/auth/splash_screen.dart';
import '../screens/auth/login_screen.dart';
import '../screens/onboarding/onboarding_flow.dart';
import '../screens/home/home_screen.dart';
import '../screens/trips/trip_booking_screen.dart';
import '../screens/trips/trips_screen.dart';
import '../screens/trips/trip_detail_screen.dart';
import '../screens/trips/trip_history_screen.dart';
import '../screens/tracking/rti_tracking_screen.dart';
import '../screens/tracking/full_map_screen.dart';
import '../screens/notifications/notification_list_screen.dart';
import '../screens/profile/profile_screen.dart';
import '../screens/profile/edit_profile_screen.dart';
import '../screens/profile/preferences_screen.dart';
import '../screens/stats/statistics_screen.dart';
import '../screens/emergency/emergency_screen.dart';
import '../screens/profile/security_questionnaire_screen.dart';
import '../screens/content/content_feed_screen.dart';
import '../screens/content/content_detail_screen.dart';
import '../screens/content/training_player_screen.dart';

final _rootNavigatorKey = GlobalKey<NavigatorState>();
final _shellNavigatorKey = GlobalKey<NavigatorState>();

final GoRouter appRouter = GoRouter(
  navigatorKey: _rootNavigatorKey,
  initialLocation: '/splash',
  routes: [
    // Auth routes (outside shell)
    GoRoute(
      path: '/splash',
      builder: (context, state) => const SplashScreen(),
    ),
    GoRoute(
      path: '/login',
      builder: (context, state) => const LoginScreen(),
    ),
    GoRoute(
      path: '/onboarding',
      builder: (context, state) => const OnboardingFlow(),
    ),

    // Main app with bottom navigation
    ShellRoute(
      navigatorKey: _shellNavigatorKey,
      builder: (context, state, child) => AppScaffold(child: child),
      routes: [
        // Home tab
        GoRoute(
          path: '/home',
          pageBuilder: (context, state) => const NoTransitionPage(
            child: HomeScreen(),
          ),
        ),

        // Trips tab
        GoRoute(
          path: '/trips',
          pageBuilder: (context, state) => const NoTransitionPage(
            child: TripsScreen(),
          ),
          routes: [
            GoRoute(
              path: 'book',
              parentNavigatorKey: _rootNavigatorKey,
              builder: (context, state) => const TripBookingScreen(),
            ),
            GoRoute(
              path: 'history',
              parentNavigatorKey: _rootNavigatorKey,
              builder: (context, state) => const TripHistoryScreen(),
            ),
            GoRoute(
              path: ':id',
              parentNavigatorKey: _rootNavigatorKey,
              builder: (context, state) => TripDetailScreen(
                tripId: state.pathParameters['id']!,
              ),
            ),
          ],
        ),

        // Tracking tab
        GoRoute(
          path: '/tracking',
          pageBuilder: (context, state) => const NoTransitionPage(
            child: RTITrackingScreen(),
          ),
          routes: [
            GoRoute(
              path: 'map',
              parentNavigatorKey: _rootNavigatorKey,
              builder: (context, state) => const FullMapScreen(),
            ),
          ],
        ),

        // Content tab
        GoRoute(
          path: '/content',
          pageBuilder: (context, state) => const NoTransitionPage(
            child: ContentFeedScreen(),
          ),
          routes: [
            GoRoute(
              path: ':id',
              parentNavigatorKey: _rootNavigatorKey,
              builder: (context, state) => ContentDetailScreen(
                contentId: state.pathParameters['id']!,
              ),
            ),
            GoRoute(
              path: 'training/:id',
              parentNavigatorKey: _rootNavigatorKey,
              builder: (context, state) => TrainingPlayerScreen(
                contentId: state.pathParameters['id']!,
              ),
            ),
            GoRoute(
              path: 'survey/:id',
              parentNavigatorKey: _rootNavigatorKey,
              builder: (context, state) => PlaceholderScreen(
                title: 'Sondage ${state.pathParameters['id']}',
                icon: Icons.poll,
              ),
            ),
          ],
        ),

        // Profile tab
        GoRoute(
          path: '/profile',
          pageBuilder: (context, state) => const NoTransitionPage(
            child: ProfileScreen(),
          ),
          routes: [
            GoRoute(
              path: 'edit',
              parentNavigatorKey: _rootNavigatorKey,
              builder: (context, state) => const EditProfileScreen(),
            ),
            GoRoute(
              path: 'preferences',
              parentNavigatorKey: _rootNavigatorKey,
              builder: (context, state) => const PreferencesScreen(),
            ),
            GoRoute(
              path: 'security',
              parentNavigatorKey: _rootNavigatorKey,
              builder: (context, state) => const SecurityQuestionnaireScreen(),
            ),
          ],
        ),
      ],
    ),

    // Standalone screens (outside bottom nav)
    GoRoute(
      path: '/stats',
      builder: (context, state) => const StatisticsScreen(),
    ),
    GoRoute(
      path: '/emergency',
      builder: (context, state) => const EmergencyScreen(),
    ),
    GoRoute(
      path: '/notifications',
      builder: (context, state) => const NotificationListScreen(),
    ),
  ],
);
