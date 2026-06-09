// importe le package Material Design de Flutter (boutons, appbars, etc.)
import 'package:flutter/material.dart';
import 'pages/map_page.dart';

// Fonction d'entrée : point de départ de l'application Dart/Flutter
void main() {
  // runApp() : initialise et affiche l'application avec le widget LocationApp
  runApp(const LocationApp());
}

class LocationApp extends StatelessWidget {
  // Constructeur avec une clé optionnelle (pattern Flutter standard)
  const LocationApp({super.key});

// build() : construit le widget qui représente l'interface de l'app
  @override
  Widget build(BuildContext context) {
    // MaterialApp : conteneur principal qui configure l'app avec Material Design
    return MaterialApp(
      title: 'Location Service',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(primarySwatch: Colors.blue), // masque la bannière "DEBUG" en haut à droite
      home: const MapPage(), // définit l'écran initial à afficher (MapPage)
    );
  }
}