import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:http/http.dart';
import 'dart:convert';
import 'asset_details_screen.dart';

/// A stateful widget that displays the dashboard.
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

/// HomeScreen Widget
///
/// This screen displays a list of asset symbols retrieved from the Fintel server.
/// It serves as the main interface for users to view available asset symbols and
/// navigate to detailed views of each asset symbol.
///
/// The HomeScreen retrieves asset symbols from the server whenever it is
/// displayed, ensuring that users always see the most up-to-date information.
///
/// Key Features:
/// - A dynamic list of asset symbols presented in a visually appealing format.
/// - Clicking on an asset symbol navigates to the AssetDetailsScreen,
///   where users can view detailed information and graphs related to
///   the selected asset symbol.
/// - Automatically refreshes asset symbols when navigating back from the
///   AssetDetailsScreen, ensuring the user sees any updates that may have
///   occurred during their navigation.
///
/// This screen does not include a back navigation arrow to the
/// ConnectScreen, enforcing a straightforward navigation flow
/// within the application.
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

  /// Initializes the state and fetches asset symbols from the server.
  ///
  /// This method is called when the widget is first created.
  /// It triggers the fetchAssetSymbols method to load the asset symbols
  /// immediately upon entering the HomeScreen.
  @override
  void initState() {
    super.initState();
    setState(() {
      // Initial _assetSymbols values.
      _assetSymbols = widget.assetSymbols;
    });
  }

  /// Called when the dependencies of this State object change.
  ///
  /// This method is triggered after the state object is created and
  /// whenever the dependencies of the widget change. This can occur
  /// when the parent widget rebuilds, which can affect the inherited
  /// widgets that this State object relies on.
  ///
  /// Typically, this method is overridden to fetch data that requires
  /// the build context or to listen to inherited widget changes.
  ///
  /// For instance, if you have an InheritedWidget that provides data
  /// to this widget, you can use this method to react to those changes.
  /// In this case, there is no specific implementation required for
  /// the HomeScreen, but it can be used for additional setup in the
  /// future if needed.
  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    fetchAssetSymbols();
  }

  /// Fetches asset symbols from the server using the provided hostname and port.
  ///
  /// This method sends an HTTP GET request to the server's /symbols endpoint.
  /// If successful, it updates the state with the retrieved asset symbols.
  /// If the request fails, it navigates back to the ConnectScreen.
  Future<void> fetchAssetSymbols() async {
    final url = Uri.parse('http://${widget.hostname}:${widget.port}/symbols');

    setState(() {
      _isLoading = true;
    });

    try {
      final Response response = await http.get(url);

      if (response.statusCode == 200) {
        final dynamic decodedData = jsonDecode(response.body);
        if (decodedData is Map && decodedData.containsKey('symbols')) {
          setState(() {
            _assetSymbols = List<String>.from(decodedData['symbols']);
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
        title: const Text('Error'),
        content: Text(message),
        actions: <Widget>[
          TextButton(
            onPressed: () {
              // Navigate back to ConnectScreen
              Navigator.popUntil(
                  context, (Route<dynamic> route) => route.isFirst);
            },
            child: const Text('OK'),
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
                          'Request New Asset Symbols',
                          style: TextStyle(
                              fontSize: 20, fontWeight: FontWeight.bold),
                        ),
                      ),
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 16.0),
                        child: TextField(
                          controller: _assetSymbolsRequestListController,
                          decoration: const InputDecoration(
                            labelText: 'Enter asset symbol',
                            hintText: 'e.g., AAPL',
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
                                  'http://${widget.hostname}:${widget.port}/request');
                              final String payload =
                                  jsonEncode(_newAssetSymbolsToBeAdded);

                              try {
                                final Response response = await http.post(
                                  url,
                                  headers: <String, String>{
                                    'Content-Type': 'application/json'
                                  },
                                  body: payload,
                                );

                                if (response.statusCode == 200) {
                                  Navigator.of(context).pop();
                                  _showConfirmationDialog("Successfully sent.");
                                  setState(() {
                                    _newAssetSymbolsToBeAdded.clear();
                                    _assetSymbolsRequestListController.clear();
                                  });
                                } else {
                                  _showErrorDialog(
                                      "Failed to request asset symbols.");
                                }
                              } catch (e) {
                                _showErrorDialog(
                                    "Failed to request asset symbols.");
                              }
                            },
                      child: const Text("Submit"),
                    ),
                  ],
                )));
  }

  /// Builds the user interface for the HomeScreen.
  ///
  /// This method constructs the layout of the screen, including
  /// a loading indicator if asset symbols are being fetched and a ListView
  /// to display the asset symbols. Tapping an asset symbol navigates
  /// to the AssetDetailsScreen with the selected asset symbol.
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
                child: Text(
                  'Menu',
                  style: TextStyle(
                    color: Theme.of(context)
                        .colorScheme
                        .onPrimary, // Inherit text color based on theme
                    fontSize: 24,
                  ),
                ),
              ),
              ListTile(
                leading: Icon(Icons.switch_left,
                    color: Theme.of(context)
                        .iconTheme
                        .color), // Inherit icon color
                title: Text(
                  'Switch Server',
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
