import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../widgets/app_scaffold.dart';
import '../screens/placeholder_screen.dart';
import '../screens/auth/splash_screen.dart';
import '../screens/auth/login_screen.dart';
import '../screens/onboarding/onboarding_flow.dart';
import '../screens/home/home_screen.dart';
import '../screens/trips/trip_booking_screen.dart';

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
            child: PlaceholderScreen(title: 'Trajets', icon: Icons.calendar_today_outlined),
          ),
          routes: [
            GoRoute(
              path: 'book',
              parentNavigatorKey: _rootNavigatorKey,
              builder: (context, state) => const TripBookingScreen(),
            ),
            GoRoute(
              path: ':id',
              parentNavigatorKey: _rootNavigatorKey,
              builder: (context, state) => PlaceholderScreen(
                title: 'Trajet ${state.pathParameters['id']}',
                icon: Icons.route,
              ),
            ),
            GoRoute(
              path: 'history',
              parentNavigatorKey: _rootNavigatorKey,
              builder: (context, state) => const PlaceholderScreen(
                title: 'Historique',
                icon: Icons.history,
              ),
            ),
          ],
        ),

        // Tracking tab
        GoRoute(
          path: '/tracking',
          pageBuilder: (context, state) => const NoTransitionPage(
            child: PlaceholderScreen(title: 'Suivi', icon: Icons.location_on_outlined),
          ),
          routes: [
            GoRoute(
              path: 'map',
              parentNavigatorKey: _rootNavigatorKey,
              builder: (context, state) => const PlaceholderScreen(
                title: 'Carte en direct',
                icon: Icons.map,
              ),
            ),
          ],
        ),

        // Content tab
        GoRoute(
          path: '/content',
          pageBuilder: (context, state) => const NoTransitionPage(
            child: PlaceholderScreen(title: 'Contenu', icon: Icons.article_outlined),
          ),
          routes: [
            GoRoute(
              path: ':id',
              parentNavigatorKey: _rootNavigatorKey,
              builder: (context, state) => PlaceholderScreen(
                title: 'Article ${state.pathParameters['id']}',
                icon: Icons.article,
              ),
            ),
            GoRoute(
              path: 'training/:id',
              parentNavigatorKey: _rootNavigatorKey,
              builder: (context, state) => PlaceholderScreen(
                title: 'Formation ${state.pathParameters['id']}',
                icon: Icons.school,
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
            child: PlaceholderScreen(title: 'Profil', icon: Icons.person_outline),
          ),
          routes: [
            GoRoute(
              path: 'edit',
              parentNavigatorKey: _rootNavigatorKey,
              builder: (context, state) => const PlaceholderScreen(
                title: 'Modifier le profil',
                icon: Icons.edit,
              ),
            ),
            GoRoute(
              path: 'preferences',
              parentNavigatorKey: _rootNavigatorKey,
              builder: (context, state) => const PlaceholderScreen(
                title: 'Préférences',
                icon: Icons.settings,
              ),
            ),
            GoRoute(
              path: 'security',
              parentNavigatorKey: _rootNavigatorKey,
              builder: (context, state) => const PlaceholderScreen(
                title: 'Sécurité',
                icon: Icons.shield_outlined,
              ),
            ),
          ],
        ),
      ],
    ),

    // Standalone screens (outside bottom nav)
    GoRoute(
      path: '/stats',
      builder: (context, state) =>
          const PlaceholderScreen(title: 'Statistiques', icon: Icons.bar_chart),
    ),
    GoRoute(
      path: '/emergency',
      builder: (context, state) =>
          const PlaceholderScreen(title: 'Urgence', icon: Icons.emergency),
    ),
    GoRoute(
      path: '/notifications',
      builder: (context, state) =>
          const PlaceholderScreen(title: 'Notifications', icon: Icons.notifications),
    ),
  ],
);
