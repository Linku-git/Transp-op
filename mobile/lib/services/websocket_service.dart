import 'dart:async';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:socket_io_client/socket_io_client.dart' as io;
import '../config/api_config.dart';
import '../models/vehicle_position.dart';

class WebSocketService {
  io.Socket? _socket;
  final _positionController = StreamController<VehiclePosition>.broadcast();
  final FlutterSecureStorage _storage;
  bool _isConnected = false;

  WebSocketService({FlutterSecureStorage? storage})
      : _storage = storage ?? const FlutterSecureStorage();

  Stream<VehiclePosition> get positionStream => _positionController.stream;
  bool get isConnected => _isConnected;

  Future<void> connect(String vehicleId) async {
    final token = await _storage.read(key: ApiConfig.accessTokenKey);
    final baseUrl = ApiConfig.baseUrl.replaceAll('/api/v1', '');

    _socket = io.io(baseUrl, <String, dynamic>{
      'transports': ['websocket'],
      'autoConnect': false,
      'auth': {'token': token},
      'query': {'vehicle_id': vehicleId},
    });

    _socket!.onConnect((_) {
      _isConnected = true;
      _socket!.emit('subscribe_vehicle', {'vehicle_id': vehicleId});
    });

    _socket!.on('vehicle_position', (data) {
      if (data is Map<String, dynamic>) {
        _positionController.add(VehiclePosition.fromJson(data));
      }
    });

    _socket!.onDisconnect((_) {
      _isConnected = false;
    });

    _socket!.onConnectError((_) {
      _isConnected = false;
    });

    _socket!.connect();
  }

  void disconnect() {
    _socket?.disconnect();
    _socket?.dispose();
    _socket = null;
    _isConnected = false;
  }

  void dispose() {
    disconnect();
    _positionController.close();
  }
}
