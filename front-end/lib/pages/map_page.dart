// importe les outils de conversion JSON (jsonEncode, jsonDecode)
import 'dart:convert';
// importe Material Design (Scaffold, AppBar, FloatingActionButton, etc.)
import 'package:flutter/material.dart';
// importe la librairie flutter_map pour afficher les cartes interactives
import 'package:flutter_map/flutter_map.dart';
// importe LatLng : classe représentant une coordonnée géographique (latitude, longitude)
import 'package:latlong2/latlong.dart';
// importe le package http pour faire des requêtes HTTP (GET, POST, etc.)
import 'package:http/http.dart' as http;

// ⚠️ Adresse de ton backend FastAPI
// À changer selon l'environnement (localhost pour développement, IP réelle en production)
const String apiBase = 'http://localhost:8000';


// MapPage : widget avec état (StatefulWidget) - l'état change (marqueurs, positions, etc.)
class MapPage extends StatefulWidget {
  // Constructeur avec clé optionnelle (pattern Flutter standard)
  const MapPage({super.key});

  // Crée l'état associé à ce widget
  @override
  State<MapPage> createState() => _MapPageState();
}

// Classe d'état : gère l'état interne et la logique du MapPage
class _MapPageState extends State<MapPage> {
  // Contrôleur pour la carte : permet de contrôler le zoom, le centre, etc.
  final MapController _mapController = MapController();
  // Liste pour stocker tous les marqueurs affichés sur la carte
  final List<Marker> _markers = [];
  // Liste pour stocker les points du polyline (tracé du trajet)
  final List<LatLng> _polylinePoints = [];
  // Flag booléen : true si une requête est en cours, false sinon
  bool _loading = false;
  String _statusMessage = 'Clique sur la carte pour enregistrer une position';

  // ── 1. Envoyer une position au backend ──────────────────────────
  Future<void> _sendLocation(LatLng point) async {
     // Met à jour l'état : affiche l'indicateur de chargement et un message de statut
    setState(() {
      _loading = true;
      _statusMessage = 'Envoi en cours...';
    });

    try {
      // Effectue une requête POST au backend
      final response = await http.post(
        Uri.parse('$apiBase/locations/'), // URL : http://localhost:8000/locations/
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          // Corps de la requête : JSON contenant user_id, latitude et longitude
          'user_id': 1,
          'latitude': point.latitude,
          'longitude': point.longitude,
        }),
      );

      if (response.statusCode == 201) {
        setState(() {
          // ajoute un marqueur bleu à la position enregistrée
          _markers.add(_buildMarker(point, Colors.blue));
          // affiche un message de confirmation avec les coordonnées
          _statusMessage =
              '✅ Enregistré : ${point.latitude.toStringAsFixed(5)}, ${point.longitude.toStringAsFixed(5)}';
        });
      } else {
        setState(() => _statusMessage = '❌ Erreur : ${response.statusCode}');
      }
    } catch (e) {
      // Exception capturée : le backend est inaccessible ou erreur réseau
      setState(() => _statusMessage = '❌ Backend inaccessible : $e');
    } finally {
      setState(() => _loading = false);
    }
  }

  // ── 2. Charger l'historique de l'utilisateur ────────────────────
  Future<void> _loadHistory() async {
    // Met à jour l'état avant de charger
    setState(() {
      _loading = true; // affiche le spinne
      _markers.clear(); // vide la liste des marqueurs
      _polylinePoints.clear(); // vide la liste des points du tracé
      _statusMessage = 'Chargement de l\'historique...';
    });

    try {
      // Effectue une requête GET au backend pour récupérer l'historique
      final response = await http.get(
        Uri.parse('$apiBase/locations/user/1'), // URL : http://localhost:8000/locations/user/1
      );

      if (response.statusCode == 200) {
         // Décode la réponse JSON en liste d'objets
        final List data = jsonDecode(response.body);

        for (var item in data) {
          // Crée un objet LatLng à partir de la latitude et longitude de chaque position
          final point = LatLng(
            item['latitude'].toDouble(), // convertit la latitude en double
            item['longitude'].toDouble(), // convertit la longitude en double
          );
          // Ajoute un marqueur vert pour les positions historiques
          _markers.add(_buildMarker(point, Colors.green));
          // Ajoute le point au tracé (polyline)
          _polylinePoints.add(point);
        }

// Si au moins un point a été chargé, centre la carte sur le premier point
        if (_polylinePoints.isNotEmpty) {
          _mapController.move(_polylinePoints.first, 13);
        }

        setState(() {
          _statusMessage = '📍 ${data.length} position(s) chargée(s)'; // affiche le nombre de positions
        });
      }
    } catch (e) {
      // Exception capturée : erreur réseau ou parsing JSON
      setState(() => _statusMessage = '❌ Erreur chargement : $e');
    } finally {
      // Code exécuté quoiqu'il arrive (succès ou erreur)
      setState(() => _loading = false);
    }
  }

  // ── Utilitaire : créer un marqueur ──────────────────────────────
  Marker _buildMarker(LatLng point, Color color) {
    // Retourne un objet Marker configuré pour s'afficher sur la carte
    return Marker(
      point: point, // position géographique du marqueur
      width: 40, // largeur du marqueur en pixels
      height: 40, // hauteur du marqueur en pixels
      // Widget enfant : une icône d'épingle de localisation
      child: Icon(Icons.location_pin, color: color, size: 40),
    );
  }

  // ── UI : Interface utilisateur ──────────────────────────────────
  @override
  Widget build(BuildContext context) {
    // Scaffold : structure de base avec AppBar, body, FAB, etc.
    return Scaffold(
      appBar: AppBar(
        title: const Text('📍 Location Service'),
        backgroundColor: Colors.blue[800],
        foregroundColor: Colors.white,
        // Boutons d'action à droite de l'AppBar
        actions: [
          // Bouton 1 : charger l'historique
          IconButton(
            icon: const Icon(Icons.history), // icône d'historique
            tooltip: 'Historique',
            onPressed: _loadHistory, // appelle _loadHistory quand appuyé
          ),
          // Bouton 2 : effacer les marqueurs et le tracé
          IconButton(
            icon: const Icon(Icons.clear), // icône de fermeture
            tooltip: 'Effacer',
            // Remet l'app à zéro : vide les marqueurs et le tracé
            onPressed: () => setState(() {
              _markers.clear(); // supprime tous les marqueurs
              _polylinePoints.clear(); // supprime tous les points du tracé
              _statusMessage = 'Carte réinitialisée';
            }),
          ),
        ],
      ),

// Body : contenu principal de l'écran
      body: Column(
        // Empile les widgets verticalement
        children: [
            // ─────────────────────────────────────────────────────
            // Barre de statut (affichage des messages et spinner)
            // ─────────────────────────────────────────────────────

           // Conteneur pour le message de statut
          Container(
            width: double.infinity, // prend toute la largeur
            color: Colors.blue[50], // couleur de fond bleu pâle
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8), // espacement interne
            // Row : affiche les éléments horizontalement
            child: Row( 
              children: [
                // Si une requête est en cours, affiche un spinner
                if (_loading)
                  const SizedBox(
                    width: 16, height: 16,
                    child: CircularProgressIndicator(strokeWidth: 2), // spinner de chargement
                  ),
                if (_loading) const SizedBox(width: 8),
                Expanded(
                   // prend tout l'espace disponible
                  child: Text(
                    _statusMessage,
                    style: TextStyle(color: Colors.blue[900]), // couleur bleu foncé
                  ),
                ),
              ],
            ),
          ),

          // La carte (FlutterMap)

          // Expanded : remplit tout l'espace disponible
          Expanded(
            child: FlutterMap(
              mapController: _mapController, // contrôleur pour gérer la carte
              // Configuration de la carte
              options: MapOptions(
                initialCenter: const LatLng(37.2403, 10.0503), // centre initial : Metline
                initialZoom: 13,
                onTap: (tapPosition, latLng) => _sendLocation(latLng), // appelle _sendLocation au tap
              ),
              
              // Couches de la carte (fond, tracé, marqueurs)
              children: [
                // Fond OpenStreetMap
                // TileLayer : affiche les tuiles de la carte
                TileLayer(
                  // URL du serveur de tuiles OpenStreetMap
                  urlTemplate:
                      'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                       // Identifiant de l'app (requis par OpenStreetMap)
                  userAgentPackageName: 'com.example.front_end',
                ),

                // Couche 2 : Tracé du trajet (polyline)

                // Affiche le polyline seulement s'il y a au moins 2 points
                if (_polylinePoints.length > 1)
                // URL du serveur de tuiles OpenStreetMap
                  PolylineLayer(
                    polylines: [
                       // Crée un polyline avec les points du trajet
                      Polyline(
                        points: _polylinePoints, // les points du tracé
                        color: Colors.blue, // couleur du tracé
                        strokeWidth: 3, // épaisseur du trait
                      ),
                    ],
                  ),
                
                
                 // Couche 3 : Marqueurs
                 // MarkerLayer : affiche tous les marqueurs enregistrés
                MarkerLayer(markers: _markers),
              ],
            ),
          ),
        ],
      ),
    );
  }
}