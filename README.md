# 🎮 Don't Touch My Area (Territory Conquest)

> **2D Cyberpunk Neon Territory Conquest Game built with Python Turtle Graphics**  
> *Game Jam Workshop 2026*

---

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
│   ├── bg.gif             # ภาพพื้นหลัง 600x600 px ของหน้าต่างเกม
│   └── sounds/            # ไฟล์เสียงเอฟเฟกต์ 8-bit .wav
│       ├── click.wav      # เสียงกดปุ่มเมนู / นับถอยหลัง 5 วินาที
│       ├── claim.wav      # เสียงยึดครองพื้นที่สำเร็จ
│       ├── hit.wav        # เสียงชนหาง / ชนประสานงา
│       ├── win.wav        # เสียงชัยชนะ (Fanfare)
│       └── game_over.wav  # เสียงจบเกมเสมอ / พ่ายแพ้
├── dont_touch_my_area.py  # โค้ดเกมหลัก (Logic, Rendering, SFX, Loop)
├── generate_sfx.py        # สคริปต์สังเคราะห์เสียง 8-bit ด้วย Python wave/struct
└── README.md              # เอกสารประกอบโปรเจกต์
```

---

## 🚀 วิธีติดตั้งและเริ่มเล่น (Getting Started)

### ข้อกำหนดระบบ (Requirements)
- **Python 3.8+** (รองรับ Standard Library โดยตรง ไม่จำเป็นต้อง `pip install` ไลบรารีภายนอก)
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

