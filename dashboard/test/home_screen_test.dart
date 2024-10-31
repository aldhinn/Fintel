import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:fintel/screens/home_screen.dart';

void main() {
  group('HomeScreen Tests', () {
    testWidgets('Loading indicator is shown during ticker fetch',
        (WidgetTester tester) async {
      // Mock the HomeScreen with some sample tickers
      final sampleTickers = ['appl', 'googl'];
      await tester.pumpWidget(MaterialApp(
          home: HomeScreen(
              tickers: sampleTickers, hostname: 'localhost', port: '5000')));

      // Initially, loading indicator should be present
      expect(find.byType(CircularProgressIndicator), findsOneWidget);

      // Simulate a delay and then rebuild
      await tester.pump(const Duration(seconds: 2));
      await tester.pumpAndSettle();

      // After loading, loading indicator should not be present
      expect(find.byType(CircularProgressIndicator), findsNothing);
    });

    testWidgets('Tickers Displayed', (WidgetTester tester) async {
      // Mock the HomeScreen with some sample tickers
      final sampleTickers = ['appl', 'googl'];
      await tester.pumpWidget(MaterialApp(
          home: HomeScreen(
              tickers: sampleTickers, hostname: 'localhost', port: '5000')));

      // Simulate fetching tickers and rebuilding with sample data
      await tester.pumpAndSettle(); // Simulate waiting for the tickers to load

      // Verify that the tickers are displayed
      expect(find.text('appl'), findsOneWidget);
      expect(find.text('googl'), findsOneWidget);
    });
  });
}
