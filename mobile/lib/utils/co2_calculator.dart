class Co2Calculator {
  Co2Calculator._();

  // Average car emits ~120g CO2 per km (Morocco fleet average)
  static const double carEmissionGPerKm = 120.0;
  // Company bus emits ~30g CO2 per passenger-km
  static const double busEmissionGPerPassengerKm = 30.0;

  static double savedPerTripKg(double distanceKm) {
    final carEmission = distanceKm * carEmissionGPerKm;
    final busEmission = distanceKm * busEmissionGPerPassengerKm;
    return (carEmission - busEmission) / 1000.0;
  }

  static double totalSavedKg(List<double> tripDistancesKm) {
    return tripDistancesKm.fold(0.0, (sum, d) => sum + savedPerTripKg(d));
  }

  static String formatCo2(double kg) {
    if (kg >= 1000) return '${(kg / 1000).toStringAsFixed(1)} t';
    return '${kg.toStringAsFixed(1)} kg';
  }

  static int treesEquivalent(double co2Kg) {
    // One tree absorbs ~22 kg CO2/year
    return (co2Kg / 22.0).round();
  }
}
