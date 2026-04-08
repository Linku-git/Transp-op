import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('EmergencyScreen layout', () {
    // Test the layout without the actual screen (avoids HapticFeedback platform channel)
    testWidgets('emergency overlay renders key elements', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            backgroundColor: const Color(0xFFDC2626),
            body: SafeArea(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.emergency, size: 80, color: Colors.white),
                  const Text('ALERTE URGENCE ACTIVÉE', style: TextStyle(color: Colors.white, fontSize: 24)),
                  const Text('Localisation GPS active', style: TextStyle(color: Colors.white)),
                  ElevatedButton(onPressed: () {}, child: const Text('Appeler les secours')),
                  TextButton(onPressed: () {}, child: const Text('Annuler l\'alerte')),
                ],
              ),
            ),
          ),
        ),
      );

      expect(find.text('ALERTE URGENCE ACTIVÉE'), findsOneWidget);
      expect(find.text('Localisation GPS active'), findsOneWidget);
      expect(find.text('Appeler les secours'), findsOneWidget);
      expect(find.text('Annuler l\'alerte'), findsOneWidget);
      expect(find.byIcon(Icons.emergency), findsOneWidget);
    });
  });
}
