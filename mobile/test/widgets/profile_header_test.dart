import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:transpop_mobile/models/user_profile.dart';
import 'package:transpop_mobile/widgets/profile_header.dart';

void main() {
  final profile = UserProfile(
    id: '1',
    email: 'jean@test.com',
    firstName: 'Jean',
    lastName: 'Dupont',
    matricule: 'MAT-001',
    siteName: 'Ain Sebaa',
    shiftLabel: 'Poste 1',
    transportMode: 'voiture',
  );

  group('ProfileHeader', () {
    testWidgets('renders name and matricule', (tester) async {
      await tester.pumpWidget(
        MaterialApp(home: Scaffold(body: ProfileHeader(profile: profile))),
      );

      expect(find.text('Jean Dupont'), findsOneWidget);
      expect(find.text('Matricule: MAT-001'), findsOneWidget);
    });

    testWidgets('renders site and shift chips', (tester) async {
      await tester.pumpWidget(
        MaterialApp(home: Scaffold(body: ProfileHeader(profile: profile))),
      );

      expect(find.text('Ain Sebaa'), findsOneWidget);
      expect(find.text('Poste 1'), findsOneWidget);
    });

    testWidgets('renders transport mode badge', (tester) async {
      await tester.pumpWidget(
        MaterialApp(home: Scaffold(body: ProfileHeader(profile: profile))),
      );

      expect(find.text('Voiture'), findsOneWidget);
    });

    testWidgets('renders initials in avatar', (tester) async {
      await tester.pumpWidget(
        MaterialApp(home: Scaffold(body: ProfileHeader(profile: profile))),
      );

      expect(find.text('JD'), findsOneWidget);
    });
  });

  group('TransportModeBadge', () {
    testWidgets('renders mode label', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(body: TransportModeBadge(mode: 'covoiturage')),
        ),
      );

      expect(find.text('Covoiturage'), findsOneWidget);
    });
  });
}
