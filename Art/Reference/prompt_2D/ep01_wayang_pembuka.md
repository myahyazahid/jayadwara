# Pembuka wayang Ep 1: "Dua Penjaga"

| | |
|---|---|
| **Adegan** | 1 · WAYANG · 1,5 menit, bisa di-skip |
| **Narator** | Ki Sastro sebagai dalang (suara + teks, tidak tampil) |
| **Teknik** | 2D parallax: kelir di belakang, wayang sebagai layer PNG yang digerakkan di UE |
| **Sumber** | [17 adegan 1](../../../docs/17-skenario-arc-1.md#adegan-1--pembuka-wayang-dua-penjaga--wayang), [16 bagian 2.1](../../../docs/16-panduan-arc-1.md#21-struktur-dari-07) |

Aturan umum: [README](README.md).

## Alur gambar (dari skenario)

1. Kelir menyala, blencong di atas, gunungan tertancap di tengah → gunungan dicabut.
2. "Batara Kala menebar makhluk-makhluknya" → wayang makhluk Kala.
3. "Di setiap gerbang, berdiri dua penjaga" → dua wayang Dwarapala berhadapan, gada di tangan.
4. Makhluk Kala menyerbu lalu tersedot ke balik gerbang (wayang gerbang di tengah).
5. "Apa harga yang dibayar para penjaga itu" → gunungan ditancapkan lagi, layar gelap.

Butuh **5 layer**: kelir + blencong, Dwarapala (1 wayang, dicerminkan untuk pasangannya), makhluk Kala, gerbang, gunungan.

## Catatan

- **Dua gaya untuk dibandingkan** (keputusan gaya belum ada):
  - **Gaya A, sisi depan wayang kulit:** tatahan berlubang dan sunggingan warna (merah, emas, hitam, putih), seperti melihat wayang dari sisi dalang. Paling kaya dan paling khas, paling mahal kalau di-commission.
  - **Gaya B, sisi bayangan:** yang terlihat penonton di balik kelir. Siluet hitam/cokelat tembus cahaya hangat dengan pola tatahan sebagai lubang cahaya. Lebih murah, lebih misterius, cocok dengan nada "penjaga yang ambigu".
- Wayang Dwarapala dan makhluk Kala adalah **tokoh fiksi** dengan bentuk wayang (proporsi, tangan bertangkai/cempurit), bukan salinan wayang pakem tertentu. Tetap perlu review budayawan sebelum rilis ([17 cek budaya](../../../docs/17-skenario-arc-1.md#cek-ip--budaya-ep-1)).
- Kalimat "harga yang dibayar para penjaga" adalah foreshadowing Ep 30; **jangan** gambarkan Dwarapala memakan Kala.
- Palet Dwarapala boleh menggemakan Jayadwara (merah, hitam, emas, [14](../../../docs/14-model-sheet-jayadwara.md#3-palet-warna)) supaya pemain merasakan hubungannya.

## Prompt 1: komposisi utuh (acuan mood)

```
A traditional Javanese wayang kulit shadow puppet performance seen on a glowing white cotton screen (kelir), wide cinematic 16:9 frame. A warm oil lamp (blencong) hangs at the top center, casting golden flickering light. On the screen, two identical fierce temple guardian puppets face each other on the left and right, each holding a heavy club, drawn in classic wayang kulit proportions with long thin arms on control rods. Between them, a small stone temple gate, and a swarm of twisted demon puppets being pulled into the gate in a swirl of dark red. A tall leaf-shaped gunungan puppet stands at the bottom center. Dark wooden frame of the screen at the edges, deep black surroundings, atmospheric and mysterious.

Style: hand-crafted wayang kulit, intricate perforated leather carving, painted in deep red, black, white and antique gold. No text, no letters, no people visible, no blue light, no blood.
```

## Prompt 2: layer kelir + blencong

```
An empty traditional Javanese wayang kulit screen (kelir), wide 16:9 frame, front view, perfectly flat and centered. Glowing warm off-white cotton screen with subtle fabric texture and a soft hot spot of light in the upper center from a brass oil lamp (blencong) hanging just in front of the screen at the top. Dark carved wooden frame at the top and bottom edges, a long banana trunk along the bottom edge where puppets are planted. Deep black surroundings.

No puppets, no people, no text, no letters, no blue light.
```

## Prompt 3: layer wayang Dwarapala (gaya A)

```
A single Javanese wayang kulit leather shadow puppet of a fierce temple guardian giant (Dwarapala), shown flat in full side profile facing right, isolated on a plain flat light-gray background, full figure from head to the central control rod. Stocky powerful body in classic wayang proportions, large round bulging eye, curled fangs, thick curly hair rendered as carved swirls, a tall ornate crown, heavy armlets, a patterned cloth wrap at the waist, holding a heavy club (gada) upright in the front hand. Both arms jointed at the shoulder and elbow with thin dark control rods (cempurit) attached to the hands. Intricate perforated leather carving, painted in deep red, black, white and antique gold.

Flat front lighting, no shadow on the background, no text, no letters, no blue, no blood.
```

## Prompt 3b: layer wayang Dwarapala (gaya B)

```
A single Javanese wayang kulit leather shadow puppet of a fierce temple guardian giant (Dwarapala), shown flat in full side profile facing right, isolated on a plain flat light-gray background, full figure from head to the central control rod. Stocky powerful body in classic wayang proportions, large round bulging eye, curled fangs, thick curly hair rendered as carved swirls, a tall ornate crown, heavy armlets, a patterned cloth wrap at the waist, holding a heavy club (gada) upright in the front hand. Both arms jointed at the shoulder and elbow with thin dark control rods (cempurit) attached to the hands. Rendered as the shadow side seen through the screen: a dark warm brown semi-translucent silhouette glowing amber at the edges, the carved perforations showing as tiny points of warm light.

Flat front lighting, no shadow on the background, no text, no letters, no blue, no blood.
```

## Prompt 4: layer makhluk Kala

```
A single Javanese wayang kulit leather shadow puppet of a twisted demon creature of Kala, shown flat in full side profile facing left, isolated on a plain flat light-gray background. A hunched lean demon with a wide grinning fanged mouth, one huge round eye, spiky flame-like hair, long clawed fingers, a thin coiling tail, jointed arms on thin control rods. Intricate perforated leather carving, painted mostly in dark red and black with small gold accents, menacing but not gory.

Flat front lighting, no shadow on the background, no text, no letters, no blue, no blood.
```

## Prompt 5: layer gerbang + gunungan

```
Two separate Javanese wayang kulit leather shadow puppets side by side on a plain flat light-gray background, flat front view, same scale. Left: a small ornate temple gate puppet, a paduraksa gate with a tiered stepped roof and a dark doorway, carved with floral perforations, painted red, black and antique gold. Right: a tall leaf-shaped gunungan (kayon) puppet with a single central control rod, carved with a stylized tree of life, a small gate at its base, and swirling clouds, painted in deep red, gold, black and white.

Flat front lighting, no shadow on the background, no text, no letters, no blue.
```

## Setelah gambar jadi

Simpan di `docs/concept-art/2d/wayang_ep01_<layer>_<A|B>_v01.png`. Bandingkan gaya A dan B di komposisi utuh sebelum memutuskan.
