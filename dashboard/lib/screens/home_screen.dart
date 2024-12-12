import "package:flutter/material.dart";
import "package:http/http.dart" as http;
import "package:http/http.dart";
import "dart:convert";
import "asset_details_screen.dart";

/// The HomeScreen widget serves as the main interface for displaying a list of
/// asset symbols retrieved from the server. It also provides functionality to:
/// - Fetch the asset symbols from the server.
/// - Navigate to details of a selected asset symbol.
/// - Request new asset symbols to be added to the server.
///
/// This screen is stateful and updates dynamically based on server responses.
///
/// Parameters:
/// - `assetSymbols` (List<String>): Initial list of asset symbols to display.
/// - `hostname` (String): The server hostname.
/// - `port` (String): The server port.
class HomeScreen extends StatefulWidget {
  final List<String> assetSymbols;
  final String hostname;
  final String port;

  const HomeScreen(
      {super.key,
      required this.assetSymbols,
      required this.hostname,
      required this.port});

  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  /// A list to hold the asset symbols retrieved from the server.
  List<String> _assetSymbols = <String>[];

  /// A boolean to track the loading state of the asset symbols fetching process.
  bool _isLoading = true;

  /// Controller for managing the input field where users enter asset symbols
  /// they want to request. Used to retrieve and clear user input.
  final TextEditingController _assetSymbolsRequestListController =
      TextEditingController();

  /// List of asset symbols specified by the user to be analyzed.
  /// Populated as the user adds each asset symbol to their request.
  final List<String> _newAssetSymbolsToBeAdded = <String>[];

  @override
  void initState() {
    super.initState();
    setState(() {
      // Initial _assetSymbols values.
      _assetSymbols = widget.assetSymbols;
    });
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    fetchAssetSymbols();
  }

  /// Fetches asset symbols from the server using the provided hostname and port.
  ///
  /// This method sends an HTTP GET request to the server"s /symbols endpoint.
  /// If successful, it updates the state with the retrieved asset symbols.
  /// If the request fails, it navigates back to the ConnectScreen.
  Future<void> fetchAssetSymbols() async {
    final url = Uri.parse("http://${widget.hostname}:${widget.port}/symbols");

    setState(() {
      _isLoading = true;
    });

    try {
      final Response response = await http.get(url);

      if (response.statusCode == 200) {
        final dynamic decodedData = jsonDecode(response.body);
        if (decodedData is Map && decodedData.containsKey("symbols")) {
          setState(() {
            _assetSymbols = List<String>.from(decodedData["symbols"]);
          });
        }
      } else {
        _showErrorDialog("Failed to load asset symbols.");
      }
    } catch (e) {
      _showErrorDialog("Connection error.");
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  /// Displays an error dialog with the specified message.
  ///
  /// This method is called when there is an error in fetching asset symbols
  /// or if the server responds with an error status code.
  void _showErrorDialog(String message) {
    showDialog(
      context: context,
      builder: (BuildContext context) => AlertDialog(
        title: const Text("Error"),
        content: Text(message),
        actions: <Widget>[
          TextButton(
            onPressed: () {
              // Navigate back to ConnectScreen
              Navigator.popUntil(
                  context, (Route<dynamic> route) => route.isFirst);
            },
            child: const Text("OK"),
          ),
        ],
      ),
    );
  }

  /// Displays a confirmation dialog with a given message after a successful asset symbols request.
  /// Provides user feedback on request status and can be dismissed with an "OK" button.
  void _showConfirmationDialog(String message) {
    showDialog(
      context: context,
      builder: (BuildContext context) => AlertDialog(
        title: const Text("Success"),
        content: Text(message),
        actions: <Widget>[
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text("OK"),
          ),
        ],
      ),
    );
  }

  /// Displays a loading screen dialog with a specified message.
  void _showLoadingDialog(String message) {
    showDialog(
        context: context,
        builder: (BuildContext context) => Dialog(
              backgroundColor: Theme.of(context).splashColor,
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(message, style: const TextStyle(fontSize: 16)),
                    const SizedBox(height: 20),
                    const CircularProgressIndicator(),
                  ],
                ),
              ),
            ));
  }

  /// Displays a dialog allowing the user to request new asset symbols.
  ///
  /// This method opens a modal dialog where the user can enter the asset symbols
  /// they want to request. The dialog contains a text field for input, a list of
  /// entered asset symbols, and action buttons to cancel or submit the request. Asset symbols
  /// are added to the request list upon pressing Enter in the text field.
  ///
  /// Actions:
  /// - **Cancel**: Closes the dialog and clears the list of entered asset symbols.
  /// - **Submit**: Sends a POST request with the asset symbols to the server if the list
  ///   is not empty. If no asset symbols are present, the button is disabled.
  void _showAssetSymbolsRequestDialog() {
    showDialog(
        context: context,
        builder: (BuildContext context) => StatefulBuilder(
            builder: (context, setState) => AlertDialog(
                  content: Column(
                    children: <Widget>[
                      const Padding(
                        padding: EdgeInsets.all(16.0),
                        child: Text(
                          "Request New Asset Symbols",
                          style: TextStyle(
                              fontSize: 20, fontWeight: FontWeight.bold),
                        ),
                      ),
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 16.0),
                        child: TextField(
                          controller: _assetSymbolsRequestListController,
                          decoration: const InputDecoration(
                            labelText: "Enter asset symbol",
                            hintText: "e.g., AAPL",
                            border: OutlineInputBorder(),
                          ),
                          onSubmitted: (String value) {
                            if (value.isNotEmpty) {
                              setState(() {
                                _newAssetSymbolsToBeAdded.add(value);
                                _assetSymbolsRequestListController.clear();
                              });
                            }
                          },
                        ),
                      ),
                      Padding(
                        padding: const EdgeInsets.all(16.0),
                        child: ElevatedButton(
                          onPressed: () {
                            if (_assetSymbolsRequestListController
                                .text.isNotEmpty) {
                              setState(() {
                                _newAssetSymbolsToBeAdded.add(
                                    _assetSymbolsRequestListController.text);
                                _assetSymbolsRequestListController.clear();
                              });
                            }
                          },
                          child: const Text("Add Asset Symbol"),
                        ),
                      ),
                      Wrap(
                        spacing: 8.0,
                        runSpacing: 4.0,
                        children: _newAssetSymbolsToBeAdded
                            .map((assetSymbol) => Chip(
                                  label: Text(assetSymbol),
                                ))
                            .toList(),
                      ),
                    ],
                  ),
                  actions: <Widget>[
                    TextButton(
                      onPressed: () {
                        Navigator.of(context).pop();
                        setState(() {
                          _newAssetSymbolsToBeAdded.clear();
                        });
                      },
                      child: const Text("Cancel"),
                    ),
                    ElevatedButton(
                      onPressed: _newAssetSymbolsToBeAdded.isEmpty
                          ? null
                          : () async {
                              final Uri url = Uri.parse(
                                  "http://${widget.hostname}:${widget.port}/symbols");
                              final String payload =
                                  jsonEncode(_newAssetSymbolsToBeAdded);

                              try {
                                _showLoadingDialog(
                                    "Requesting for the server to append the symbol");
                                final Response response = await http.post(
                                  url,
                                  headers: <String, String>{
                                    "Content-Type": "application/json"
                                  },
                                  body: payload,
                                );
                                Navigator.of(context).pop();

                                if (response.statusCode == 204) {
                                  Navigator.of(context).pop();
                                  _showConfirmationDialog("Successfully sent.");
                                  setState(() {
                                    _newAssetSymbolsToBeAdded.clear();
                                    _assetSymbolsRequestListController.clear();
                                  });
                                } else {
                                  _showErrorDialog(
                                      "${jsonDecode(response.body)["error"]}");
                                }
                              } catch (e) {
                                _showErrorDialog("$e");
                              }
                            },
                      child: const Text("Submit"),
                    ),
                  ],
                )));
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: fetchAssetSymbols,
      child: Scaffold(
        appBar: AppBar(
          automaticallyImplyLeading: true,
        ),
        drawer: Drawer(
          child: ListView(
            padding: EdgeInsets.zero,
            children: <Widget>[
              DrawerHeader(
                decoration: BoxDecoration(
                  color: Theme.of(context)
                      .primaryColor, // Inherit primary color from theme
                ),
                child: Text("Menu",
                    style: Theme.of(context).textTheme.headlineSmall),
              ),
              ListTile(
                leading: Icon(Icons.switch_left,
                    color: Theme.of(context)
                        .iconTheme
                        .color), // Inherit icon color
                title: Text(
                  "Switch Server",
                  style: Theme.of(context)
                      .textTheme
                      .bodyLarge, // Inherit text style
                ),
                onTap: () {
                  Navigator.pop(context); // Close the drawer
                  Navigator.of(context).pop(); // Navigate to ConnectScreen
                },
              ),
            ],
          ),
        ),
        body: _isLoading
            ? const Center(child: CircularProgressIndicator())
            : Stack(
                children: <Widget>[
                  _assetSymbols.isEmpty
                      ? const Center(child: Text("No asset symbols found"))
                      : ListView.builder(
                          itemCount: _assetSymbols.length,
                          itemBuilder: (context, index) {
                            return Card(
                              margin: const EdgeInsets.symmetric(
                                  horizontal: 16, vertical: 8),
                              elevation: 3,
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(12),
                              ),
                              child: ListTile(
                                title: Text(
                                  _assetSymbols[index],
                                  style: const TextStyle(
                                    fontSize: 18,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                                trailing: const Icon(Icons.arrow_forward_ios,
                                    size: 16),
                                onTap: () {
                                  fetchAssetSymbols();
                                  Navigator.push(
                                    context,
                                    MaterialPageRoute(
                                      builder: (context) => AssetDetailsScreen(
                                        assetSymbol: _assetSymbols[index],
                                        hostname: widget.hostname,
                                        port: widget.port,
                                      ),
                                    ),
                                  );
                                },
                              ),
                            );
                          },
                        ),
                  Positioned(
                    bottom: 16, // Position it a little above the bottom
                    left: MediaQuery.of(context).size.width / 2 -
                        28, // Center horizontally
                    child: FloatingActionButton(
                      onPressed: _showAssetSymbolsRequestDialog,
                      child: const Icon(Icons.add),
                    ),
                  ),
                ],
              ),
      ),
    );
  }
}
