import 'package:flutter/material.dart';

class AssetDetailsScreen extends StatelessWidget {
  final String assetSymbol;

  const AssetDetailsScreen({super.key, required this.assetSymbol});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(assetSymbol),
      ),
      body: Center(
        child: Text(
          "Details, graphs, and information for $assetSymbol will appear here.",
          style: const TextStyle(fontSize: 16),
          textAlign: TextAlign.center,
        ),
      ),
    );
  }
}
