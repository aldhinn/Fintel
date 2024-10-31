import 'package:flutter/material.dart';

class TickerDetailsScreen extends StatelessWidget {
  final String tickerName;

  const TickerDetailsScreen({super.key, required this.tickerName});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(tickerName),
      ),
      body: Center(
        child: Text(
          "Details, graphs, and information for $tickerName will appear here.",
          style: const TextStyle(fontSize: 16),
          textAlign: TextAlign.center,
        ),
      ),
    );
  }
}
