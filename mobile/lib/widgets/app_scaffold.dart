import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'bottom_nav_bar.dart';

class AppScaffold extends StatelessWidget {
  final Widget child;

  const AppScaffold({super.key, required this.child});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: child,
      bottomNavigationBar: BottomNavBar(
        currentIndex: _calculateSelectedIndex(context),
        onTap: (index) => _onItemTapped(index, context),
      ),
    );
  }

  int _calculateSelectedIndex(BuildContext context) {
    final location = GoRouterState.of(context).uri.path;
    if (location.startsWith('/home')) return 0;
    if (location.startsWith('/trips')) return 1;
    if (location.startsWith('/tracking')) return 2;
    if (location.startsWith('/content')) return 3;
    if (location.startsWith('/profile')) return 4;
    return 0;
  }

  void _onItemTapped(int index, BuildContext context) {
    switch (index) {
      case 0:
        context.go('/home');
      case 1:
        context.go('/trips');
      case 2:
        context.go('/tracking');
      case 3:
        context.go('/content');
      case 4:
        context.go('/profile');
    }
  }
}
