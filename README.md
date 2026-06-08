# Work Permit System



ระบบใบอนุญาตเข้า-ออกพื้นที่ (Work Permit) สำหรับใช้งานในโรงงาน — รองรับ 3 ภาษา (ไทย / English / 中文)



## Technology



- Python 3.10+

- Flask + Flask-Login + Flask-SQLAlchemy + Flask-WTF (CSRF)

- SQLite (พัฒนา) / PostgreSQL (Production แนะนำ)

- Bootstrap 5 + Jinja2



## โครงสร้างโปรเจค



```

project/

├── app.py

├── config.py            # ตั้งค่าจาก environment

├── i18n.py              # แปล 3 ภาษา

├── factory_data.py      # โซน / ประเภทงาน / แผนก

├── helpers.py

├── models.py

├── utils.py

├── routes/

├── templates/

├── static/css/

├── .env.example

├── requirements.txt

└── README.md

```



## วิธีรัน (Development)



```bash

cd "c:\Users\Chat\Documents\New project 4"

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt

copy .env.example .env

python app.py

```



เปิดเบราว์เซอร์: **http://127.0.0.1:5000**



## เปลี่ยนภาษา



- คลิกปุ่ม **ภาษา** มุมขวาบน (ไทย / English / 中文)

- ระบบจำภาษาใน session และบันทึกใน user profile



## บัญชีทดสอบ



รหัสผ่าน: `password`



| Username    | Role              |

|-------------|-------------------|

| requester1  | ผู้ขอ             |

| specialist1 | Specialist        |

| asst_mgr1   | Assistant Manager |

| dgm1        | DGM               |

| hr1         | HR                |

| security1   | Security Guard    |

| admin1      | Admin             |



## Workflow การอนุมัติ



1. **ผู้ขอ** สร้างและส่งคำขอ

2. **Specialist** → **Assistant Manager** → **DGM** → **HR**

3. ครบทุกขั้น → สถานะ `approved`

4. **Security** บันทึก Check-In / Check-Out (เฉพาะวันที่อยู่ในช่วงอนุญาต)



## Production Deployment



1. คัดลอก `.env.example` เป็น `.env` แล้วตั้งค่า:



```env

SECRET_KEY=<random-64-char-string>

DATABASE_URL=postgresql://user:pass@host/dbname

SEED_DEMO_DATA=false

SHOW_DEMO_ACCOUNTS=false

FLASK_DEBUG=false

FLASK_HOST=0.0.0.0

FACTORY_NAME=Your Factory Name

```



2. รันด้วย WSGI server (แนะนำ):



```bash

pip install gunicorn

gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"

```



3. วาง reverse proxy (Nginx/IIS) + HTTPS ด้านหน้า



## ฟีเจอร์สำหรับโรงงาน



- เลือก **โซนพื้นที่** และ **ประเภทงาน** จากรายการมาตรฐาน

- บังคับกรอก **เบอร์ติดต่อฉุกเฉิน**

- Security กรองเฉพาะใบอนุญาต **ใช้งานได้วันนี้**

- ปุ่ม Check-In/Out ขนาดใหญ่เหมาะกับจุด รปภ.

- **พิมพ์ใบอนุญาต** จากหน้ารายละเอียด

- CSRF protection ทุกฟอร์ม

- Pagination รายการคำขอ



## หมายเหตุ



- ลบ `database.db` แล้วรันใหม่เพื่อ reset ข้อมูล (SQLite)

- แก้ไขโซน/ประเภทงานได้ที่ `factory_data.py` และคำแปลที่ `i18n.py`

