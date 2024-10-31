import 'package:flutter/material.dart';

class AssetDetailsScreen extends StatelessWidget {
  final String assetName;

  const AssetDetailsScreen({super.key, required this.assetName});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(assetName),
      ),
      body: Center(
        child: Text(
          "Details, graphs, and information for $assetName will appear here.",
          style: const TextStyle(fontSize: 16),
          textAlign: TextAlign.center,
        ),
      ),
    );
  }
}
