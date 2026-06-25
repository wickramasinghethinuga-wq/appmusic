"""
Study Focus Music Player
=========================
A premium, Spotify-inspired ambient/focus sound player built with Kivy.
Fully fixed and optimized for Buildozer compilation (all copy-paste syntax errors resolved).
"""

import random
import threading

from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.metrics import dp
from kivy.properties import (
    StringProperty,
    NumericProperty,
    BooleanProperty,
    ObjectProperty,
    ListProperty,
)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import AsyncImage
from kivy.animation import Animation

# ---------------------------------------------------------------------------
# Theme constants & Top Padding
# ---------------------------------------------------------------------------
BG_COLOR = (0x12 / 255, 0x12 / 255, 0x12 / 255, 1)         # #121212
CARD_COLOR = (0x1E / 255, 0x1E / 255, 0x1E / 255, 1)       # slightly lighter charcoal
ACCENT_COLOR = (0x1D / 255, 0xB9 / 255, 0x54 / 255, 1)     # #1DB954
ACCENT_DIM = (0x1D / 255, 0xB9 / 255, 0x54 / 255, 0.18)
TEXT_PRIMARY = (1, 1, 1, 1)
TEXT_SECONDARY = (0.7, 0.7, 0.7, 1)
DIVIDER_COLOR = (1, 1, 1, 0.08)
ENV_TOP_PAD = 28                                           # Top padding for phone status bars

Window.clearcolor = BG_COLOR

# ---------------------------------------------------------------------------
# Sound library — Public working MP3 direct streams
# ---------------------------------------------------------------------------
SOUND_LIBRARY = [
    {
        "id": "lofi",
        "title": "Lo-Fi Beats",
        "subtitle": "Chill hip-hop study loop",
        "artwork": "https://images.unsplash.com/photo-1518609878373-06d740f60d8b?w=600&q=80",
        "urls": [
            "https://cdn.pixabay.com/download/audio/2022/03/15/audio_c8f7d57f3a.mp3",
            "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
        ],
    },
    {
        "id": "rain",
        "title": "Rainstorms",
        "subtitle": "Heavy rain + distant thunder",
        "artwork": "https://images.unsplash.com/photo-1428592953211-077101b2021b?w=600&q=80",
        "urls": [
            "https://cdn.pixabay.com/download/audio/2021/09/06/audio_1b196b6f3e.mp3",
            "https://www.soundjay.com/nature/sounds/rain-01.mp3",
        ],
    },
    {
        "id": "white_noise",
        "title": "White Noise",
        "subtitle": "Pure focus static",
        "artwork": "https://images.unsplash.com/photo-1505904267569-f02eaeb45a4c?w=600&q=80",
        "urls": [
            "https://cdn.pixabay.com/download/audio/2021/10/25/audio_5f8a1a8f1c.mp3",
            "https://www.soundjay.com/nature/sounds/weather-white-noise.mp3",
        ],
    },
    {
        "id": "piano",
        "title": "Ambient Piano",
        "subtitle": "Soft minimal piano keys",
        "artwork": "https://images.unsplash.com/photo-1520523839897-bd0b52f945a0?w=600&q=80",
        "urls": [
            "https://cdn.pixabay.com/download/audio/2022/05/27/audio_1808fbf07a.mp3",
            "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3",
        ],
    },
    {
        "id": "ocean",
        "title": "Ocean Meditation",
        "subtitle": "Gentle waves on the shore",
        "artwork": "https://images.unsplash.com/photo-1505142468610-359e7d316be0?w=600&q=80",
        "urls": [
            "https://cdn.pixabay.com/download/audio/2021/08/09/audio_88447e769f.mp3",
            "https://www.soundjay.com/nature/sounds/ocean-wave-1.mp3",
        ],
    },
]

# ---------------------------------------------------------------------------
# Reusable visual components
# ---------------------------------------------------------------------------
class RoundedCanvasWidget(Widget):
    bg_color = ListProperty(CARD_COLOR)
    radius = NumericProperty(dp(16))
    border_color = ListProperty([0, 0, 0, 0])
    border_width = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            self._color_instr = Color(*self.bg_color)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])
            self._border_color_instr = Color(*self.border_color)
            self._border_line = Line(width=self.border_width)
        self.bind(
            pos=self._update_canvas,
            size=self._update_canvas,
            bg_color=self._update_color,
            radius=self._update_canvas,
            border_color=self._update_border_color,
            border_width=self._update_canvas,
        )

    def _update_canvas(self, *_args):
        self._rect.pos = self.pos
        self._rect.size = self.size
        self._rect.radius = [self.radius]
        self._border_line.rounded_rectangle = (self.x, self.y, self.width, self.height, self.radius)
        self._border_line.width = self.border_width

    def _update_color(self, *_args):
        self._color_instr.rgba = self.bg_color

    def _update_border_color(self, *_args):
        self._border_color_instr.rgba = self.border_color


class SoundCard(ButtonBehavior, RoundedCanvasWidget):
    title_text = StringProperty("")
    subtitle_text = StringProperty("")
    artwork_url = StringProperty("")
    active = BooleanProperty(False)
    sound_id = StringProperty("")

    def __init__(self, sound_data, on_select, **kwargs):
        super().__init__(**kwargs)
        self.sound_id = sound_data["id"]
        self.title_text = sound_data["title"]
        self.subtitle_text = sound_data["subtitle"]
        self.artwork_url = sound_data["artwork"]
        self._on_select_cb = on_select
        self.size_hint = (1, None)
        self.height = dp(78)
        self.bg_color = CARD_COLOR
        self.border_width = 0

        root = BoxLayout(
            orientation="horizontal",
            padding=(dp(12), dp(10)),
            spacing=dp(14),
            size=self.size,
            pos=self.pos,
        )
        self.bind(pos=lambda *_: setattr(root, "pos", self.pos))
        self.bind(size=lambda *_: setattr(root, "size", self.size))

        thumb_wrap = FloatLayout(size_hint=(None, 1), width=dp(56))
        self.thumb = AsyncImage(
            source=self.artwork_url,
            size_hint=(1, 1),
            allow_stretch=True,
            keep_ratio=False,
        )
        thumb_wrap.add_widget(self.thumb)
        root.add_widget(thumb_wrap)

        text_box = BoxLayout(orientation="vertical", spacing=dp(2))
        self.title_label = Label(
            text=self.title_text,
            font_size="16sp",
            bold=True,
            color=TEXT_PRIMARY,
            halign="left",
            valign="middle",
            size_hint=(1, None),
            height=dp(20),
        )
        self.title_label.bind(size=self._sync_label_text_size)
        self.subtitle_label = Label(
            text=self.subtitle_text,
            font_size="12sp",
            color=TEXT_SECONDARY,
            halign="left",
            valign="middle",
            size_hint=(1, None),
            height=dp(16),
        )
        self.subtitle_label.bind(size=self._sync_label_text_size)
        text_box.add_widget(self.title_label)
        text_box.add_widget(self.subtitle_label)
        root.add_widget(text_box)

        self.status_dot = Widget(size_hint=(None, None), size=(dp(10), dp(10)))
        with self.status_dot.canvas:
            self._dot_color = Color(*ACCENT_COLOR)
            self._dot_shape = RoundedRectangle(
                pos=self.status_dot.pos, size=self.status_dot.size, radius=[dp(5)]
            )
        self.status_dot.bind(pos=self._update_dot, size=self._update_dot)
        self.status_dot.opacity = 0
        dot_wrap = FloatLayout(size_hint=(None, 1), width=dp(20))
        dot_wrap.add_widget(self.status_dot)
        root.add_widget(dot_wrap)

        self.add_widget(root)

    def _sync_label_text_size(self, instance, _size):
        instance.text_size = instance.size

    def _update_dot(self, *_args):
        self._dot_shape.pos = self.status_dot.pos
        self._dot_shape.size = self.status_dot.size

    def on_press(self):
        Animation.cancel_all(self, "bg_color")
        Animation(bg_color=ACCENT_DIM, duration=0.08).start(self)
        Clock.schedule_once(lambda *_: self._restore_bg(), 0.12)
        if self._on_select_cb:
            self._on_select_cb(self.sound_id)

    def _restore_bg(self):
        target = ACCENT_DIM if self.active else CARD_COLOR
        Animation(bg_color=target, duration=0.18).start(self)

    def set_active(self, is_active: bool):
        self.active = is_active
        self.border_width = dp(1.5) if is_active else 0
        self.border_color = ACCENT_COLOR if is_active else [0, 0, 0, 0]
        self.bg_color = ACCENT_DIM if is_active else CARD_COLOR
        self.status_dot.opacity = 1 if is_active else 0


class CircleIconButton(ButtonBehavior, Widget):
    bg_color = ListProperty(ACCENT_COLOR)
    icon_text = StringProperty("▶")
    icon_color = ListProperty([0, 0, 0, 1])
    icon_font_size = NumericProperty(dp(28))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            self._color_instr = Color(*self.bg_color)
            self._circle = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(999)])
        self.label = Label(
            text=self.icon_text,
            font_size=self.icon_font_size,
            color=self.icon_color,
            bold=True,
        )
        self.add_widget(self.label)
        self.bind(
            pos=self._update_canvas,
            size=self._update_canvas,
            bg_color=self._update_color,
            icon_text=lambda *_: setattr(self.label, "text", self.icon_text),
            icon_color=lambda *_: setattr(self.label, "color", self.icon_color),
        )

    def _update_canvas(self, *_args):
        self._circle.pos = self.pos
        self._circle.size = self.size
        self._circle.radius = [min(self.width, self.height) / 2]
        self.label.center = self.center
        self.label.size = self.size

    def _update_color(self, *_args):
        self._color_instr.rgba = self.bg_color

    def on_press(self):
        Animation.cancel_all(self, "size")
        orig = self.size[:]
        Animation(size=(orig[0] * 0.9, orig[1] * 0.9), duration=0.06).start(self)
        Clock.schedule_once(
            lambda *_: Animation(size=orig, duration=0.1).start(self), 0.07
        )


class ProgressTrack(Widget):
    progress = NumericProperty(0.0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            self._bg_color = Color(1, 1, 1, 0.12)
            self._bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(4)])
            self._fg_color = Color(*ACCENT_COLOR)
            self._fg_rect = RoundedRectangle(pos=self.pos, size=(0, self.height), radius=[dp(4)])
        self.bind(pos=self._redraw, size=self._redraw, progress=self._redraw)

    def _redraw(self, *_args):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size
        fg_w = max(dp(8), self.width * min(max(self.progress, 0), 1))
        self._fg_rect.pos = self.pos
        self._fg_rect.size = (fg_w, self.height)


# ---------------------------------------------------------------------------
# Audio Engine
# ---------------------------------------------------------------------------
class AudioEngine:
    def __init__(self, on_state_change, on_error, on_progress):
        self.sound = None
        self.current_track = None
        self.volume = 0.7
        self._on_state_change = on_state_change
        self._on_error = on_error
        self._on_progress = on_progress
        self._progress_event = None
        self._load_lock = threading.Lock()
        self._loading = False

    def load_and_play(self, track_data):
        if self._loading:
            return
        self._loading = True
        self._stop_progress_clock()
        self._on_state_change("loading", track_data)
        thread = threading.Thread(
            target=self._threaded_load, args=(track_data,), daemon=True
        )
        thread.start()

    def toggle_pause(self):
        if not self.sound:
            return
        if self.sound.state == "play":
            self.sound.stop()
            self._stop_progress_clock()
            self._on_state_change("paused", self.current_track)
        else:
            self.sound.play()
            self._start_progress_clock()
            self._on_state_change("playing", self.current_track)

    def stop(self):
        if self.sound:
            self.sound.stop()
        self._stop_progress_clock()
        self._on_state_change("stopped", self.current_track)

    def set_volume(self, value: float):
        self.volume = max(0.0, min(1.0, value))
        if self.sound:
            self.sound.volume = self.volume

    def _threaded_load(self, track_data):
        with self._load_lock:
            new_sound = None
            for url in track_data["urls"]:
                try:
                    candidate = SoundLoader.load(url)
                    if candidate is not None:
                        new_sound = candidate
                        break
                except Exception:
                    continue
            Clock.schedule_once(
                lambda *_: self._finish_load_on_main_thread(new_sound, track_data)
            )

    @mainthread
    def _finish_load_on_main_thread(self, new_sound, track_data):
        self._loading = False
        if self.sound:
            self.sound.stop()
            self.sound.unload()
            self.sound = None

        if new_sound is None:
            self._on_error(track_data)
            self._on_state_change("error", track_data)
            return

        self.sound = new_sound
        self.sound.loop = True
        self.sound.volume = self.volume
        self.current_track = track_data
        self.sound.play()
        self._start_progress_clock()
        self._on_state_change("playing", track_data)

    def _start_progress_clock(self):
        self._stop_progress_clock()
        self._progress_event = Clock.schedule_interval(self._tick_progress, 0.3)

    def _stop_progress_clock(self):
        if self._progress_event:
            self._progress_event.cancel()
            self._progress_event = None

    def _tick_progress(self, _dt):
        if self.sound and self.sound.length:
            fraction = (self.sound.get_pos() or 0) / self.sound.length
            self._on_progress(fraction, self.sound.get_pos(), self.sound.length)

    def teardown(self):
        self._stop_progress_clock()
        if self.sound:
            self.sound.stop()
            self.sound.unload()
            self.sound = None


# ---------------------------------------------------------------------------
# UI Design Layout
# ---------------------------------------------------------------------------
class RootLayout(FloatLayout):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app

        with self.canvas.before:
            Color(*BG_COLOR)
            self._bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[0])
        self.bind(pos=self._sync_bg, size=self._sync_bg)

        main_col = BoxLayout(
            orientation="vertical",
            size_hint=(1, 1),
            padding=(dp(20), dp(ENV_TOP_PAD), dp(20), dp(16)),
            spacing=dp(14),
        )
        self.add_widget(main_col)

        # Header
        header = BoxLayout(
            orientation="vertical", size_hint=(1, None), height=dp(54), spacing=dp(2)
        )
        eyebrow = Label(
            text="FOCUS ENVIRONMENT",
            font_size="11sp",
            color=ACCENT_COLOR,
            bold=True,
            size_hint=(1, None),
            height=dp(16),
            halign="left",
            valign="bottom",
        )
        eyebrow.bind(size=lambda i, s: setattr(i, "text_size", s))
        self.header_title = Label(
            text="Select a sound to begin",
            font_size="22sp",
            bold=True,
            color=TEXT_PRIMARY,
            size_hint=(1, None),
            height=dp(32),
            halign="left",
            valign="top",
        )
        self.header_title.bind(size=lambda i, s: setattr(i, "text_size", s))
        header.add_widget(eyebrow)
        header.add_widget(self.header_title)
        main_col.add_widget(header)

        # Center card artwork + titles
        center_card = RoundedCanvasWidget(
            size_hint=(1, None), height=dp(260), radius=dp(24), bg_color=CARD_COLOR
        )
        center_inner = BoxLayout(
            orientation="vertical",
            padding=dp(18),
            spacing=dp(10),
            size=center_card.size,
            pos=center_card.pos,
        )
        center_card.bind(
            pos=lambda *_: setattr(center_inner, "pos", center_card.pos),
            size=lambda *_: setattr(center_inner, "size", center_card.size),
        )

        art_wrap = RoundedCanvasWidget(
            size_hint=(1, 1), radius=dp(18), bg_color=(0, 0, 0, 0.3)
        )
        self.artwork = AsyncImage(
            source=SOUND_LIBRARY[0]["artwork"],
            allow_stretch=True,
            keep_ratio=False,
            size_hint=(1, 1),
        )
        art_wrap.add_widget(self.artwork)
        self.artwork.bind(
            pos=lambda *_: setattr(self.artwork, "pos", art_wrap.pos),
            size=lambda *_: setattr(self.artwork, "size", art_wrap.size),
        )
        art_wrap.bind(
            pos=lambda *_: setattr(self.artwork, "pos", art_wrap.pos),
            size=lambda *_: setattr(self.artwork, "size", art_wrap.size),
        )
        center_inner.add_widget(art_wrap)

        track_box = BoxLayout(
            orientation="vertical", size_hint=(1, None), height=dp(46)
        )
        self.track_title = Label(
            text="Nothing playing",
            font_size="17sp",
            bold=True,
            color=TEXT_PRIMARY,
            size_hint=(1, None),
            height=dp(24),
            halign="left",
            valign="middle",
        )
        self.track_title.bind(size=lambda i, s: setattr(i, "text_size", s))
        self.track_subtitle = Label(
            text="Tap a card below to start your session",
            font_size="13sp",
            color=TEXT_SECONDARY,
            size_hint=(1, None),
            height=dp(20),
            halign="left",
            valign="middle",
        )
        self.track_subtitle.bind(size=lambda i, s: setattr(i, "text_size", s))
        track_box.add_widget(self.track_title)
        track_box.add_widget(self.track_subtitle)
        center_inner.add_widget(track_box)

        center_card.add_widget(center_inner)
        main_col.add_widget(center_card)

        # Progress bar
        progress_row = BoxLayout(
            orientation="vertical", size_hint=(1, None), height=dp(28), spacing=dp(4)
        )
        self.progress_track = ProgressTrack(size_hint=(1, None), height=dp(6))
        time_row = BoxLayout(size_hint=(1, None), height=dp(16))
        self.time_elapsed = Label(
            text="0:00", font_size="11sp", color=TEXT_SECONDARY, halign="left"
        )
        self.time_elapsed.bind(size=lambda i, s: setattr(i, "text_size", s))
        self.time_total = Label(
            text="∞ (looping)",
            font_size="11sp",
            color=TEXT_SECONDARY,
            halign="right",
        )
        self.time_total.bind(size=lambda i, s: setattr(i, "text_size", s))
        time_row.add_widget(self.time_elapsed)
        time_row.add_widget(self.time_total)
        progress_row.add_widget(self.progress_track)
        progress_row.add_widget(time_row)
        main_col.add_widget(progress_row)

        # Transport Controls
        controls_row = BoxLayout(
            size_hint=(1, None),
            height=dp(84),
            spacing=dp(24),
            padding=(dp(10), 0),
        )
        controls_row.add_widget(Widget())

        self.stop_btn = CircleIconButton(
            size_hint=(None, None),
            size=(dp(54), dp(54)),
            bg_color=(1, 1, 1, 0.08),
            icon_text="■",
            icon_color=TEXT_PRIMARY,
            icon_font_size="18sp",
        )
        self.stop_btn.bind(on_press=lambda *_: self.app.on_stop())
        controls_row.add_widget(self.stop_btn)

        self.play_btn = CircleIconButton(
            size_hint=(None, None),
            size=(dp(72), dp(72)),
            bg_color=ACCENT_COLOR,
            icon_text="▶",
            icon_color=(0, 0, 0, 1),
            icon_font_size="30sp",
        )
        self.play_btn.bind(on_press=lambda *_: self.app.on_play_pause())
        controls_row.add_widget(self.play_btn)

        self.next_btn = CircleIconButton(
            size_hint=(None, None),
            size=(dp(54), dp(54)),
            bg_color=(1, 1, 1, 0.08),
            icon_text="⟳",
            icon_color=TEXT_PRIMARY,
            icon_font_size="22sp",
        )
        self.next_btn.bind(on_press=lambda *_: self.app.on_shuffle_next())
        controls_row.add_widget(self.next_btn)

        controls_row.add_widget(Widget())
        main_col.add_widget(controls_row)

        # Volume slider
        volume_row = BoxLayout(
            size_hint=(1, None), height=dp(36), spacing=dp(10)
        )
        vol_icon = Label(text="🔈", font_size="16sp", size_hint=(None, 1), width=dp(24))
        self.volume_slider = Slider(
            min=0,
            max=1,
            value=0.7,
            size_hint=(1, 1),
            cursor_size=(dp(18), dp(18)),
        )
        self.volume_slider.bind(value=lambda inst, val: self.app.on_volume_change(val))
        vol_icon_loud = Label(text="🔊", font_size="16sp", size_hint=(None, 1), width=dp(24))
        volume_row.add_widget(vol_icon)
        volume_row.add_widget(self.volume_slider)
        volume_row.add_widget(vol_icon_loud)
        main_col.add_widget(volume_row)

        # Sound card section title
        section_label = Label(
            text="Choose your soundscape",
            font_size="13sp",
            bold=True,
            color=TEXT_SECONDARY,
            size_hint=(1, None),
            height=dp(20),
            halign="left",
        )
        section_label.bind(size=lambda i, s: setattr(i, "text_size", s))
        main_col.add_widget(section_label)

        # Scrollview
        scroll = ScrollView(size_hint=(1, 1), bar_width=dp(2))
        cards_col = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            size_hint=(1, None),
            padding=(0, 0, 0, dp(8)),
        )
        cards_col.bind(minimum_height=cards_col.setter("height"))

        self.cards = {}
        for sound_data in SOUND_LIBRARY:
            card = SoundCard(sound_data, on_select=self.app.on_select_sound)
            self.cards[sound_data["id"]] = card
            cards_col.add_widget(card)

        scroll.add_widget(cards_col)
        main_col.add_widget(scroll)

    def _sync_bg(self, *_args):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size


# ---------------------------------------------------------------------------
# App Main Entry
# ---------------------------------------------------------------------------
class MainApp(App):
    title = "Study Focus"

    def build(self):
        self.engine = AudioEngine(
            on_state_change=self._handle_state_change,
            on_error=self._handle_load_error,
            on_progress=self._handle_progress,
        )
        self.current_sound_id = None
        self.played_history = []
        self.root_layout = RootLayout(self)
        return self.root_layout

    def on_select_sound(self, sound_id):
        track_data = next((s for s in SOUND_LIBRARY if s["id"] == sound_id), None)
        if not track_data:
            return
        self.current_sound_id = sound_id
        self._highlight_active_card(sound_id)
        self._update_now_playing_preview(track_data)
        self.engine.load_and_play(track_data)
        if sound_id not in self.played_history:
            self.played_history.append(sound_id)

    def on_play_pause(self):
        if not self.engine.sound:
            if SOUND_LIBRARY:
                self.on_select_sound(SOUND_LIBRARY[0]["id"])
            return
        self.engine.toggle_pause()

    def on_stop(self):
        self.engine.stop()
        if self.current_sound_id:
            card = self.root_layout.cards.get(self.current_sound_id)
            if card:
                card.set_active(False)
        self.current_sound_id = None
        self.root_layout.header_title.text = "Select a sound to begin"
        self.root_layout.track_title.text = "Nothing playing"
        self.root_layout.track_subtitle.text = "Tap a card below to start your session"
        self.root_layout.progress_track.progress = 0

    def on_shuffle_next(self):
        choices = [s for s in SOUND_LIBRARY if s["id"] != self.current_sound_id]
        if not choices:
            choices = SOUND_LIBRARY
        next_track = random.choice(choices)
        self.on_select_sound(next_track["id"])

    def on_volume_change(self, value):
        self.engine.set_volume(value)

    def _handle_state_change(self, state, track_data):
        if state == "loading":
            self.root_layout.header_title.text = f"Loading {track_data['title']}..."
            self.root_layout.play_btn.icon_text = "⏳"
        elif state == "playing":
            self.root_layout.header_title.text = f"Now Playing: {track_data['title']}"
            self.root_layout.play_btn.icon_text = "❚❚"
            self._animate_track_title()
        elif state == "paused":
            self.root_layout.header_title.text = f"Paused: {track_data['title']}"
            self.root_layout.play_btn.icon_text = "▶"
        elif state == "stopped" or state == "error":
            self.root_layout.play_btn.icon_text = "▶"

    def _handle_load_error(self, track_data):
        self.root_layout.header_title.text = (
            f"Couldn't load {track_data['title']} — try another sound"
        )
        self.root_layout.track_subtitle.text = "All stream sources failed. Tap to retry."
        if self.current_sound_id:
            card = self.root_layout.cards.get(self.current_sound_id)
            if card:
                card.set_active(False)

    def _handle_progress(self, fraction, pos, length):
        self.root_layout.progress_track.progress = fraction
        self.root_layout.time_elapsed.text = self._format_time(pos)
        self.root_layout.time_total.text = self._format_time(length)

    def _highlight_active_card(self, active_id):
        for sid, card in self.root_layout.cards.items():
            card.set_active(sid == active_id)

    def _update_now_playing_preview(self, track_data):
        self.root_layout.artwork.source = track_data["artwork"]
        self.root_layout.track_title.text = track_data["title"]
        self.root_layout.track_subtitle.text = track_data["subtitle"]

    def _animate_track_title(self):
        label = self.root_layout.track_title
        Animation.cancel_all(label, "opacity")
        label.opacity = 0
        Animation(opacity=1, duration=0.4, t="out_quad").start(label)

    @staticmethod
    def _format_time(seconds):
        if not seconds or seconds < 0:
            return "0:00"
        m, s = divmod(int(seconds), 60)
        return f"{m}:{s:02d}"

    def on_stop_app(self, *_args):
        self.engine.teardown()

    def on_pause(self):
        return True


if __name__ == "__main__":
    MainApp().run()