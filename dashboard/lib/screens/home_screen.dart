import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:http/http.dart';
import 'dart:convert';
import 'ticker_details_screen.dart';

/// A stateful widget that displays the dashboard.
class HomeScreen extends StatefulWidget {
  final List<String> tickers;
  final String hostname;
  final String port;

  const HomeScreen(
      {super.key,
      required this.tickers,
      required this.hostname,
      required this.port});

  @override
  _HomeScreenState createState() => _HomeScreenState();
}

/// HomeScreen Widget
///
/// This screen displays a list of tickers retrieved from the Fintel server.
/// It serves as the main interface for users to view available tickers and
/// navigate to detailed views of each ticker.
///
/// The HomeScreen retrieves ticker data from the server whenever it is
/// displayed, ensuring that users always see the most up-to-date information.
///
/// Key Features:
/// - A dynamic list of tickers presented in a visually appealing format.
/// - Clicking on an ticker name navigates to the tickerDetailsScreen,
///   where users can view detailed information and graphs related to
///   the selected ticker.
/// - Automatically refreshes ticker data when navigating back from the
///   tickerDetailsScreen, ensuring the user sees any updates that may have
///   occurred during their navigation.
///
/// This screen does not include a back navigation arrow to the
/// ConnectScreen, enforcing a straightforward navigation flow
/// within the application.
class _HomeScreenState extends State<HomeScreen> {
  /// A list to hold the ticker names retrieved from the server.
  List<String> _tickers = <String>[];

  /// A boolean to track the loading state of the ticker fetching process.
  bool _isLoading = true;

  /// Controller for managing the input field where users enter ticker symbols
  /// they want to request. Used to retrieve and clear user input.
  final TextEditingController _tickerRequestListController =
      TextEditingController();

  /// List of ticker symbols specified by the user to be added as new ticker requests.
  /// Populated as the user adds each ticker to their request.
  final List<String> _newTickersToBeAdded = <String>[];

  /// Initializes the state and fetches tickers from the server.
  ///
  /// This method is called when the widget is first created.
  /// It triggers the _fetchTickers method to load the tickers
  /// immediately upon entering the HomeScreen.
  @override
  void initState() {
    super.initState();
    setState(() {
      // Initial _tickers values.
      _tickers = widget.tickers;
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
    fetchTickers();
  }

  /// Fetches tickers from the server using the provided hostname and port.
  ///
  /// This method sends an HTTP GET request to the server's /tickers endpoint.
  /// If successful, it updates the state with the retrieved tickers.
  /// If the request fails, it navigates back to the ConnectScreen.
  Future<void> fetchTickers() async {
    final url = Uri.parse('http://${widget.hostname}:${widget.port}/tickers');

    setState(() {
      _isLoading = true;
    });

    try {
      final Response response = await http.get(url);

      if (response.statusCode == 200) {
        final dynamic decodedData = jsonDecode(response.body);
        if (decodedData is Map && decodedData.containsKey('tickers')) {
          setState(() {
            _tickers = List<String>.from(decodedData['tickers']);
          });
        }
      } else {
        _showErrorDialog("Failed to load tickers.");
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
  /// This method is called when there is an error in fetching tickers
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

  /// Displays a confirmation dialog with a given message after a successful tickers request.
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

  /// Displays a dialog allowing the user to request new tickers.
  ///
  /// This method opens a modal dialog where the user can enter the ticker symbols
  /// they want to request. The dialog contains a text field for input, a list of
  /// entered tickers, and action buttons to cancel or submit the request. Tickers
  /// are added to the request list upon pressing Enter in the text field.
  ///
  /// Actions:
  /// - **Cancel**: Closes the dialog and clears the list of entered tickers.
  /// - **Submit**: Sends a POST request with the tickers to the server if the list
  ///   is not empty. If no tickers are present, the button is disabled.
  void _showTickerRequestDialog() {
    showDialog(
        context: context,
        builder: (BuildContext context) => StatefulBuilder(
            builder: (context, setState) => AlertDialog(
                  content: Column(
                    children: <Widget>[
                      const Padding(
                        padding: EdgeInsets.all(16.0),
                        child: Text(
                          'Request New Tickers',
                          style: TextStyle(
                              fontSize: 20, fontWeight: FontWeight.bold),
                        ),
                      ),
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 16.0),
                        child: TextField(
                          controller: _tickerRequestListController,
                          decoration: const InputDecoration(
                            labelText: 'Enter ticker name',
                            hintText: 'e.g., AAPL',
                            border: OutlineInputBorder(),
                          ),
                          onSubmitted: (String value) {
                            if (value.isNotEmpty) {
                              setState(() {
                                _newTickersToBeAdded.add(value);
                                _tickerRequestListController.clear();
                              });
                            }
                          },
                        ),
                      ),
                      Padding(
                        padding: const EdgeInsets.all(16.0),
                        child: ElevatedButton(
                          onPressed: () {
                            if (_tickerRequestListController.text.isNotEmpty) {
                              setState(() {
                                _newTickersToBeAdded
                                    .add(_tickerRequestListController.text);
                                _tickerRequestListController.clear();
                              });
                            }
                          },
                          child: const Text("Add Ticker"),
                        ),
                      ),
                      Wrap(
                        spacing: 8.0,
                        runSpacing: 4.0,
                        children: _newTickersToBeAdded
                            .map((ticker) => Chip(
                                  label: Text(ticker),
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
                          _newTickersToBeAdded.clear();
                        });
                      },
                      child: const Text("Cancel"),
                    ),
                    ElevatedButton(
                      onPressed: _newTickersToBeAdded.isEmpty
                          ? null
                          : () async {
                              final Uri url = Uri.parse(
                                  'http://${widget.hostname}:${widget.port}/request');
                              final String payload =
                                  jsonEncode(_newTickersToBeAdded);

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
                                    _newTickersToBeAdded.clear();
                                    _tickerRequestListController.clear();
                                  });
                                } else {
                                  _showErrorDialog(
                                      "Failed to request tickers.");
                                }
                              } catch (e) {
                                _showErrorDialog("Failed to request tickers.");
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
  /// a loading indicator if tickers are being fetched and a ListView
  /// to display the tickers. Tapping an ticker name navigates
  /// to the TickerDetailsScreen with the selected ticker.
  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: fetchTickers,
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
                  _tickers.isEmpty
                      ? const Center(child: Text("No tickers found"))
                      : ListView.builder(
                          itemCount: _tickers.length,
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
                                  _tickers[index],
                                  style: const TextStyle(
                                    fontSize: 18,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                                trailing: const Icon(Icons.arrow_forward_ios,
                                    size: 16),
                                onTap: () {
                                  fetchTickers();
                                  Navigator.push(
                                    context,
                                    MaterialPageRoute(
                                      builder: (context) => TickerDetailsScreen(
                                        tickerName: _tickers[index],
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
                      onPressed: _showTickerRequestDialog,
                      child: const Icon(Icons.add),
                    ),
                  ),
                ],
              ),
      ),
    );
  }
}
