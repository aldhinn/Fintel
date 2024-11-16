import "package:fintel/screens/home_screen.dart";
import "package:flutter/material.dart";
import "package:http/http.dart" as http;
import "dart:convert";

/// A screen where the user can input a hostname and port to connect to a Fintel server.
///
/// The screen displays input fields for the server"s hostname and port.
/// If valid inputs are provided, it sends a request to the server to fetch a list of asset symbols
/// and navigates to the [HomeScreen] on successful connection.
/// If the connection fails, an error dialog is displayed.
class ConnectScreen extends StatefulWidget {
  const ConnectScreen({super.key});

  @override
  _ConnectScreenState createState() => _ConnectScreenState();
}

class _ConnectScreenState extends State<ConnectScreen> {
  /// Text controller for the hostname input field.
  final _hostnameController = TextEditingController();

  /// Text controller for the port input field.
  final _portController = TextEditingController();

  /// Connects to the server using the provided hostname and port.
  ///
  /// If the connection succeeds and the server responds with a valid JSON containing
  /// a `symbols` list, the app navigates to the [HomeScreen].
  /// Displays an error dialog if the connection fails or the response is invalid.
  Future<void> _connectToServer() async {
    final hostname = _hostnameController.text.isEmpty
        ? "localhost"
        : _hostnameController.text;
    final port = _portController.text.isEmpty ? "61000" : _portController.text;
    final url = Uri.parse("http://$hostname:$port/symbols");

    try {
      final response = await http.get(url);

      if (response.statusCode == 200) {
        final decodedData = jsonDecode(response.body);

        if (decodedData is Map &&
            decodedData.containsKey("symbols") &&
            decodedData["symbols"] is List) {
          List<String> assetSymbols = List<String>.from(decodedData["symbols"]);

          // Navigate to HomeScreen with the list of asset symbols.
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => HomeScreen(
                  assetSymbols: assetSymbols, hostname: hostname, port: port),
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

  /// Displays an error dialog when the connection fails.
  void _showErrorDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text("Connection Error"),
        content: const Text("Please enter a valid server address."),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text("OK"),
          ),
        ],
      ),
    );
  }

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
              key: const Key("hostnameInput"),
              controller: _hostnameController,
              decoration: const InputDecoration(
                labelText: "Hostname (default: localhost)",
                border: OutlineInputBorder(),
              ),
              keyboardType: TextInputType.url,
            ),
            const SizedBox(height: 20),
            TextField(
              key: const Key("portInput"),
              controller: _portController,
              decoration: const InputDecoration(
                labelText: "Port (default: 61000)",
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

  @override
  void dispose() {
    _hostnameController.dispose();
    _portController.dispose();
    super.dispose();
  }
}
