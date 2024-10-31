import 'package:fintel/screens/home_screen.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

/// A stateful widget that handles the connection to the Fintel server.
class ConnectScreen extends StatefulWidget {
  const ConnectScreen({super.key});

  @override
  _ConnectScreenState createState() => _ConnectScreenState();
}

/// The `_ConnectScreenState` manages the user interface for connecting
/// to a specified server. It allows users to input the hostname and port
/// of the Fintel server, with default values of 'localhost' and '5000'
/// if left empty. Upon successful connection, it retrieves tickers
/// from the server and navigates to the HomeScreen to display them.
///
/// The main responsibilities of this class include:
/// - Collecting user input for the hostname and port.
/// - Attempting to connect to the specified server.
/// - Handling successful and failed connection attempts.
/// - Navigating to the HomeScreen with the retrieved tickers.
class _ConnectScreenState extends State<ConnectScreen> {
  final _hostnameController = TextEditingController();
  final _portController = TextEditingController();

  /// Attempts to connect to the specified server using the provided
  /// hostname and port.
  ///
  /// This method sends a GET request to the server's tickers endpoint
  /// and retrieves ticker names. If the connection is successful, it
  /// navigates to the HomeScreen. If it fails, it shows an error dialog
  /// to inform the user.
  Future<void> _connectToServer() async {
    final hostname = _hostnameController.text.isEmpty
        ? 'localhost'
        : _hostnameController.text;
    final port = _portController.text.isEmpty ? '5000' : _portController.text;
    final url = Uri.parse('http://$hostname:$port/tickers');

    try {
      final response = await http.get(url);

      if (response.statusCode == 200) {
        final decodedData = jsonDecode(response.body);

        if (decodedData is Map &&
            decodedData.containsKey('tickers') &&
            decodedData['tickers'] is List) {
          List<String> tickers = List<String>.from(decodedData['tickers']);

          // Navigate to HomeScreen with the list of tickers.
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) =>
                  HomeScreen(tickers: tickers, hostname: hostname, port: port),
            ),
          );
        } else {
          _showErrorDialog(); // Show error if JSON structure is unexpected
        }
      } else {
        _showErrorDialog();
      }
    } catch (e) {
      _showErrorDialog();
    }
  }

  /// Displays an error dialog with the specified message.
  ///
  /// This method is called when a connection attempt fails or when
  /// the server response is not as expected. It provides feedback to
  /// the user regarding the connection issue.
  void _showErrorDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Connection Error'),
        content: const Text('Please enter a valid server address.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  /// Builds the user interface for the ConnectScreen.
  ///
  /// This method returns a Scaffold widget containing the app bar,
  /// input fields for the hostname and port, and a connect button.
  /// It manages the layout and styling of the screen.
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const SizedBox(height: 50),
            Text(
              "Welcome to Fintel",
              style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 10),
            Text(
              "Please enter the address of the Fintel server you wish to connect",
              style: Theme.of(context).textTheme.bodyMedium,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 40),
            TextField(
              controller: _hostnameController,
              decoration: const InputDecoration(
                labelText: "Hostname (default: localhost)",
                border: OutlineInputBorder(),
              ),
              keyboardType: TextInputType.url,
            ),
            const SizedBox(height: 20),
            TextField(
              controller: _portController,
              decoration: const InputDecoration(
                labelText: "Port (default: 5000)",
                border: OutlineInputBorder(),
              ),
              keyboardType: TextInputType.number,
            ),
            const SizedBox(height: 40),
            ElevatedButton(
                onPressed: _connectToServer,
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 20),
                ),
                child: const Text("Connect")),
          ],
        ),
      ),
    );
  }

  /// Releases any resources used by the _ConnectScreenState.
  ///
  /// This method is called when the widget is permanently removed from the
  /// widget tree. It is typically used to clean up any resources or
  /// subscriptions that were initialized in the state object, ensuring
  /// that there are no memory leaks or unnecessary resource usage.
  ///
  /// If you have any controllers or listeners, make sure to dispose
  /// of them in this method to free up resources and prevent memory leaks.
  @override
  void dispose() {
    _hostnameController.dispose();
    _portController.dispose();
    super.dispose();
  }
}
