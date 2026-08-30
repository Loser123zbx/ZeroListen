# -*- coding: utf-8 -*-
"""ZeroListen 离线 HTML 播放器生成器。

生成一个自包含(仅依赖相对路径音频文件)的 index.html。
风格: 淡蓝色 + 白色, 简介, 直角控件。
包含: 播放列表(单词+释义)、上一首/下一首/暂停、进度条,
以及跟读设置(读几遍、间隔秒数或音频时长倍数)。
"""

import json

_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{TITLE}}</title>
<style>
  :root {
    --blue: #3a7bd5;
    --blue-deep: #2f65b3;
    --blue-bg: #eef4fb;
    --blue-line: #d5e3f4;
    --blue-hover: #e3f0fd;
    --blue-active: #cfe5fb;
    --ink: #1f2d3d;
    --muted: #6b7a8d;
  }
  * { box-sizing: border-box; border-radius: 0; }
  html, body { margin: 0; height: 100%; }
  body {
    font-family: "Segoe UI", "Microsoft YaHei", "PingFang SC", sans-serif;
    color: var(--ink);
    background: var(--blue-bg);
    display: flex;
    flex-direction: column;
    height: 100vh;
  }
  header {
    background: #fff;
    border-bottom: 1px solid var(--blue-line);
    padding: 14px 22px;
    display: flex;
    align-items: baseline;
    gap: 14px;
  }
  header h1 { font-size: 20px; margin: 0; font-weight: 600; }
  header .sub { color: var(--muted); font-size: 13px; }
  main { flex: 1; display: flex; min-height: 0; }

  .playlist-panel {
    width: 300px;
    min-width: 220px;
    background: #fff;
    border-right: 1px solid var(--blue-line);
    display: flex;
    flex-direction: column;
  }
  .panel-title {
    padding: 12px 16px;
    font-weight: 600;
    border-bottom: 1px solid var(--blue-line);
    background: #f6fafd;
    font-size: 14px;
  }
  #playlist { list-style: none; margin: 0; padding: 0; overflow-y: auto; flex: 1; }
  #playlist li {
    padding: 10px 16px;
    cursor: pointer;
    border-bottom: 1px solid #eef2f7;
  }
  #playlist li:hover { background: var(--blue-hover); }
  #playlist li.active { background: var(--blue-active); border-left: 3px solid var(--blue); }
  #playlist .w { font-size: 15px; font-weight: 600; }
  #playlist .m { font-size: 12px; color: var(--muted); margin-top: 2px; }

  .stage {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 20px;
  }
  .word-display {
    text-align: center;
    margin-bottom: 18px;
    max-width: 90%;
  }
  .word { font-size: 64px; font-weight: 700; line-height: 1.1; word-break: break-word; }
  .meaning { font-size: 44px; color: var(--muted); margin-top: 8px; word-break: break-word; }

  .progress-row { width: 100%; max-width: 640px; display: flex; align-items: center; gap: 10px; }
  .progress-row span { font-size: 12px; color: var(--muted); min-width: 42px; text-align: center; }
  .progress-bar {
    flex: 1; height: 8px; background: var(--blue-line);
    cursor: pointer; position: relative;
  }
  #progress-fill { height: 100%; width: 0%; background: var(--blue); }

  .controls { display: flex; gap: 10px; margin: 18px 0; }
  button {
    border: 1px solid var(--blue);
    background: #fff;
    color: var(--blue-deep);
    font-size: 15px;
    padding: 9px 22px;
    cursor: pointer;
    transition: background .12s, color .12s;
  }
  button:hover { background: var(--blue); color: #fff; }
  button:active { background: var(--blue-deep); color: #fff; }
  button.primary { background: var(--blue); color: #fff; }
  button.primary:hover { background: var(--blue-deep); }

  .shadowing {
    background: #fff;
    border: 1px solid var(--blue-line);
    padding: 12px 16px;
    display: flex;
    align-items: center;
    gap: 14px;
    flex-wrap: wrap;
    font-size: 13px;
    color: var(--ink);
  }
  .shadowing label { display: inline-flex; align-items: center; gap: 5px; cursor: pointer; }
  .shadowing input[type="number"] {
    width: 60px; padding: 5px 6px; border: 1px solid var(--blue-line);
    font-size: 13px;
  }
  .shadowing select {
    padding: 5px 6px; border: 1px solid var(--blue-line);
    font-size: 13px; background: #fff; color: var(--ink);
  }
  .shadowing .grp { display: inline-flex; align-items: center; gap: 8px; }
  .shadowing .sep { color: var(--blue-line); }
</style>
</head>
<body>
<header>
  <h1>{{TITLE}}</h1>
  <span class="sub" id="meta"></span>
</header>
<main>
  <aside class="playlist-panel">
    <div class="panel-title">播放列表</div>
    <ul id="playlist"></ul>
  </aside>
  <section class="stage">
    <div class="word-display">
      <div class="word" id="word">—</div>
      <div class="meaning" id="meaning">—</div>
    </div>
    <div class="progress-row">
      <span id="cur">00:00</span>
      <div class="progress-bar" id="bar"><div id="progress-fill"></div></div>
      <span id="dur">00:00</span>
    </div>
    <div class="controls">
      <button id="prev">上一首</button>
      <button id="play" class="primary">播放</button>
      <button id="next">下一首</button>
    </div>
    <div class="shadowing">
      <label><input type="checkbox" id="shadow-on"> 跟读模式</label>
      <span class="sep">|</span>
      <label>读几遍 <input type="number" id="repeat" min="1" max="10" value="{{REPEAT}}"></label>
      <span class="sep">|</span>
      <span class="grp">间隔
        <label><input type="radio" name="imode" value="seconds" {{SECONDS_CHECKED}}> 秒</label>
        <label><input type="radio" name="imode" value="multiple" {{MULTIPLE_CHECKED}}> 时长倍数</label>
        <input type="number" id="interval" min="0" step="0.1" value="{{INTERVAL}}">
      </span>
      <span class="sep">|</span>
      <label><input type="checkbox" id="autonext"> 连播</label>
      <span class="sep">|</span>
      <span class="grp">速度
        <select id="rate">
          <option value="0.5">0.5x</option>
          <option value="0.75">0.75x</option>
          <option value="1" selected>1.0x</option>
          <option value="1.25">1.25x</option>
          <option value="1.5">1.5x</option>
          <option value="1.75">1.75x</option>
          <option value="2">2.0x</option>
        </select>
      </span>
    </div>
  </section>
</main>

<script type="application/json" id="data">{{DATA}}</script>
<script>
(function () {
  var PLAYLIST = JSON.parse(document.getElementById("data").textContent);
  var audio = new Audio();
  var current = 0;
  var playedTimes = 0;      // 当前跟读循环里已播放次数
  var shadowTimer = null;
  var playbackRate = 1;

  var wordEl = document.getElementById("word");
  var meaningEl = document.getElementById("meaning");
  var playBtn = document.getElementById("play");
  var curEl = document.getElementById("cur");
  var durEl = document.getElementById("dur");
  var fillEl = document.getElementById("progress-fill");
  var barEl = document.getElementById("bar");
  var listEl = document.getElementById("playlist");
  var metaEl = document.getElementById("meta");

  function fmt(t) {
    if (!isFinite(t) || t < 0) t = 0;
    var m = Math.floor(t / 60), s = Math.floor(t % 60);
    return (m < 10 ? "0" + m : m) + ":" + (s < 10 ? "0" + s : s);
  }

  function clearTimer() {
    if (shadowTimer) { clearTimeout(shadowTimer); shadowTimer = null; }
  }

  function setPlayingUI(playing) {
    playBtn.textContent = playing ? "暂停" : "播放";
  }

  function renderList() {
    listEl.innerHTML = "";
    PLAYLIST.forEach(function (item, i) {
      var li = document.createElement("li");
      var w = document.createElement("div");
      w.className = "w";
      w.textContent = item.word;
      var m = document.createElement("div");
      m.className = "m";
      m.textContent = item.meaning || "";
      li.appendChild(w);
      li.appendChild(m);
      li.addEventListener("click", function () { current = i; playCurrent(); });
      if (i === current) li.className = "active";
      listEl.appendChild(li);
    });
    metaEl.textContent = "共 " + PLAYLIST.length + " 条 · 第 " + (PLAYLIST.length ? (current + 1) : 0) + " 条";
  }

  function showCurrent() {
    var item = PLAYLIST[current] || { word: "—", meaning: "" };
    wordEl.textContent = item.word || "—";
    meaningEl.textContent = item.meaning || "";
    renderList();
  }

  function playCurrent() {
    if (!PLAYLIST.length) return;
    clearTimer();
    var item = PLAYLIST[current];
    playedTimes = 1;
    showCurrent();
    audio.src = item.audio;
    audio.playbackRate = playbackRate;
    audio.currentTime = 0;
    audio.play().catch(function () {});
    setPlayingUI(true);
  }

  function repeatGapMs() {
    var mode = document.querySelector('input[name="imode"]:checked').value;
    var val = parseFloat(document.getElementById("interval").value);
    if (isNaN(val) || val < 0) val = 0;
    if (mode === "seconds") return val * 1000;
    // 时长倍数
    var d = audio.duration;
    if (!isFinite(d) || d <= 0) d = 0;
    return d * val * 1000;
  }

  audio.addEventListener("timeupdate", function () {
    var d = audio.duration || 0;
    fillEl.style.width = (d > 0 ? (audio.currentTime / d) * 100 : 0) + "%";
    curEl.textContent = fmt(audio.currentTime);
    durEl.textContent = fmt(d);
  });

  audio.addEventListener("ended", function () {
    var shadowOn = document.getElementById("shadow-on").checked;
    var repeat = parseInt(document.getElementById("repeat").value, 10);
    if (isNaN(repeat) || repeat < 1) repeat = 1;

    if (shadowOn && playedTimes < repeat) {
      var gap = repeatGapMs();
      shadowTimer = setTimeout(function () {
        playedTimes++;
        audio.currentTime = 0;
        audio.play().catch(function () {});
      }, gap);
      return;
    }

    setPlayingUI(false);
    var autonext = document.getElementById("autonext").checked;
    if (autonext && current < PLAYLIST.length - 1) {
      current++;
      playCurrent();
    }
  });

  playBtn.addEventListener("click", function () {
    if (!PLAYLIST.length) return;
    if (audio.paused) {
      if (audio.src && audio.currentTime > 0 && !audio.ended) {
        audio.play().catch(function () {});
      } else {
        playCurrent();
      }
      setPlayingUI(true);
    } else {
      audio.pause();
      setPlayingUI(false);
    }
  });

  document.getElementById("prev").addEventListener("click", function () {
    if (!PLAYLIST.length) return;
    current = (current - 1 + PLAYLIST.length) % PLAYLIST.length;
    playCurrent();
  });
  document.getElementById("next").addEventListener("click", function () {
    if (!PLAYLIST.length) return;
    current = (current + 1) % PLAYLIST.length;
    playCurrent();
  });

  barEl.addEventListener("click", function (e) {
    var rect = barEl.getBoundingClientRect();
    var ratio = (e.clientX - rect.left) / rect.width;
    if (!isFinite(audio.duration) || !audio.duration) return;
    audio.currentTime = Math.max(0, Math.min(1, ratio)) * audio.duration;
  });

  document.getElementById("rate").addEventListener("change", function (e) {
    var v = parseFloat(e.target.value);
    playbackRate = isNaN(v) ? 1 : v;
    audio.playbackRate = playbackRate;
  });

  showCurrent();
})();
</script>
</body>
</html>
"""


def render_player_html(items, title="ZeroListen 播放器", config=None):
    """items: list[dict], 每项 {"word": str, "meaning": str, "audio": str(相对路径)}
    config: 跟读默认设置 dict, 键 repeat_count / interval_mode / interval_value。
    返回完整 HTML 字符串。
    """
    config = config or {}
    repeat = int(config.get("repeat_count", 2) or 2)
    repeat = max(1, min(10, repeat))
    interval_mode = config.get("interval_mode", "seconds")
    if interval_mode not in ("seconds", "multiple"):
        interval_mode = "seconds"
    interval_value = float(config.get("interval_value", 1.5) or 0)
    if interval_value < 0:
        interval_value = 0

    data_json = json.dumps(items, ensure_ascii=False)
    data_json = data_json.replace("</", "<\\/")

    html = _TEMPLATE
    html = html.replace("{{TITLE}}", _escape(title))
    html = html.replace("{{DATA}}", data_json)
    html = html.replace("{{REPEAT}}", str(repeat))
    html = html.replace("{{INTERVAL}}", _num(interval_value))
    html = html.replace("{{SECONDS_CHECKED}}", "checked" if interval_mode == "seconds" else "")
    html = html.replace("{{MULTIPLE_CHECKED}}", "checked" if interval_mode == "multiple" else "")
    return html


def _num(v):
    """输出稳定的数字字符串(避免浮点尾巴)。"""
    if float(v).is_integer():
        return str(int(v))
    return ("%.2f" % v).rstrip("0").rstrip(".")


def _escape(s):
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
