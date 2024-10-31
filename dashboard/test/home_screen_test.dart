import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:fintel/screens/home_screen.dart';

void main() {
  group('HomeScreen Tests', () {
    testWidgets('Loading indicator is shown during asset fetch',
        (WidgetTester tester) async {
      // Mock the HomeScreen with some sample assets
      final sampleAssets = ['appl', 'googl'];
      await tester.pumpWidget(MaterialApp(
          home: HomeScreen(
              assets: sampleAssets, hostname: 'localhost', port: '5000')));

      // Initially, loading indicator should be present
      expect(find.byType(CircularProgressIndicator), findsOneWidget);

      // Simulate a delay and then rebuild
      await tester.pump(const Duration(seconds: 2));
      await tester.pumpAndSettle();

      // After loading, loading indicator should not be present
      expect(find.byType(CircularProgressIndicator), findsNothing);
    });

    testWidgets('Assets Displayed', (WidgetTester tester) async {
      // Mock the HomeScreen with some sample assets
      final sampleAssets = ['appl', 'googl'];
      await tester.pumpWidget(MaterialApp(
          home: HomeScreen(
              assets: sampleAssets, hostname: 'localhost', port: '5000')));

      // Simulate fetching assets and rebuilding with sample data
      await tester.pumpAndSettle(); // Simulate waiting for the assets to load

      // Verify that the assets are displayed
      expect(find.text('appl'), findsOneWidget);
      expect(find.text('googl'), findsOneWidget);
    });
  });
}
