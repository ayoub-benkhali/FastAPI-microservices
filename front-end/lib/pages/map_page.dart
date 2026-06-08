import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:http/http.dart' as http;

// ⚠️ Adresse de ton backend FastAPI
const String apiBase = 'http://localhost:8000';

class MapPage extends StatefulWidget {
  const MapPage({super.key});
  @override
  State<MapPage> createState() => _MapPageState();
}

class _MapPageState extends State<MapPage> {
  final MapController _mapController = MapController();
  final List<Marker> _markers = [];
  final List<LatLng> _polylinePoints = [];
  bool _loading = false;
  String _statusMessage = 'Clique sur la carte pour enregistrer une position';

  // ── 1. Envoyer une position au backend ──────────────────────────
  Future<void> _sendLocation(LatLng point) async {
    setState(() {
      _loading = true;
      _statusMessage = 'Envoi en cours...';
    });

    try {
      final response = await http.post(
        Uri.parse('$apiBase/locations/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'user_id': 1,
          'latitude': point.latitude,
          'longitude': point.longitude,
        }),
      );

      if (response.statusCode == 201) {
        setState(() {
          _markers.add(_buildMarker(point, Colors.blue));
          _statusMessage =
              '✅ Enregistré : ${point.latitude.toStringAsFixed(5)}, ${point.longitude.toStringAsFixed(5)}';
        });
      } else {
        setState(() => _statusMessage = '❌ Erreur : ${response.statusCode}');
      }
    } catch (e) {
      setState(() => _statusMessage = '❌ Backend inaccessible : $e');
    } finally {
      setState(() => _loading = false);
    }
  }

  // ── 2. Charger l'historique de l'utilisateur ────────────────────
  Future<void> _loadHistory() async {
    setState(() {
      _loading = true;
      _markers.clear();
      _polylinePoints.clear();
      _statusMessage = 'Chargement de l\'historique...';
    });

    try {
      final response = await http.get(
        Uri.parse('$apiBase/locations/user/1'),
      );

      if (response.statusCode == 200) {
        final List data = jsonDecode(response.body);

        for (var item in data) {
          final point = LatLng(
            item['latitude'].toDouble(),
            item['longitude'].toDouble(),
          );
          _markers.add(_buildMarker(point, Colors.green));
          _polylinePoints.add(point);
        }

        if (_polylinePoints.isNotEmpty) {
          _mapController.move(_polylinePoints.first, 13);
        }

        setState(() {
          _statusMessage = '📍 ${data.length} position(s) chargée(s)';
        });
      }
    } catch (e) {
      setState(() => _statusMessage = '❌ Erreur chargement : $e');
    } finally {
      setState(() => _loading = false);
    }
  }

  // ── 3. Chercher les points proches ──────────────────────────────
  Future<void> _findNearby() async {
    setState(() {
      _loading = true;
      _statusMessage = 'Recherche des points proches...';
    });

    try {
      final response = await http.post(
        Uri.parse('$apiBase/locations/nearby'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'latitude': 36.8065,
          'longitude': 10.1815,
          'radius_meters': 5000,
        }),
      );

      if (response.statusCode == 200) {
        final List data = jsonDecode(response.body);
        for (var item in data) {
          final point = LatLng(
            item['latitude'].toDouble(),
            item['longitude'].toDouble(),
          );
          _markers.add(_buildMarker(point, Colors.orange));
        }
        setState(() {
          _statusMessage = '🔍 ${data.length} point(s) trouvé(s) dans un rayon de 5km';
        });
      }
    } catch (e) {
      setState(() => _statusMessage = '❌ Erreur nearby : $e');
    } finally {
      setState(() => _loading = false);
    }
  }

  // ── Utilitaire : créer un marqueur ──────────────────────────────
  Marker _buildMarker(LatLng point, Color color) {
    return Marker(
      point: point,
      width: 40,
      height: 40,
      child: Icon(Icons.location_pin, color: color, size: 40),
    );
  }

  // ── UI ──────────────────────────────────────────────────────────
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('📍 Location Service'),
        backgroundColor: Colors.blue[800],
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.history),
            tooltip: 'Historique',
            onPressed: _loadHistory,
          ),
          IconButton(
            icon: const Icon(Icons.clear),
            tooltip: 'Effacer',
            onPressed: () => setState(() {
              _markers.clear();
              _polylinePoints.clear();
              _statusMessage = 'Carte réinitialisée';
            }),
          ),
        ],
      ),

      body: Column(
        children: [

          // Barre de statut
          Container(
            width: double.infinity,
            color: Colors.blue[50],
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: Row(
              children: [
                if (_loading)
                  const SizedBox(
                    width: 16, height: 16,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  ),
                if (_loading) const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    _statusMessage,
                    style: TextStyle(color: Colors.blue[900]),
                  ),
                ),
              ],
            ),
          ),

          // Carte
          Expanded(
            child: FlutterMap(
              mapController: _mapController,
              options: MapOptions(
                initialCenter: const LatLng(36.8065, 10.1815), // Tunis
                initialZoom: 13,
                onTap: (tapPosition, latLng) => _sendLocation(latLng),
              ),
              children: [
                // Fond OpenStreetMap
                TileLayer(
                  urlTemplate:
                      'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                  userAgentPackageName: 'com.example.front_end',
                ),
                // Tracé du trajet
                if (_polylinePoints.length > 1)
                  PolylineLayer(
                    polylines: [
                      Polyline(
                        points: _polylinePoints,
                        color: Colors.blue,
                        strokeWidth: 3,
                      ),
                    ],
                  ),
                // Marqueurs
                MarkerLayer(markers: _markers),
              ],
            ),
          ),
        ],
      ),

      // Bouton Nearby
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _findNearby,
        icon: const Icon(Icons.radar),
        label: const Text('Points proches (5km)'),
        backgroundColor: Colors.orange,
      ),
    );
  }
}