import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';

class SqliteStorageService {
  Database? _db;

  Future<void> initialize() async {
    final dbPath = await getDatabasesPath();
    _db = await openDatabase(
      join(dbPath, 'transpop_offline.db'),
      version: 1,
      onCreate: _createTables,
    );
  }

  Future<void> _createTables(Database db, int version) async {
    await db.execute('''
      CREATE TABLE trip_history (
        id TEXT PRIMARY KEY,
        data TEXT NOT NULL,
        date TEXT NOT NULL,
        cached_at TEXT NOT NULL
      )
    ''');
    await db.execute('''
      CREATE TABLE content_library (
        id TEXT PRIMARY KEY,
        data TEXT NOT NULL,
        type TEXT,
        cached_at TEXT NOT NULL
      )
    ''');
    await db.execute('''
      CREATE TABLE notifications (
        id TEXT PRIMARY KEY,
        data TEXT NOT NULL,
        received_at TEXT NOT NULL,
        is_read INTEGER DEFAULT 0
      )
    ''');
    await db.execute('CREATE INDEX idx_trip_date ON trip_history(date)');
    await db.execute('CREATE INDEX idx_content_type ON content_library(type)');
    await db.execute('CREATE INDEX idx_notif_received ON notifications(received_at)');
  }

  Database get db {
    if (_db == null) throw StateError('SQLite not initialized');
    return _db!;
  }

  // Trip history
  Future<void> saveTripHistory(String id, String jsonData, String date) async {
    await db.insert(
      'trip_history',
      {'id': id, 'data': jsonData, 'date': date, 'cached_at': DateTime.now().toIso8601String()},
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }

  Future<List<Map<String, dynamic>>> getTripHistory({int limit = 100}) async {
    return db.query('trip_history', orderBy: 'date DESC', limit: limit);
  }

  // Content library
  Future<void> saveContent(String id, String jsonData, String? type) async {
    await db.insert(
      'content_library',
      {'id': id, 'data': jsonData, 'type': type, 'cached_at': DateTime.now().toIso8601String()},
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }

  Future<List<Map<String, dynamic>>> getContent({String? type, int limit = 50}) async {
    return db.query(
      'content_library',
      where: type != null ? 'type = ?' : null,
      whereArgs: type != null ? [type] : null,
      orderBy: 'cached_at DESC',
      limit: limit,
    );
  }

  // Notifications
  Future<void> saveNotification(String id, String jsonData, String receivedAt) async {
    await db.insert(
      'notifications',
      {'id': id, 'data': jsonData, 'received_at': receivedAt, 'is_read': 0},
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }

  Future<void> markNotificationRead(String id) async {
    await db.update('notifications', {'is_read': 1}, where: 'id = ?', whereArgs: [id]);
  }

  Future<List<Map<String, dynamic>>> getNotifications({int limit = 100}) async {
    return db.query('notifications', orderBy: 'received_at DESC', limit: limit);
  }

  Future<void> clearAll() async {
    await db.delete('trip_history');
    await db.delete('content_library');
    await db.delete('notifications');
  }

  Future<void> close() async {
    await _db?.close();
  }
}
