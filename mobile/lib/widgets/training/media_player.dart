import 'package:flutter/material.dart';
import 'package:video_player/video_player.dart';

import '../../models/training.dart';

class TrainingMediaPlayer extends StatefulWidget {
  final String mediaUrl;
  final MediaType mediaType;
  final VoidCallback onCompleted;
  final ValueChanged<Duration>? onPositionChanged;
  final ValueChanged<Duration>? onDurationChanged;

  const TrainingMediaPlayer({
    super.key,
    required this.mediaUrl,
    required this.mediaType,
    required this.onCompleted,
    this.onPositionChanged,
    this.onDurationChanged,
  });

  @override
  State<TrainingMediaPlayer> createState() => _TrainingMediaPlayerState();
}

class _TrainingMediaPlayerState extends State<TrainingMediaPlayer> {
  late VideoPlayerController _controller;
  bool _initialized = false;
  bool _completed = false;

  @override
  void initState() {
    super.initState();
    _initController();
  }

  Future<void> _initController() async {
    _controller = VideoPlayerController.networkUrl(Uri.parse(widget.mediaUrl));
    try {
      await _controller.initialize();
      _controller.addListener(_onUpdate);
      widget.onDurationChanged?.call(_controller.value.duration);
      setState(() => _initialized = true);
    } catch (_) {
      // Initialization failed — show error state
      setState(() {});
    }
  }

  void _onUpdate() {
    if (!mounted) return;
    final value = _controller.value;

    widget.onPositionChanged?.call(value.position);

    // Check completion (within 1 second of end)
    if (!_completed &&
        value.duration.inSeconds > 0 &&
        value.position.inSeconds >= value.duration.inSeconds - 1) {
      _completed = true;
      widget.onCompleted();
    }

    if (mounted) setState(() {});
  }

  @override
  void dispose() {
    _controller.removeListener(_onUpdate);
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    if (!_initialized) {
      if (_controller.value.hasError) {
        return _buildError(theme);
      }
      return _buildLoading(theme);
    }

    return Column(
      children: [
        // Video display
        AspectRatio(
          aspectRatio: widget.mediaType == MediaType.audio
              ? 16 / 4
              : _controller.value.aspectRatio,
          child: widget.mediaType == MediaType.audio
              ? _buildAudioVisual(theme)
              : VideoPlayer(_controller),
        ),

        // Progress bar
        _ProgressBar(
          position: _controller.value.position,
          duration: _controller.value.duration,
          onSeek: (position) => _controller.seekTo(position),
        ),

        // Controls
        _PlayerControls(
          isPlaying: _controller.value.isPlaying,
          position: _controller.value.position,
          duration: _controller.value.duration,
          onPlayPause: () {
            setState(() {
              _controller.value.isPlaying
                  ? _controller.pause()
                  : _controller.play();
            });
          },
          onSeekForward: () {
            final pos = _controller.value.position + const Duration(seconds: 10);
            _controller.seekTo(pos);
          },
          onSeekBackward: () {
            final pos = _controller.value.position - const Duration(seconds: 10);
            _controller.seekTo(pos < Duration.zero ? Duration.zero : pos);
          },
        ),
      ],
    );
  }

  Widget _buildAudioVisual(ThemeData theme) {
    return Container(
      color: theme.colorScheme.surfaceContainerHigh,
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              _controller.value.isPlaying
                  ? Icons.graphic_eq
                  : Icons.audiotrack,
              size: 48,
              color: theme.colorScheme.primary,
            ),
            const SizedBox(height: 8),
            Text(
              'Audio',
              style: theme.textTheme.labelLarge?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildLoading(ThemeData theme) {
    return Container(
      height: 200,
      color: theme.colorScheme.surfaceContainerHigh,
      child: const Center(child: CircularProgressIndicator()),
    );
  }

  Widget _buildError(ThemeData theme) {
    return Container(
      height: 200,
      color: theme.colorScheme.surfaceContainerHigh,
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.error_outline, size: 40, color: theme.colorScheme.error),
            const SizedBox(height: 8),
            Text(
              'Impossible de lire le média',
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ProgressBar extends StatelessWidget {
  final Duration position;
  final Duration duration;
  final ValueChanged<Duration> onSeek;

  const _ProgressBar({
    required this.position,
    required this.duration,
    required this.onSeek,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final total = duration.inMilliseconds.toDouble();
    final current = position.inMilliseconds.toDouble();

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: SliderTheme(
        data: SliderThemeData(
          trackHeight: 3,
          thumbShape: const RoundSliderThumbShape(enabledThumbRadius: 6),
          activeTrackColor: theme.colorScheme.primary,
          inactiveTrackColor: theme.colorScheme.surfaceContainerHigh,
          thumbColor: theme.colorScheme.primary,
        ),
        child: Slider(
          value: total > 0 ? (current / total).clamp(0.0, 1.0) : 0.0,
          onChanged: (value) {
            onSeek(Duration(milliseconds: (value * total).round()));
          },
        ),
      ),
    );
  }
}

class _PlayerControls extends StatelessWidget {
  final bool isPlaying;
  final Duration position;
  final Duration duration;
  final VoidCallback onPlayPause;
  final VoidCallback onSeekForward;
  final VoidCallback onSeekBackward;

  const _PlayerControls({
    required this.isPlaying,
    required this.position,
    required this.duration,
    required this.onPlayPause,
    required this.onSeekForward,
    required this.onSeekBackward,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      child: Row(
        children: [
          // Time elapsed
          Text(
            _formatDuration(position),
            style: theme.textTheme.labelSmall?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
          ),
          const Spacer(),

          // Controls
          IconButton(
            onPressed: onSeekBackward,
            icon: const Icon(Icons.replay_10, size: 28),
            tooltip: 'Reculer 10s',
          ),
          IconButton.filled(
            onPressed: onPlayPause,
            icon: Icon(
              isPlaying ? Icons.pause : Icons.play_arrow,
              size: 32,
            ),
            tooltip: isPlaying ? 'Pause' : 'Lecture',
          ),
          IconButton(
            onPressed: onSeekForward,
            icon: const Icon(Icons.forward_10, size: 28),
            tooltip: 'Avancer 10s',
          ),

          const Spacer(),
          // Duration
          Text(
            _formatDuration(duration),
            style: theme.textTheme.labelSmall?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
          ),
        ],
      ),
    );
  }

  String _formatDuration(Duration d) {
    final minutes = d.inMinutes.remainder(60).toString().padLeft(2, '0');
    final seconds = d.inSeconds.remainder(60).toString().padLeft(2, '0');
    if (d.inHours > 0) {
      return '${d.inHours}:$minutes:$seconds';
    }
    return '$minutes:$seconds';
  }
}
