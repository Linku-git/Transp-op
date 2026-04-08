import 'dart:async';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:logger/logger.dart';
import '../models/notification_item.dart';
import 'api_client.dart';

final _log = Logger();

class PushNotificationService {
  final FirebaseMessaging _fcm;
  final ApiClient _apiClient;
  final _notificationController = StreamController<NotificationItem>.broadcast();
  String? _currentToken;

  PushNotificationService({
    FirebaseMessaging? fcm,
    required ApiClient apiClient,
  })  : _fcm = fcm ?? FirebaseMessaging.instance,
        _apiClient = apiClient;

  Stream<NotificationItem> get notificationStream => _notificationController.stream;
  String? get currentToken => _currentToken;

  Future<void> initialize() async {
    // Request permission
    final settings = await _fcm.requestPermission(
      alert: true,
      badge: true,
      sound: true,
      provisional: false,
    );

    if (settings.authorizationStatus == AuthorizationStatus.denied) {
      _log.w('Push notification permission denied');
      return;
    }

    // Get and register token
    _currentToken = await _fcm.getToken();
    if (_currentToken != null) {
      await _registerToken(_currentToken!);
    }

    // Listen for token refresh
    _fcm.onTokenRefresh.listen((newToken) async {
      _currentToken = newToken;
      await _registerToken(newToken);
    });

    // Foreground messages
    FirebaseMessaging.onMessage.listen(_handleForegroundMessage);

    // Background message tap (app was in background)
    FirebaseMessaging.onMessageOpenedApp.listen(_handleMessageTap);

    // Check if app was opened from terminated state via notification
    final initialMessage = await _fcm.getInitialMessage();
    if (initialMessage != null) {
      _handleMessageTap(initialMessage);
    }
  }

  Future<void> _registerToken(String token) async {
    try {
      await _apiClient.dio.post(
        '/devices/register',
        data: {
          'token': token,
          'platform': _getPlatform(),
        },
      );
      _log.d('FCM token registered with backend');
    } catch (e) {
      _log.e('Failed to register FCM token: $e');
    }
  }

  void _handleForegroundMessage(RemoteMessage message) {
    final item = NotificationItem.fromFCM({
      'notification': {
        'title': message.notification?.title,
        'body': message.notification?.body,
      },
      'data': message.data,
    });
    _notificationController.add(item);
  }

  void _handleMessageTap(RemoteMessage message) {
    final item = NotificationItem.fromFCM({
      'notification': {
        'title': message.notification?.title,
        'body': message.notification?.body,
      },
      'data': message.data,
    });
    _notificationController.add(item);
  }

  String _getPlatform() {
    // Simplified — in production use Platform.isIOS/isAndroid
    return 'android';
  }

  void dispose() {
    _notificationController.close();
  }
}
