class NotificationChannels {
  NotificationChannels._();

  static const String rtiAlertId = 'rti_alerts';
  static const String rtiAlertName = 'Alertes transport';
  static const String rtiAlertDesc = 'Notifications d\'arrivée du véhicule';

  static const String routeChangeId = 'route_changes';
  static const String routeChangeName = 'Changements d\'itinéraire';
  static const String routeChangeDesc = 'Modifications de routes et horaires';

  static const String weatherId = 'weather_alerts';
  static const String weatherName = 'Alertes météo';
  static const String weatherDesc = 'Conditions météo affectant les trajets';

  static const String contentId = 'content_updates';
  static const String contentName = 'Contenu';
  static const String contentDesc = 'Nouvelles actualités et formations';

  static const String emergencyId = 'emergency';
  static const String emergencyName = 'Urgences';
  static const String emergencyDesc = 'Alertes de sécurité urgentes';
}
