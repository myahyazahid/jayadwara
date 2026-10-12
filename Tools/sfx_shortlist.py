"""Shortlist kandidat SFX Episode 1 (docs/18 bagian E) — Python sistem, bukan Python UE.

Sumber hanya yang boleh dipakai komersial tanpa syarat: Kenney (CC0) dan Freesound berlisensi CC0.
Untuk tiap slot: cari, download, ukur (durasi, peak, RMS, porsi bass < 150 Hz, centroid), pilih 3 kandidat,
convert ke WAV 48 kHz 16-bit -> Audio/Kandidat/<NN_slot>/, lalu tulis Audio/KANDIDAT.md + Audio/kandidat.json.

Freesound diambil dari preview HQ (MP3 ±128 kbps, tanpa login). Untuk aset final, download file asli
(perlu akun Freesound) dari link di KANDIDAT.md. Lisensi tetap CC0.

Pakai:
  python3 Tools/sfx_shortlist.py --kenney <folder zip Kenney yang sudah diekstrak> --cache <folder cache>
  (pack Kenney: ui-audio, impact-sounds, interface-sounds, rpg-audio dari kenney.nl/assets)
Butuh: ffmpeg di PATH, numpy.
"""
import argparse
import glob
import html
import json
import math
import os
import re
import shutil
import subprocess
import time
import urllib.parse
import urllib.request

import numpy as np

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
OUT = os.path.join(REPO, "Audio", "Kandidat")
SR = 48000
PER_SLOT = 3

# kind: "oneshot" (dipakai apa adanya) | "loop" (ambien/musik, dipotong LOOP_MAX detik untuk audisi)
LOOP_MAX = 30.0

# kenney: daftar pola glob; satu pola = satu kandidat (semua variasinya, untuk Sound Cue Random)
# fs: daftar query Freesound; dur = rentang durasi (detik); kw = kata yang diharapkan di judul/tag; neg = kata yang ditolak
# bass: bobot porsi bass dalam skor (slot "berat" > 0)
SLOTS = [
    # --- Combat (manusia & raksasa memakai pukulan yang sama, raksasa di-pitch turun di Sound Cue)
    dict(id="01_pukulan_ringan", ue="S_Combat_Punch_Light", grp="Combat", desc="Pukulan ringan (combo)",
         kenney=["impactPunch_medium_*"], fs=["punch light hit", "punch hit", "fist punch"], dur=(0.05, 1.5), kw=["punch", "hit", "slap"],
         neg=["bell", "metal", "glass"], bass=0.0),
    dict(id="02_pukulan_berat", ue="S_Combat_Punch_Heavy", grp="Combat", desc="Pukulan berat / finisher",
         kenney=["impactPunch_heavy_*"], fs=["heavy punch impact body", "punch heavy", "body hit punch"], dur=(0.1, 2.5), kw=["punch", "impact", "hit"],
         neg=["bell", "glass"], bass=0.5),
    dict(id="03_tangkis", ue="S_Combat_Block", grp="Combat", desc="Tangkis (block) lengan",
         kenney=["impactSoft_heavy_*"], fs=["block arm hand hit", "martial arts block", "punch block", "kung fu hit"], dur=(0.05, 1.5),
         kw=["block", "arm", "hand", "hit"], neg=["sword", "metal", "glass"], bass=0.0),
    dict(id="04_parry", ue="S_Combat_Parry", grp="Combat", desc="Parry sukses (aksen terang, tangan kosong)",
         kenney=[], fs=["parry", "impact whoosh hit"], dur=(0.1, 2.0), kw=["parry", "impact", "hit", "whoosh"],
         neg=["sword", "gun"], bass=0.0),
    dict(id="05_dodge", ue="S_Combat_Dodge", grp="Combat", desc="Dodge / menghindar (whoosh + kain)",
         kenney=["cloth[0-9]*"], fs=["whoosh swoosh"], dur=(0.1, 1.5), kw=["whoosh", "swoosh", "swish"],
         neg=["sword", "fire"], bass=0.0),
    dict(id="06_tulang_patah", ue="S_Enemy_Bone_Break", grp="Enemy", desc="Tulang patah (minion & Jerangkong)",
         kenney=[], fs=["bone break crack", "bone crunch"], dur=(0.1, 3.0), kw=["bone", "break", "crack", "crunch", "snap"],
         neg=["punch", "head"], bass=0.0),
    dict(id="07_tulang_merayap", ue="S_Enemy_Bone_Crawl", grp="Enemy", desc="Tulang merayap / menyusun ulang",
         kenney=[], fs=["bones rattle", "skeleton bones"], dur=(0.5, 8.0), kw=["bone", "rattle", "skeleton"],
         neg=["dice"], bass=0.0),
    dict(id="08_langkah_aksa", ue="S_Aksa_Footstep", grp="Aksa", desc="Langkah Aksa (tanah/batu situs penggalian)",
         kenney=["footstep_grass_*", "footstep_concrete_*", "footstep0*"], fs=[], dur=(0.05, 1.0), kw=[], neg=[], bass=0.0),
    # --- Raksasa
    dict(id="09_langkah_raksasa", ue="S_Giant_Footstep", grp="Giant", desc="Langkah raksasa (lapisan dasar boom)",
         kenney=[], fs=["giant footstep", "huge impact boom", "earth impact heavy"], dur=(0.5, 6.0),
         kw=["giant", "footstep", "impact", "boom", "stomp", "thud"], neg=["gun", "laser"], bass=1.5),
    dict(id="10_gedung_runtuh", ue="S_Giant_Building_Collapse", grp="Giant", desc="Gedung runtuh",
         kenney=[], fs=["building collapse", "demolition collapse"], dur=(2.0, 20.0),
         kw=["collapse", "building", "demolition", "crumble"], neg=["paper"], bass=1.0),
    dict(id="11_debris", ue="S_Giant_Debris", grp="Giant", desc="Debris / puing berjatuhan",
         kenney=[], fs=["rubble debris falling", "rocks falling"], dur=(1.0, 10.0),
         kw=["debris", "rubble", "rock", "falling", "stones"], neg=["water"], bass=0.5),
    dict(id="12_gema_kota", ue="S_Giant_City_Echo", grp="Giant", desc="Gema kota / dentuman jauh",
         kenney=[], fs=["distant explosion", "distant boom thunder"], dur=(1.0, 12.0),
         kw=["distant", "boom", "explosion", "rumble"], neg=["gun", "firework"], bass=1.0),
    dict(id="13_raungan_jerangkong", ue="S_Boss_Jerangkong_Roar", grp="Boss", desc="Raungan Jerangkong (bahan, di-pitch/layer)",
         kenney=[], fs=["monster roar", "creature growl"], dur=(0.5, 6.0), kw=["monster", "roar", "growl", "creature"],
         neg=["dog", "lion", "tiger", "car"], bass=0.5),
    # --- UI & scanner
    dict(id="14_scan", ue="S_UI_Scan", grp="UI", desc="Scanner aktif",
         kenney=["glitch_*"], fs=["scanner scan sci-fi"], dur=(0.2, 4.0), kw=["scan", "scanner"], neg=[], bass=0.0),
    dict(id="15_clue_ditemukan", ue="S_UI_Clue_Found", grp="UI", desc="Clue ditemukan",
         kenney=["confirmation_*", "question_*"], fs=["discovery chime", "success chime notification"], dur=(0.2, 3.0),
         kw=["discover", "chime", "found", "success"],
         neg=[], bass=0.0),
    dict(id="16_koms_masuk", ue="S_UI_Koms_In", grp="UI", desc="KOMS masuk (Sekar di telinga)",
         kenney=["bong_*", "open_*"], fs=["radio beep transmission"], dur=(0.1, 2.0), kw=["radio", "beep", "transmission"],
         neg=[], bass=0.0),
    dict(id="17_menu_pilih", ue="S_UI_Menu_Select", grp="UI", desc="Menu: pindah/pilih",
         kenney=["select_*", "click_*", "switch*"], fs=[], dur=(0.0, 1.0), kw=[], neg=[], bass=0.0),
    dict(id="18_menu_kembali", ue="S_UI_Menu_Back", grp="UI", desc="Menu: kembali/tutup",
         kenney=["back_*", "close_*", "minimize_*"], fs=[], dur=(0.0, 1.0), kw=[], neg=[], bass=0.0),
    # --- Ambien & suasana (loop)
    dict(id="19_angin_bukit", ue="S_Amb_Wind_Hill", grp="Ambient", desc="Angin bukit", kind="loop",
         kenney=[], fs=["wind grass field", "wind mountain"], dur=(10, 600), kw=["wind"], neg=["chime", "microphone", "traffic", "car", "road", "bus", "voice", "machine", "rain"], bass=0.0),
    dict(id="20_serangga_senja", ue="S_Amb_Insects_Dusk", grp="Ambient", desc="Serangga senja (jangkrik/tonggeret)", kind="loop",
         kenney=[], fs=["crickets evening", "cicada tropical"], dur=(10, 600), kw=["cricket", "insect", "cicada", "evening"],
         neg=[], bass=0.0),
    dict(id="21_desa", ue="S_Amb_Village", grp="Ambient", desc="Suasana desa (Jawa/Indonesia kalau ada)", kind="loop",
         kenney=[], fs=["indonesia village", "java village", "village ambience rooster"], dur=(10, 600),
         kw=["village", "indonesia", "java", "bali", "rural"], neg=["prayer", "adhan", "azan", "church", "traffic"], bass=0.0),
    dict(id="22_sang_penjaga", ue="S_VO_Penjaga_Drone", grp="Story", desc="Efek suara rendah Sang Penjaga (drone)", kind="loop",
         kenney=[], fs=["low drone dark", "deep rumble drone"], dur=(3, 120), kw=["drone", "low", "deep", "dark"],
         neg=[], bass=1.0),
    dict(id="23_gamelan", ue="S_Mus_Gamelan_Placeholder", grp="Music", desc="Gamelan (placeholder musik/wayang)", kind="loop",
         kenney=[], fs=["gamelan", "gamelan java"], dur=(5, 600), kw=["gamelan", "java", "bali", "gong"], neg=[], bass=0.0),
]

UA = {"User-Agent": "jayadwara-sfx-shortlist/1.0 (+https://github.com/myahyazahid/jayadwara)"}


def http_get(url, dest=None):
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            if dest:
                with open(dest, "wb") as f:
                    f.write(data)
            return data
        except Exception as e:  # noqa: BLE001 — jaringan; coba ulang dengan jeda
            if attempt == 3:
                raise
            print(f"  ulang ({e}) ...")
            time.sleep(2 ** (attempt + 1))


def fs_search(query, dur, sort=None):
    params = {"q": query, "f": f'license:"Creative Commons 0" duration:[{dur[0]} TO {dur[1]}]'}
    if sort:
        params["s"] = sort
    page = http_get("https://freesound.org/search/?" + urllib.parse.urlencode(params)).decode("utf-8", "replace")
    out = []
    starts = [m.start() for m in re.finditer(r'class="bw-player"', page)]
    for i, s in enumerate(starts):
        chunk = page[s: starts[i + 1] if i + 1 < len(starts) else len(page)]

        def attr(name):
            m = re.search(rf'data-{name}="([^"]*)"', chunk)
            return html.unescape(m.group(1)) if m else ""

        lic = re.search(r'title="License: ([^"]+)"', chunk)
        sid = attr("sound-id")
        if not sid or not lic or lic.group(1) != "Creative Commons 0":
            continue
        out.append(dict(src="freesound", id=sid, user=attr("username"), title=attr("title"),
                        duration=float(attr("duration") or 0), downloads=int(attr("num-downloads") or 0),
                        tags=sorted(set(re.findall(r'href="/browse/tags/([^/"]+)/"', chunk))),
                        preview=attr("mp3").replace("-lq.mp3", "-hq.mp3"),
                        url=f"https://freesound.org/people/{attr('username')}/sounds/{sid}/", license="CC0 1.0"))
    return out


def decode(path, max_sec=None):
    cmd = ["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR)]
    if max_sec:
        cmd += ["-t", str(max_sec)]
    raw = subprocess.run(cmd + ["-f", "f32le", "-"], check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32)


def measure(path, max_sec=None):
    x = decode(path, max_sec)
    if x.size == 0:
        return None
    peak = float(np.max(np.abs(x)))
    rms = float(np.sqrt(np.mean(x.astype(np.float64) ** 2)))
    spec = np.abs(np.fft.rfft(x[: SR * 30])) ** 2
    freqs = np.fft.rfftfreq(min(x.size, SR * 30), 1 / SR)
    tot = float(spec.sum()) or 1.0
    db = lambda v: round(20 * math.log10(max(v, 1e-9)), 1)  # noqa: E731
    return dict(dur=round(x.size / SR, 2), peak_db=db(peak), rms_db=db(rms),
                bass=round(float(spec[freqs < 150].sum()) / tot, 3),
                centroid=int(float((spec * freqs).sum()) / tot))


def to_wav(src, dst, loop):
    """WAV 48 kHz 16-bit. Peak > -1 dBFS (sering pada decode MP3) diturunkan ke -1 dBFS supaya tidak clipping."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-f", "f32le", "-"], check=True, capture_output=True).stdout
    peak = float(np.max(np.abs(np.frombuffer(raw, dtype=np.float32)))) if raw else 0.0
    gain = min(0.0, -1.0 - 20 * math.log10(max(peak, 1e-9)))
    af = [f"volume={gain:.2f}dB"]
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", src, "-ar", str(SR), "-c:a", "pcm_s16le"]
    if loop:
        cmd += ["-t", str(LOOP_MAX)]
        af.append(f"afade=t=out:st={LOOP_MAX - 2}:d=2")
    subprocess.run(cmd + ["-af", ",".join(af), dst], check=True)


def kenney_candidates(slot, kenney_root):
    cands = []
    for pat in slot["kenney"]:
        files = sorted(f for f in glob.glob(os.path.join(kenney_root, "**", "Audio", pat), recursive=True)
                       if f.endswith(".ogg"))
        if files:
            pack = os.path.relpath(files[0], kenney_root).split(os.sep)[0].replace("x_", "")
            cands.append(dict(src="kenney", id=re.sub(r"[^A-Za-z]", "", pat), pack=pack, files=files[:5], title=re.sub(r"[^A-Za-z_]", "", pat).strip("_"),
                              url=f"https://kenney.nl/assets/{pack}", license="CC0 1.0", user="Kenney"))
    return cands


def score(c, slot, rel_rank):
    text = (c["title"] + " " + " ".join(c.get("tags", []))).lower()
    if any(n in text for n in slot["neg"]):
        return -99
    s = 1.0 / (1 + rel_rank) + 0.15 * math.log10(c.get("downloads", 0) + 1)
    s += 0.3 * sum(k in text for k in slot["kw"][:3])
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kenney", required=True)
    ap.add_argument("--cache", required=True)
    ap.add_argument("--only", nargs="*", help="id slot tertentu saja")
    a = ap.parse_args()
    os.makedirs(a.cache, exist_ok=True)
    report = []
    used = set()
    for slot in SLOTS:
        if a.only and slot["id"] not in a.only:
            continue
        loop = slot.get("kind") == "loop"
        print(f"== {slot['id']}")
        picks = kenney_candidates(slot, a.kenney)[:PER_SLOT]
        for p in picks:
            p["metrics"] = [measure(f) for f in p["files"]]
        need = PER_SLOT - len(picks)
        if need > 0 and slot["fs"]:
            pool = {}
            for q in slot["fs"]:
                for sort in (None, "Downloads (most first)"):
                    for rank, c in enumerate(fs_search(q, slot["dur"], sort)[:15]):
                        if c["id"] in used:
                            continue
                        r = rank if sort is None else rank + 3          # relevansi sedikit lebih dipercaya
                        if c["id"] not in pool or r < pool[c["id"]][1]:
                            pool[c["id"]] = (c, r)
                    time.sleep(1)
            ranked = sorted(((score(c, slot, r), c) for c, r in pool.values()), key=lambda t: -t[0])
            ranked = [c for s, c in ranked if s > -50][: need * 3]
            measured = []
            for c in ranked:
                mp3 = os.path.join(a.cache, f"fs{c['id']}.mp3")
                if not os.path.exists(mp3):
                    http_get(c["preview"], mp3)
                m = measure(mp3, LOOP_MAX if loop else None)
                if not m or m["peak_db"] < -40:
                    continue
                c["metrics"] = [m]
                c["files"] = [mp3]
                measured.append(c)
            # skor akhir: urutan awal + bobot bass untuk slot "berat"
            measured.sort(key=lambda c: -(score(c, slot, ranked.index(c)) + slot["bass"] * c["metrics"][0]["bass"]))
            picks += measured[:need]
        # tulis WAV
        sdir = os.path.join(OUT, slot["id"])
        if os.path.isdir(sdir):
            shutil.rmtree(sdir)
        os.makedirs(sdir)
        for i, p in enumerate(picks, 1):
            p["out"] = []
            for j, f in enumerate(p["files"]):
                if p["src"] == "kenney":
                    name = f"k{i}_kenney_{os.path.splitext(os.path.basename(f))[0]}.wav"
                else:
                    slug = re.sub(r"[^a-z0-9]+", "-", p["title"].lower()).strip("-")[:40]
                    name = f"k{i}_fs{p['id']}_{slug}.wav"
                to_wav(f, os.path.join(sdir, name), loop)
                p["out"].append(os.path.relpath(os.path.join(sdir, name), REPO).replace(os.sep, "/"))
            if p["src"] == "freesound":
                used.add(p["id"])
            print(f"  k{i}: {p['src']} {p['title']} {p['metrics'][0]}")
        report.append(dict(slot={k: slot[k] for k in ("id", "ue", "grp", "desc")} | {"kind": slot.get("kind", "oneshot")},
                           picks=[{k: v for k, v in p.items() if k not in ("files", "preview")} for p in picks]))
    path = os.path.join(REPO, "Audio", "kandidat.json")
    if a.only and os.path.exists(path):                                  # --only: gabung dengan hasil slot lain
        with open(path, encoding="utf-8") as f:
            old = {r["slot"]["id"]: r for r in json.load(f)}
        old.update({r["slot"]["id"]: r for r in report})
        report = [old[k] for k in sorted(old)]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=1, ensure_ascii=False)
    write_md(report)


def write_md(report):
    L = ["# Kandidat SFX Episode 1", "",
         "Hasil `Tools/sfx_shortlist.py`. Semua **CC0** (boleh komersial, tanpa wajib kredit). "
         "Dengarkan `k1`–`k3` per slot, pilih satu, lalu catat di kolom **Pilih** (atau bilang ke Claude).", "",
         "- Kenney: satu kandidat = satu set variasi (pakai semua di Sound Cue *Random*).",
         "- Freesound: dari preview HQ (MP3 ±128 kbps). Untuk final, download file asli lewat link (perlu login).",
         f"- Ambien/musik dipotong {int(LOOP_MAX)} detik + fade out, hanya untuk audisi.",
         "- Kolom ukur (file sumber, kanal digabung): durasi · peak dBFS · RMS dBFS · **bass** = porsi energi < 150 Hz · "
         "centroid (Hz, makin tinggi makin terang). WAV hasil sudah dibatasi peak -1 dBFS.",
         ""]
    grp = None
    for r in report:
        s = r["slot"]
        if s["grp"] != grp:
            grp = s["grp"]
            L += [f"## {grp}", ""]
        L += [f"### {s['id']} — {s['desc']}", f"Nama aset UE: `{s['ue']}` · Pilih: ☐ k1 ☐ k2 ☐ k3", "",
              "| | Sumber | Judul | Ukur | File |", "|---|---|---|---|---|"]
        for i, p in enumerate(r["picks"], 1):
            m = p["metrics"][0]
            meas = f"{m['dur']} s · {m['peak_db']} / {m['rms_db']} dB · bass {m['bass']} · {m['centroid']} Hz"
            src = (f"[Kenney {p['pack']}]({p['url']})" if p["src"] == "kenney"
                   else f"[Freesound #{p['id']}]({p['url']}) oleh {p['user']}")
            files = f"{len(p['out'])} variasi" if len(p["out"]) > 1 else os.path.basename(p["out"][0])
            title = p["title"].replace("|", "/")
            L.append(f"| k{i} | {src} | {title} | {meas} | `{files}` |")
        if not r["picks"]:
            L.append("| – | (tidak ada kandidat CC0 yang lolos) | | | |")
        L.append("")
    with open(os.path.join(REPO, "Audio", "KANDIDAT.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L))


if __name__ == "__main__":
    main()
