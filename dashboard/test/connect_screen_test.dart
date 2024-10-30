import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:fintel/screens/connect_screen.dart';

void main() {
  group('ConnectScreen Tests', () {
    testWidgets('Default values are set correctly', (WidgetTester tester) async {
      await tester.pumpWidget(const MaterialApp(home: ConnectScreen()));

      // Verify default hostname and port values
      final hostnameField = find.byType(TextField).at(0); // Assuming hostname is the first TextField
      final portField = find.byType(TextField).at(1); // Assuming port is the second TextField

      // Verify that the values are empty by default.
      expect(tester.widget<TextField>(hostnameField).controller!.text, '');
      expect(tester.widget<TextField>(portField).controller!.text, '');
    });

    testWidgets('Invalid input prompts error dialog', (WidgetTester tester) async {
      await tester.pumpWidget(const MaterialApp(home: ConnectScreen()));

      // Tap the "Connect" button
      await tester.tap(find.text('Connect'));
      await tester.pumpAndSettle();

      // Verify that error dialog is displayed
      expect(find.text('Please enter a valid server address.'), findsOneWidget);
    });
  });
}