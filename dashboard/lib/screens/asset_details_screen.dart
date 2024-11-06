import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

/// A Flutter widget that displays detailed asset data in a line chart,
/// showing asset prices over time with dynamically adjustable x-axis intervals.
///
/// Includes a slider to control the number of visible x-axis labels, as well as
/// a chart that avoids label overlap by skipping labels at the edges of the graph.
class AssetDetailsScreen extends StatefulWidget {
  final String assetSymbol;
  final String hostname;
  final String port;

  const AssetDetailsScreen(
      {super.key,
      required this.assetSymbol,
      required this.hostname,
      required this.port});

  @override
  State<AssetDetailsScreen> createState() => _AssetDetailsScreenState();
}

/// `AssetDetailsScreen` state.
class _AssetDetailsScreenState extends State<AssetDetailsScreen> {
  /// The description of the asset symbol.
  String _assetDescription = "";

  /// List of points representing opening price history for the asset.
  List<FlSpot> _openingPriceData = [];

  /// List of points representing closing price history for the asset.
  List<FlSpot> _closePriceData = [];

  /// List of points representing adjusted closing price history for the asset.
  List<FlSpot> _adjustedClosePriceData = [];

  /// List of points representing high price history for the asset.
  List<FlSpot> _highPriceData = [];

  /// List of points representing low price history for the asset.
  List<FlSpot> _lowPriceData = [];

  /// List of dates corresponding to each point in _priceData.
  List<DateTime> _dateData = [];

  /// Show the opening price graph.
  bool _showOpeningPriceGraph = false;

  /// Show the close price graph.
  bool _showClosePriceGraph = true;

  /// Show the adjusted close price graph.
  bool _showAdjustedClosePriceGraph = false;

  /// Show the high price graph.
  bool _showHighPriceGraph = false;

  /// Show the low price graph.
  bool _showLowPriceGraph = false;

  /// This value, set by a slider in the UI, controls how far back in time
  /// the chart should display data. It is used to adjust the x-axis interval
  /// in the line chart and helps in dynamically fetching and displaying
  /// relevant data from the start date to today.
  int _monthsBack = 6;

  /// Slider-controlled interval for x-axis labels.
  double _horizontalLabelInterval = 24.0; // 4 times _monthsBack

  @override
  void initState() {
    super.initState();
    _fetchPricePoints(); // Initial fetch for 3 months back
  }

  /// Fetches the price history for the asset and populates _priceData and _dateData lists.
  ///
  /// This example uses mock data, but in a real implementation, you would pull data from
  /// an API or database. Each entry includes a date and close price.
  Future<void> _fetchPricePoints() async {
    final endDate = DateTime.now();
    final startDate = DateTime.now().subtract(Duration(days: 30 * _monthsBack));

    final response = await http.post(
      Uri.parse('http://${widget.hostname}:${widget.port}/data'),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({
        "symbol": widget.assetSymbol,
        "start_date": startDate.toIso8601String().substring(0, 10),
        "end_date": endDate.toIso8601String().substring(0, 10)
      }),
    );

    if (response.statusCode == 200) {
      final jsonData = jsonDecode(response.body);
      List pricePoints = jsonData['prices'];

      setState(() {
        _assetDescription = jsonData['description'];
        _openingPriceData = pricePoints
            .asMap()
            .entries
            .map((entry) => FlSpot(
                  entry.key.toDouble(),
                  entry.value['open_price'].toDouble(),
                ))
            .toList();
        _closePriceData = pricePoints
            .asMap()
            .entries
            .map((entry) => FlSpot(
                  entry.key.toDouble(),
                  entry.value['close_price'].toDouble(),
                ))
            .toList();
        _adjustedClosePriceData = pricePoints
            .asMap()
            .entries
            .map((entry) => FlSpot(
                  entry.key.toDouble(),
                  entry.value['adjusted_close'].toDouble(),
                ))
            .toList();
        _highPriceData = pricePoints
            .asMap()
            .entries
            .map((entry) => FlSpot(
                  entry.key.toDouble(),
                  entry.value['high_price'].toDouble(),
                ))
            .toList();
        _lowPriceData = pricePoints
            .asMap()
            .entries
            .map((entry) => FlSpot(
                  entry.key.toDouble(),
                  entry.value['low_price'].toDouble(),
                ))
            .toList();

        _dateData =
            pricePoints.map((entry) => DateTime.parse(entry['date'])).toList();
      });
    } else {
      // TODO: Implement.
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text.rich(
          TextSpan(
            children: [
              TextSpan(
                text: widget.assetSymbol,
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
              TextSpan(
                text: ' - $_assetDescription',
                style: const TextStyle(fontWeight: FontWeight.normal),
              ),
            ],
          ),
        ),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            // Checkboxes to toggle visibility of the graphs
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                Row(
                  children: [
                    Checkbox(
                      value: _showOpeningPriceGraph,
                      onChanged: (value) {
                        setState(() {
                          _showOpeningPriceGraph = value!;
                        });
                      },
                    ),
                    const Text("Show Opening Price"),
                  ],
                ),
                Row(
                  children: [
                    Checkbox(
                      value: _showClosePriceGraph,
                      onChanged: (value) {
                        setState(() {
                          _showClosePriceGraph = value!;
                        });
                      },
                    ),
                    const Text("Show Close Price"),
                  ],
                ),
                Row(
                  children: [
                    Checkbox(
                      value: _showAdjustedClosePriceGraph,
                      onChanged: (value) {
                        setState(() {
                          _showAdjustedClosePriceGraph = value!;
                        });
                      },
                    ),
                    const Text("Show Adjusted Close Price"),
                  ],
                ),
                Row(
                  children: [
                    Checkbox(
                      value: _showHighPriceGraph,
                      onChanged: (value) {
                        setState(() {
                          _showHighPriceGraph = value!;
                        });
                      },
                    ),
                    const Text("Show High Price"),
                  ],
                ),
                Row(
                  children: [
                    Checkbox(
                      value: _showLowPriceGraph,
                      onChanged: (value) {
                        setState(() {
                          _showLowPriceGraph = value!;
                        });
                      },
                    ),
                    const Text("Show Low Price"),
                  ],
                ),
              ],
            ),
            Expanded(
              child: LineChart(LineChartData(
                lineBarsData: [
                  if (_showOpeningPriceGraph)
                    LineChartBarData(
                      spots: _openingPriceData,
                      isCurved: true,
                      barWidth: 2,
                      belowBarData: BarAreaData(
                        show: true,
                        gradient: LinearGradient(
                          colors: [
                            Colors.orange.withOpacity(0.3),
                            Colors.orange.withOpacity(0.0),
                          ],
                          begin: Alignment.topCenter,
                          end: Alignment.bottomCenter,
                        ),
                      ),
                    ),
                  if (_showClosePriceGraph)
                    LineChartBarData(
                      spots: _closePriceData,
                      isCurved: true,
                      barWidth: 2,
                      belowBarData: BarAreaData(
                        show: true,
                        gradient: LinearGradient(
                          colors: [
                            Colors.blue.withOpacity(0.3),
                            Colors.blue.withOpacity(0.0),
                          ],
                          begin: Alignment.topCenter,
                          end: Alignment.bottomCenter,
                        ),
                      ),
                    ),
                  if (_showAdjustedClosePriceGraph)
                    LineChartBarData(
                      spots: _adjustedClosePriceData,
                      isCurved: true,
                      barWidth: 2,
                      belowBarData: BarAreaData(
                        show: true,
                        gradient: LinearGradient(
                          colors: [
                            Colors.deepPurple.withOpacity(0.6),
                            Colors.deepPurple.withOpacity(0.0),
                          ],
                          begin: Alignment.topCenter,
                          end: Alignment.bottomCenter,
                        ),
                      ),
                    ),
                  if (_showHighPriceGraph)
                    LineChartBarData(
                      spots: _highPriceData,
                      isCurved: true,
                      barWidth: 2,
                      belowBarData: BarAreaData(
                        show: true,
                        gradient: LinearGradient(
                          colors: [
                            Colors.green.withOpacity(0.6),
                            Colors.green.withOpacity(0.0),
                          ],
                          begin: Alignment.topCenter,
                          end: Alignment.bottomCenter,
                        ),
                      ),
                    ),
                  if (_showLowPriceGraph)
                    LineChartBarData(
                      spots: _lowPriceData,
                      isCurved: true,
                      barWidth: 2,
                      belowBarData: BarAreaData(
                        show: true,
                        gradient: LinearGradient(
                          colors: [
                            Colors.red.withOpacity(0.6),
                            Colors.red.withOpacity(0.0),
                          ],
                          begin: Alignment.topCenter,
                          end: Alignment.bottomCenter,
                        ),
                      ),
                    ),
                ],
                titlesData: FlTitlesData(
                  bottomTitles: AxisTitles(
                    sideTitles: SideTitles(
                      showTitles: true,
                      interval: _horizontalLabelInterval,
                      getTitlesWidget: (value, meta) {
                        // Assuming value corresponds to an index in your `_priceData`
                        int index = value.toInt();
                        if (index == _closePriceData.length - 1) {
                          // Skip the last label to avoid edge overlap
                          return const SizedBox.shrink();
                        }
                        if (index >= 0 && index < _closePriceData.length) {
                          DateTime date = _dateData[index];
                          return Text(
                            "${date.year}-${date.month}-${date.day}",
                            style: const TextStyle(fontSize: 10),
                          );
                        }
                        return const SizedBox.shrink();
                      },
                    ),
                  ),
                  topTitles: const AxisTitles(
                    sideTitles: SideTitles(showTitles: false),
                  ),
                  rightTitles: const AxisTitles(
                    sideTitles: SideTitles(showTitles: false),
                  ),
                  leftTitles: AxisTitles(
                    sideTitles: SideTitles(
                      showTitles: true,
                      interval: 20,
                      getTitlesWidget: (value, meta) {
                        if (value == meta.min) {
                          // Skip the bottom label on the left side
                          return const SizedBox.shrink();
                        }
                        return Text(
                          value.toStringAsFixed(0),
                          style: const TextStyle(fontSize: 10),
                        );
                      },
                    ),
                  ),
                ),
                gridData: const FlGridData(show: true),
                borderData: FlBorderData(show: true),
              )),
            ),
            const SizedBox(height: 20),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text("Time range (months):"),
                Text("$_monthsBack months"),
              ],
            ),
            Slider(
              value: _monthsBack.toDouble(),
              min: 3,
              max: 240,
              label: '$_monthsBack months',
              onChanged: (value) {
                setState(() {
                  _monthsBack = value.toInt();
                  _horizontalLabelInterval = 4 * value;
                });
                _fetchPricePoints();
              },
            ),
          ],
        ),
      ),
    );
  }
}
