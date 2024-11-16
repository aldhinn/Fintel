import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/annotations.dart';
import 'package:fintel/screens/connect_screen.dart';
import 'package:http/http.dart' as http;

@GenerateMocks([http.Client])
void main() {
  group('ConnectScreen', () {
    testWidgets('renders ConnectScreen with inputs and button',
        (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(home: ConnectScreen()),
      );

      expect(find.text("Welcome to Fintel"), findsOneWidget);
      expect(find.text("Hostname (default: localhost)"), findsOneWidget);
      expect(find.text("Port (default: 61000)"), findsOneWidget);
      expect(find.text("Connect"), findsOneWidget);
    });

    testWidgets('displays error dialog on connection failure',
        (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(home: ConnectScreen()),
      );

      await tester.enterText(
          find.byKey(const Key('hostnameInput')), 'invalid-host');
      await tester.enterText(find.byKey(const Key('portInput')), '1234');
      await tester.tap(find.text('Connect'));

      await tester.pump(); // Allow UI to update.

      expect(find.text('Connection Error'), findsOneWidget);
      expect(find.text('Please enter a valid server address.'), findsOneWidget);
    });
  });
}
