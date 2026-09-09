# 🎮 Don't Touch My Area (Territory Conquest)

> **2D Cyberpunk Neon Territory Conquest Game built with Python Turtle Graphics**  
> *Game Jam Workshop 2026*

[ 🇹🇭 ภาษาไทย ](#-ภาษาไทย) &nbsp;|&nbsp; [ 🇯🇵 日本語 ](#-日本語)

---

<a name="-ภาษาไทย"></a>
# 🇹🇭 ภาษาไทย

## 🌟 จุดเด่นของเกม (Features)

- **Neon Cyberpunk Aesthetic:** ตัวละครแบบ Dual-Layer Glow Aura (แกนพลังงานสีขาวสว่างพร้อมออร่าเรืองแสง), หางนีออนสดใส และภาพพื้นหลังธีมเรโทรอวกาศ (`asset/bg.gif`)
- **8-Bit Retro Sound Effects:** ระบบเสียงสังเคราะห์สไตล์ 8-bit ครบวงจร (`click`, `claim`, `hit`, `win`, `game_over`) เล่นแบบ Asynchronous ไม่หน่วงเฟรมเรต
- **High-Performance BFS Flood Fill & Scanline Rendering:** อัลกอริทึม BFS ด้วย `bytearray` ร่วมกับการสแตมป์แบบ Horizontal Scanline ทำให้สามารถยึดพื้นที่หลักพันช่องได้ภายในเวลา < 3 ms
- **Competitive 2-Player Local Battle:** รองรับผู้เล่น 2 คนในหน้าจอเดียวกัน พร้อมระบบเลือกระยะเวลาการแข่งขัน (10s, 30s, 60s) และระบบนับคะแนน/สัดส่วนเปอร์เซ็นต์แบบ Real-Time

---

## 🕹️ การควบคุม (Controls)

| ผู้เล่น | การควบคุม | สีประจำตัว (Neon Theme) |
| :--- | :--- | :--- |
| **Player 1** | `W` (ขึ้น), `S` (ลง), `A` (ซ้าย), `D` (ขวา) | **Neon Pink / Magenta** (`#ff007f`) |
| **Player 2** | `↑` (ขึ้น), `↓` (ลง), `←` (ซ้าย), `→` (ขวา) | **Neon Cyan / Electric Blue** (`#00f0ff`) |

---

## ⚔️ กติกาและกลไกของเกม (Gameplay Rules)

1. **การยึดพื้นที่ (Conquest):**
   - ผู้เล่นเริ่มจากฐานของตัวเอง เมื่อเคลื่อนที่ออกจากฐานจะสร้าง **"เส้นหาง (Trail)"**
   - เมื่อลากเส้นวนกลับเข้ามาบรรจบกับพื้นที่เดิมของตนเอง พื้นที่ทั้งหมดที่ถูกปิดล้อมจะถูกยึดเป็น **"อาณาเขตถาวร (Permanent Territory)"** ทันที
2. **การตัดหาง (Tail Cut - ชนหาง):**
   - ในระหว่างที่ฝ่ายตรงข้ามกำลังลากหางอยู่ หากเราวิ่งชนหางของเขา หางของเขาจะขาดหายไปทันที
   - ในโหมด **ELIMINATION**: ฝ่ายที่ถูกตัดหางจะแพ้ทันที และฝ่ายที่ตัดหางชนะ!
   - ในโหมด **RESPAWN**: หางที่ถูกตัดจะสลายไป และผู้เล่นจะถูกส่งกลับไปเกิดใหม่ที่ฐาน
3. **การชนกัน (Collisions):**
   - **ชนประสานงา (Head-on Collision):** ชนหน้ากันตรงๆ หางจะหายทั้งคู่ และผลการแข่งเสมอกัน (Draw)
   - **ตัดหางพร้อมกัน (Mutual Tail Cut):** หางขาดทั้งคู่ และผลการแข่งเสมอกัน (Draw)
4. **หมดเวลาการแข่งขัน (Time Up):**
   - เมื่อเวลานับถอยหลังหมดลง ระบบจะรวมคะแนนจำนวนช่องพื้นที่ที่ยึดได้ ฝ่ายที่ครอบครองพื้นที่มากที่สุดจะเป็นผู้ชนะ

---

## 📁 โครงสร้างโปรเจกต์ (Project Structure)

```text
Starter Kit/
├── asset/
│   ├── bg.gif                            # ภาพพื้นหลัง 600x600 px ของหน้าต่างเกม
│   └── sounds/                           # ไฟล์เสียงเอฟเฟกต์ 8-bit .wav
│       ├── click.wav                     # เสียงกดปุ่มเมนู / นับถอยหลัง 5 วินาที
│       ├── claim.wav                     # เสียงยึดครองพื้นที่สำเร็จ
│       ├── hit.wav                       # เสียงชนหาง / ชนประสานงา
│       ├── win.wav                       # เสียงชัยชนะ (Fanfare)
│       └── game_over.wav                 # เสียงจบเกมเสมอ / พ่ายแพ้
├── dont_touch_my_area.py                 # โค้ดเกมหลัก (Logic, Rendering, SFX, Loop)
├── [thai_docs]dont_touch_my_area.pdf     # เอกสารคู่มืออธิบายโค้ดฉบับภาษาไทย (.pdf)
├── [japanese_docs]dont_touch_my_area.pdf # เอกสารคู่มืออธิบายโค้ดฉบับภาษาญี่ปุ่น (.pdf)
└── README.md                             # เอกสารประกอบโปรเจกต์
```

---

## 🚀 วิธีติดตั้งและเริ่มเล่น (Getting Started)

### ข้อกำหนดระบบ (Requirements)
- **Python 3.8+** (ใช้เฉพาะ Standard Library ไม่จำเป็นต้อง `pip install` ไลบรารีภายนอก)
- ระบบปฏิบัติการ: Windows (รองรับระบบเสียง `winsound` ในตัว)

### วิธีรันเกม (Run the Game)
เปิด Terminal หรือ Command Prompt ในโฟลเดอร์โปรเจกต์ แล้วสั่งรัน:

```bash
python dont_touch_my_area.py
```

---

## 🧠 อัลกอริทึมและเทคนิคเชิงลึก (Core Architecture)

### 1. BFS Exterior Flood Fill
เพื่อตรวจสอบพื้นที่ที่ถูกปิดล้อม ระบบจะไม่คำนวณจากข้างใน แต่ใช้วิธี **Flood Fill พื้นที่ว่างภายนอก** จากขอบจอทั้ง 4 ด้าน:
- ช่องใดที่ไม่สามารถเข้าถึงได้จากการ Fill ขอบจอ = **ช่องที่ถูกปิดล้อมอยู่ข้างใน**
- แปลงช่องเหล่านั้นรวมถึงเส้น Trail ให้กลายเป็นอาณาเขตถาวรของผู้เล่น

### 2. Horizontal Scanline Strip Rendering
การสแตมป์ Turtle Stamp ทีละช่องบนตาราง $100 \times 100$ (10,000 ช่อง) จะทำให้เกมกระตุก เพื่อแก้ปัญหานี้ เกมได้ใช้เทคนิค:
- จัดกลุ่มช่องที่ติดกันในแต่ละแถวแนวนอน
- ยืดขนาด Turtle Shape ตามความยาวแถว (`shapesize`) แล้วสแตมป์เพียงครั้งเดียวต่อหนึ่งแถบ ทำให้ลดจำนวนการสแตมป์ลงกว่า 90% และคงความเร็วที่ 40+ FPS อย่างสม่ำเสมอ

### 3. Non-blocking Asynchronous Audio
ใช้ `winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)` ทำให้เสียงเอฟเฟกต์ดังขึ้นได้ทันทีโดยไม่หยุดหรือขัดจังหวะ Game Loop ของ Turtle Graphics

---
---

<a name="-日本語"></a>
# 🇯🇵 日本語 (Japanese)

## 🌟 ゲームの特徴 (Features)

- **サイバーパンク・ネオンビジュアル (Neon Cyberpunk Aesthetic):** 2層構造の発光オーラ（Dual-Layer Glow Aura：超高輝度白色コア ＋ ネオン光彩）、鮮やかな移動軌跡、レトロフューチャーな宇宙背景（`asset/bg.gif`）を搭載。
- **8-Bit レトロサウンドエフェクト (8-Bit Retro Sound Effects):** 全5種類の8-bitシンセサウンド（`click`, `claim`, `hit`, `win`, `game_over`）を収録。Windows `winsound` の非同期再生（`SND_ASYNC`）により、描画フレームレートを一切落とさずに再生可能。
- **超高速 BFS 外部フラッドフィル ＆ スキャンライン描画 (High-Performance Engine):** 1次元 `bytearray` による幅優先探索（BFS）と、水平スキャンラインによる連続タイルの帯（Strip）スタンプ合成技術を採用。1,000タイル以上の領域獲得時でも < 3ms で瞬時に描画を完了。
- **白熱の2人ローカル対戦 (Competitive 2-Player Local Battle):** 同一画面で2人のプレイヤーが直接対戦。試合時間選択（10秒／30秒／60秒）およびリアルタイム領土占有率（%）・スコア集計機能を完備。

---

## 🕹️ 操作方法 (Controls)

| プレイヤー | 操作キー | テーマカラー (Neon Theme) |
| :--- | :--- | :--- |
| **Player 1** | `W` (上), `S` (下), `A` (左), `D` (右) | **ネオンピンク (Neon Pink)** (`#ff007f`) |
| **Player 2** | `↑` (上), `↓` (下), `←` (左), `→` (右) | **ネオンシアン (Neon Cyan)** (`#00f0ff`) |

---

## ⚔️ ゲームルール・対戦メカニクス (Gameplay Rules)

1. **領土の獲得 (Conquest):**
   - プレイヤーは自陣（初期 $5 \times 5$ エリア）からスタートします。
   - 陣地の外へ出ると **「軌跡（Trail／尻尾）」** を伸ばしながら移動します。
   - 自身の軌跡を自陣または既存の軌跡へ接続してループを閉じると、**囲まれた内部領域全体が一括で確定領土（Permanent Territory）** に変換されます。
2. **尻尾の切断 (Tail Cut):**
   - 相手プレイヤーが軌跡を伸ばしている最中にその軌跡へ体当たりすると、相手の尻尾が切断されます。
   - **ELIMINATION モード:** 尻尾を切断されたプレイヤーはその場で即座に敗北となり、切断した側の勝利となります！
   - **RESPAWN モード:** 切断された尻尾のみが消滅し、プレイヤーは自陣の初期スポーン地点へ戻されて試合が継続します。
3. **衝突判定 (Collisions):**
   - **正面衝突 (Head-on Collision):** 頭同士が同一マスまたは交差して激突した場合、両者の尻尾が消滅し「引き分け (DRAW)」となります。
   - **同時切断 (Mutual Tail Cut):** 同一フレームで互いの尻尾を切り合った場合、両者の尻尾が消滅し「引き分け (DRAW)」となります。
4. **タイムアップ (Time Up):**
   - 制限時間のカウントダウンが終了した時点で、フィールド上の占有タイル数を自動集計し、より多くの領土を獲得したプレイヤーが勝者となります。

---

## 📁 プロジェクト構成 (Project Structure)

```text
Starter Kit/
├── asset/
│   ├── bg.gif                            # ゲームウィンドウの背景画像 (600x600 px)
│   └── sounds/                           # 8-bit サウンドエフェクト (.wav)
│       ├── click.wav                     # メニュー選択・残り5秒カウントダウン音
│       ├── claim.wav                     # 領土獲得ファンファーレ音
│       ├── hit.wav                       # 尻尾切断・正面激突音
│       ├── win.wav                       # 勝利ファンファーレ音
│       └── game_over.wav                 # 引き分け・決着ジングル音
├── dont_touch_my_area.py                 # ゲームメインソースコード (ロジック, 描画, 音声, ループ)
├── [thai_docs]dont_touch_my_area.pdf     # タイ語版 詳細コード解説書 (全9ページ .pdf)
├── [japanese_docs]dont_touch_my_area.pdf # 日本語版 詳細コード解説書 (全9ページ .pdf)
└── README.md                             # プロジェクト説明書 (本ファイル)
```

---

## 🚀 環境構築と起動方法 (Getting Started)

### 動作要件 (Requirements)
- **Python 3.8 以上** (Python標準ライブラリのみで動作。`pip install` などの外部パッケージ導入は不要)
- OS: **Windows** (標準モジュール `winsound` による非同期音声再生に対応)

### 起動手順 (Run the Game)
プロジェクトフォルダでターミナルまたはコマンドプロンプトを開き、以下を実行します：

```bash
python dont_touch_my_area.py
```

---

## 🧠 コアアーキテクチャ・主要アルゴリズム解説 (Core Architecture)

### 1. BFS 外部フラッドフィル反転アルゴリズム (BFS Exterior Flood Fill Inversion)
囲い込まれた領域を高速かつ正確に抽出するため、内部からではなく **「画面外周の4辺から外部の空き地へ水を流す（Flood Fill）」** 手法を採用しています：
- 外周からの水流探索で到達できなかったマス ＝ **「軌跡の内側に完全に包囲された閉域」**
- 到達不能マスおよび軌跡を一括で自陣領土へ書き換えることで、複雑な形状や凹凸のある島であっても100%確実に確定領域化できます。

### 2. 水平スキャンライン・ストリップ描画 (Horizontal Scanline Strip Rendering)
Turtleモジュールで $100 \times 100$（計10,000マス）のタイルを1マスずつスタンプすると描画負荷が極めて高くなります。これを解決するため：
- 水平（行）方向に連続するタイル群を自動検出・統合
- Turtleの形状（`shapesize`）を帯状に拡大し、**1本の水平ストリップとして1回のみスタンプ**
- スタンプAPI呼び出し回数を95%以上削減し、常時 40+ FPS の滑らかな描画を維持します。

### 3. 非ブロッキング非同期オーディオ (Non-blocking Asynchronous Audio)
`winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)` を採用し、Windowsのバックグラウンドスレッドで効果音を再生。ゲームメインループをミリ秒単位でも停止させません。

---

## 📄 詳細技術ドキュメント (Technical Documentation)

コード内のすべての関数（15関数）、ループ構造、変数・定数、データ構造（`grid`, `visited`, `deque`, `trail_stamps`）、および数理モデルの詳細解説は、プロジェクトルートにあるPDFドキュメントをご参照ください：
- 🇹🇭 **タイ語版解説書:** `[thai_docs]dont_touch_my_area.pdf`
- 🇯🇵 **日本語版解説書:** `[japanese_docs]dont_touch_my_area.pdf`
