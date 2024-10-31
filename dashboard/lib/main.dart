import 'package:flutter/material.dart';
import 'screens/connect_screen.dart';

/// Application entrypoint.
void main() {
  runApp(const FintelApp());
}

class FintelApp extends StatelessWidget {
  const FintelApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Fintel',
      theme: ThemeData(
        brightness: Brightness.light,
        primarySwatch: Colors.blue,
        colorScheme: const ColorScheme.light(
          primary: Colors.blue,
          secondary: Colors.amber, // Use secondary for accent-like color
        ),
        textTheme: const TextTheme(
          bodyLarge: TextStyle(
              color: Colors.black), // Use bodyLarge instead of bodyText1
          bodyMedium: TextStyle(
              color: Colors.black87), // Use bodyMedium instead of bodyText2
        ),
      ),
      darkTheme: ThemeData(
        brightness: Brightness.dark,
        primarySwatch: Colors.blueGrey,
        colorScheme: const ColorScheme.dark(
          primary: Colors.blueGrey,
          secondary: Colors.deepOrange, // Use secondary for accent-like color
        ),
        textTheme: const TextTheme(
          bodyLarge:
              TextStyle(color: Colors.white), // Use bodyLarge for dark mode
          bodyMedium:
              TextStyle(color: Colors.white70), // Use bodyMedium for dark mode
        ),
      ),
      themeMode: ThemeMode
          .system, // Switch between light and dark mode based on system settings
      home: const ConnectScreen(),
    );
  }
}
