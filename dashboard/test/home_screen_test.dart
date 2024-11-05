import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:fintel/screens/home_screen.dart';

void main() {
  group('HomeScreen Tests', () {
    testWidgets('Loading indicator is shown during asset symbols fetch',
        (WidgetTester tester) async {
      // Mock the HomeScreen with some sample asset symbols
      final sampleAssetSymbols = ['appl', 'googl'];
      await tester.pumpWidget(MaterialApp(
          home: HomeScreen(
              assetSymbols: sampleAssetSymbols,
              hostname: 'localhost',
              port: '61000')));

      // Initially, loading indicator should be present
      expect(find.byType(CircularProgressIndicator), findsOneWidget);

      // Simulate a delay and then rebuild
      await tester.pump(const Duration(seconds: 2));
      await tester.pumpAndSettle();

      // After loading, loading indicator should not be present
      expect(find.byType(CircularProgressIndicator), findsNothing);
    });

    testWidgets('Asset Symbols Displayed', (WidgetTester tester) async {
      // Mock the HomeScreen with some sample asset symbols
      final sampleAssetSymbols = ['appl', 'googl'];
      await tester.pumpWidget(MaterialApp(
          home: HomeScreen(
              assetSymbols: sampleAssetSymbols,
              hostname: 'localhost',
              port: '61000')));

      // Simulate fetching asset symbols and rebuilding with sample data
      await tester
          .pumpAndSettle(); // Simulate waiting for the asset symbols to load

      // Verify that the asset symbols are displayed
      expect(find.text('appl'), findsOneWidget);
      expect(find.text('googl'), findsOneWidget);
    });
  });
}
