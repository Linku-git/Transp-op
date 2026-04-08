class NightModeHelper {
  static const int nightStartHour = 20;
  static const int nightEndHour = 6;
  static const int nightEndMinute = 30;

  static bool isNightTime([DateTime? now]) {
    final time = now ?? DateTime.now();
    final hour = time.hour;
    final minute = time.minute;

    if (hour >= nightStartHour) return true;
    if (hour < nightEndHour) return true;
    if (hour == nightEndHour && minute <= nightEndMinute) return true;
    return false;
  }
}
