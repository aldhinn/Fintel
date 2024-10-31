import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'asset_details_screen.dart';

/// A stateful widget that displays the dashboard.
class HomeScreen extends StatefulWidget {
  final List<String> assets;
  final String hostname;
  final String port;

  const HomeScreen({super.key, required this.assets, required this.hostname, required this.port});

  @override
  _HomeScreenState createState() => _HomeScreenState();
}

/// HomeScreen Widget
///
/// This screen displays a list of asset names retrieved from the Fintel server.
/// It serves as the main interface for users to view available assets and
/// navigate to detailed views of each asset.
///
/// The HomeScreen retrieves asset data from the server whenever it is
/// displayed, ensuring that users always see the most up-to-date information.
/// 
/// Key Features:
/// - A dynamic list of assets presented in a visually appealing format.
/// - Clicking on an asset name navigates to the AssetDetailsScreen,
///   where users can view detailed information and graphs related to
///   the selected asset.
/// - Automatically refreshes asset data when navigating back from the
///   AssetDetailsScreen, ensuring the user sees any updates that may have
///   occurred during their navigation.
///
/// This screen does not include a back navigation arrow to the
/// ConnectScreen, enforcing a straightforward navigation flow
/// within the application.
class _HomeScreenState extends State<HomeScreen> {
  /// A list to hold the asset names retrieved from the server.
  List<String> _assets = [];
  /// A boolean to track the loading state of the asset fetching process.
  bool _isLoading = true;

  /// Initializes the state and fetches asset names from the server.
  ///
  /// This method is called when the widget is first created.
  /// It triggers the _fetchAssets method to load the asset names
  /// immediately upon entering the HomeScreen.
  @override
  void initState() {
    super.initState();
    setState(() {
      // Initial _assets values.
      _assets = widget.assets;
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
    fetchAssets();
  }

  /// Fetches asset names from the server using the provided hostname and port.
  ///
  /// This method sends an HTTP GET request to the server's /assets endpoint.
  /// If successful, it updates the state with the retrieved asset names.
  /// If the request fails, it navigates back to the ConnectScreen.
  Future<void> fetchAssets() async {
    final url = Uri.parse('http://${widget.hostname}:${widget.port}/assets');

    setState(() {
      _isLoading = true;
    });

    try {
      final response = await http.get(url);

      if (response.statusCode == 200) {
        final decodedData = jsonDecode(response.body);
        if (decodedData is Map && decodedData.containsKey('assets')) {
          setState(() {
            _assets = List<String>.from(decodedData['assets']);
          });
        }
      } else {
        _showErrorDialog("Failed to load assets.");
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
  /// This method is called when there is an error in fetching assets
  /// or if the server responds with an error status code.
  void _showErrorDialog(String message) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Error'),
        content: Text(message),
        actions: [
          TextButton(
            onPressed: () {
              // Navigate back to ConnectScreen
              Navigator.popUntil(context, (route) => route.isFirst);
            },
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  /// Builds the user interface for the HomeScreen.
  ///
  /// This method constructs the layout of the screen, including
  /// a loading indicator if assets are being fetched and a ListView
  /// to display the asset names. Tapping an asset name navigates
  /// to the AssetDetailsScreen with the selected asset.
  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: fetchAssets,
      child: Scaffold(
      appBar: AppBar(
        automaticallyImplyLeading: false,
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _assets.isEmpty
              ? const Center(child: Text("No assets found"))
              : ListView.builder(
                  itemCount: _assets.length,
                  itemBuilder: (context, index) {
                    return Card(
                      margin: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                      elevation: 3,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: ListTile(
                        title: Text(
                          _assets[index],
                          style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        trailing: const Icon(Icons.arrow_forward_ios, size: 16),
                        onTap: () {
                          fetchAssets();
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (context) => AssetDetailsScreen(
                                assetName: _assets[index],
                              ),
                            ),
                          );
                        },
                      ),
                    );
                  },
                ),
    ),
    );
  }
}