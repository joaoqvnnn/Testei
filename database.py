import aiosqlite
from datetime import datetime, timedelta
from config import DATABASE_PATH
from texts import TEXTS, DEFAULT_BUTTONS

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    username TEXT,
    saldo REAL DEFAULT 0,
    whatsapp TEXT,
    created_at TEXT,
    referred_by INTEGER
);
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT, emoji TEXT DEFAULT '📱',
    active INTEGER DEFAULT 1, position INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER, name TEXT, price REAL,
    description TEXT, stock INTEGER DEFAULT 0,
    sold INTEGER DEFAULT 0, views INTEGER DEFAULT 0,
    active INTEGER DEFAULT 1, position INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS purchases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER, product_id INTEGER, price REAL,
    email TEXT, password TEXT, link TEXT,
    created_at TEXT, expires_at TEXT, active INTEGER DEFAULT 1
);
CREATE TABLE IF NOT EXISTS gifts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE, value REAL, product_id INTEGER,
    used INTEGER DEFAULT 0, used_by INTEGER, used_at TEXT,
    email TEXT, password TEXT, link TEXT
);
CREATE TABLE IF NOT EXISTS pix (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ref TEXT UNIQUE, user_id INTEGER, value REAL,
    type TEXT, status TEXT DEFAULT 'pending',
    code TEXT, product_id INTEGER, qty INTEGER DEFAULT 1,
    created_at TEXT, expires_at TEXT
);
CREATE TABLE IF NOT EXISTS messages (key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE IF NOT EXISTS buttons (key TEXT PRIMARY KEY, label TEXT);
CREATE TABLE IF NOT EXISTS affiliates (
    user_id INTEGER PRIMARY KEY,
    status TEXT DEFAULT 'inactive',
    commission REAL DEFAULT 10,
    total_earned REAL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS abandoned (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER, product_id INTEGER, type TEXT,
    value REAL, created_at TEXT, notified INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER, type TEXT, value REAL, created_at TEXT
);
"""

async def init_db():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.executescript(SCHEMA)
        for k, v in TEXTS.items():
            await db.execute("INSERT OR IGNORE INTO messages(key,value) VALUES(?,?)", (k, v))
        for k, v in DEFAULT_BUTTONS.items():
            await db.execute("INSERT OR IGNORE INTO buttons(key,label) VALUES(?,?)", (k, v))
        cur = await db.execute("SELECT COUNT(*) FROM categories")
        row = await cur.fetchone()
        if row[0] == 0:
            await db.execute("INSERT INTO categories(name,emoji) VALUES('Streamings','🎬')")
            await db.execute("INSERT INTO categories(name,emoji) VALUES('Design','🎨')")
            await db.execute(
                "INSERT INTO products(category_id,name,price,description,stock) VALUES(1,'Canva Pro 1 mês',19.90,'Conta Canva Pro por 30 dias com acesso completo.',10)"
            )
        await db.commit()

# ---------- texts/buttons ----------
async def get_text(key):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cur = await db.execute("SELECT value FROM messages WHERE key=?", (key,))
        row = await cur.fetchone()
        return row[0] if row else TEXTS.get(key, "")

async def set_text(key, value):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("INSERT OR REPLACE INTO messages(key,value) VALUES(?,?)", (key, value))
        await db.commit()

async def get_btn(key):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cur = await db.execute("SELECT label FROM buttons WHERE key=?", (key,))
        row = await cur.fetchone()
        return row[0] if row else DEFAULT_BUTTONS.get(key, "")

async def set_btn(key, label):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("INSERT OR REPLACE INTO buttons(key,label) VALUES(?,?)", (key, label))
        await db.commit()

# ---------- users ----------
async def get_or_create_user(tg_user, referred_by=None):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cur = await db.execute("SELECT * FROM users WHERE id=?", (tg_user.id,))
        row = await cur.fetchone()
        if row:
            return row
        await db.execute(
            "INSERT INTO users(id,name,username,saldo,created_at,referred_by) VALUES(?,?,?,0,?,?)",
            (tg_user.id, tg_user.full_name, tg_user.username or "",
             datetime.utcnow().isoformat(), referred_by)
        )
        await db.commit()
        cur = await db.execute("SELECT * FROM users WHERE id=?", (tg_user.id,))
        return await cur.fetchone()

async def get_user(uid):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cur = await db.execute("SELECT * FROM users WHERE id=?", (uid,))
        return await cur.fetchone()

async def add_saldo(uid, value):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("UPDATE users SET saldo=saldo+? WHERE id=?", (value, uid))
        await db.commit()

async def set_whatsapp(uid, value):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("UPDATE users SET whatsapp=? WHERE id=?", (value, uid))
        await db.commit()

# ---------- categories/products ----------
async def get_categories():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cur = await db.execute("SELECT * FROM categories WHERE active=1 ORDER BY position")
        return await cur.fetchall()

async def get_products_by_cat(cat_id, page=0, per_page=6):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cur = await db.execute(
            "SELECT * FROM products WHERE category_id=? AND active=1 ORDER BY position LIMIT ? OFFSET ?",
            (cat_id, per_page, page*per_page))
        return await cur.fetchall()

async def count_products_by_cat(cat_id):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cur = await db.execute("SELECT COUNT(*) FROM products WHERE category_id=? AND active=1", (cat_id,))
        r = await cur.fetchone()
        return r[0]

async def get_product(pid):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cur = await db.execute("SELECT * FROM products WHERE id=?", (pid,))
        return await cur.fetchone()

async def inc_views(pid):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("UPDATE products SET views=views+1 WHERE id=?", (pid,))
        await db.commit()

async def decrement_stock(pid, qty=1):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("UPDATE products SET stock=stock-?, sold=sold+? WHERE id=?", (qty, qty, pid))
        await db.commit()

async def search_products(text):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cur = await db.execute(
            "SELECT * FROM products WHERE active=1 AND name LIKE ? LIMIT 20",
            (f"%{text}%",))
        return await cur.fetchall()

# ---------- purchases ----------
async def add_purchase(uid, pid, price, email, senha, link, days=30):
    now = datetime.utcnow()
    exp = now + timedelta(days=days)
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cur = await db.execute(
            "INSERT INTO purchases(user_id,product_id,price,email,password,link,created_at,expires_at,active) VALUES(?,?,?,?,?,?,?,?,1)",
            (uid, pid, price, email, senha, link, now.isoformat(), exp.isoformat())
        )
        await db.commit()
        return cur.lastrowid

async def user_purchases(uid, active_only=True, page=0, per_page=1):
    q = "SELECT * FROM purchases WHERE user_id=?"
    args = [uid]
    if active_only:
        q += " AND active=1 AND expires_at > ?"
        args.append(datetime.utcnow().isoformat())
    q += " ORDER BY id DESC LIMIT ? OFFSET ?"
    args += [per_page, page*per_page]
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cur = await db.execute(q, args)
        return await cur.fetchall()

async def count_user_purchases(uid, active_only=True):
    q = "SELECT COUNT(*) FROM purchases WHERE user_id=?"
    args = [uid]
    if active_only:
        q += " AND active=1 AND expires_at > ?"
        args.append(datetime.utcnow().isoformat())
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cur = await db.execute(q, args)
        r = await cur.fetchone()
        return r[0]

async def get_purchase(purchase_id):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cur = await db.execute("SELECT * FROM purchases WHERE id=?", (purchase_id,))
        return await cur.fetchone()

async def has_purchased_product(uid, pid):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cur = await db.execute(
            "SELECT id FROM purchases WHERE user_id=? AND product_id=? AND active=1 AND expires_at > ? LIMIT 1",
            (uid, pid, datetime.utcnow().isoformat())
        )
        return await cur.fetchone()

# ---------- stats ----------
async def user_stats(uid):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cur = await db.execute("SELECT COUNT(*), COALESCE(SUM(price),0) FROM purchases WHERE user_id=?", (uid,))
        compras, total = await cur.fetchone()
        cur = await db.execute(
            "SELECT COALESCE(SUM(value),0) FROM pix WHERE user_id=? AND status='paid' AND type='recharge'", (uid,))
        pix = (await cur.fetchone())[0]
        cur = await db.execute(
            "SELECT COALESCE(SUM(value),0) FROM gifts WHERE used_by=? AND used=1", (uid,))
        gifts = (await cur.fetchone())[0]
        return {"compras": compras, "total_gasto": total, "pix": pix, "gifts": gifts}

# ---------- pix ----------
async def add_pix(ref, uid, value, type_, code, product_id=None, qty=1, minutes=10):
    now = datetime.utcnow()
    exp = now + timedelta(minutes=minutes)
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "INSERT INTO pix(ref,user_id,value,type,status,code,product_id,qty,created_at,expires_at) VALUES(?,?,?,?, 'pending', ?,?,?,?,?)",
            (ref, uid, value, type_, code, product_id, qty, now.isoformat(), exp.isoformat())
        )
        await db.commit()

async def get_pix(ref):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cur = await db.execute("SELECT * FROM pix WHERE ref=?", (ref,))
        return await cur.fetchone()

async def set_pix_status(ref, status):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("UPDATE pix SET status=? WHERE ref=?", (status, ref))
        await db.commit()

async def pending_pix_older_than(minutes):
    lim = (datetime.utcnow() - timedelta(minutes=minutes)).isoformat()
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cur = await db.execute("SELECT * FROM pix WHERE status='pending' AND created_at < ?", (lim,))
        return await cur.fetchall()

async def expired_pix():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cur = await db.execute(
            "SELECT * FROM pix WHERE status='pending' AND expires_at < ?",
            (datetime.utcnow().isoformat(),))
        return await cur.fetchall()

# ---------- gifts ----------
async def get_gift(code):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cur = await db.execute("SELECT * FROM gifts WHERE code=? AND used=0", (code,))
        return await cur.fetchone()

async def use_gift(code, uid):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "UPDATE gifts SET used=1, used_by=?, used_at=? WHERE code=?",
            (uid, datetime.utcnow().isoformat(), code))
        await db.commit()

# ---------- affiliates ----------
async def get_affiliate(uid):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cur = await db.execute("SELECT * FROM affiliates WHERE user_id=?", (uid,))
        row = await cur.fetchone()
        if row:
            return row
        await db.execute("INSERT INTO affiliates(user_id) VALUES(?)", (uid,))
        await db.commit()
        cur = await db.execute("SELECT * FROM affiliates WHERE user_id=?", (uid,))
        return await cur.fetchone()

async def set_affiliate_status(uid, status):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("UPDATE affiliates SET status=? WHERE user_id=?", (status, uid))
        await db.commit()

async def count_referrals(uid):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cur = await db.execute("SELECT COUNT(*) FROM users WHERE referred_by=?", (uid,))
        r = await cur.fetchone()
        return r[0]

# ---------- ranking ----------
async def ranking_servicos():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cur = await db.execute("""
            SELECT u.id, u.name, COUNT(*) as c FROM purchases p
            JOIN users u ON u.id=p.user_id
            GROUP BY p.user_id ORDER BY c DESC LIMIT 10
        """)
        return await cur.fetchall()

async def ranking_recargas():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cur = await db.execute("""
            SELECT u.id, u.name, COALESCE(SUM(p.value),0) as s FROM pix p
            JOIN users u ON u.id=p.user_id WHERE p.status='paid' AND p.type='recharge'
            GROUP BY p.user_id ORDER BY s DESC LIMIT 10
        """)
        return await cur.fetchall()

async def ranking_saldo():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cur = await db.execute("SELECT id,name,saldo FROM users ORDER BY saldo DESC LIMIT 10")
        return await cur.fetchall()

async def ranking_gift():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cur = await db.execute("""
            SELECT u.id, u.name, COUNT(*) as c FROM gifts g
            JOIN users u ON u.id=g.used_by WHERE g.used=1
            GROUP BY g.used_by ORDER BY c DESC LIMIT 10
        """)
        return await cur.fetchall()

# ---------- abandoned ----------
async def track_abandoned(uid, pid, type_='cart', value=0):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("DELETE FROM abandoned WHERE user_id=? AND type=? AND notified=0", (uid, type_))
        await db.execute(
            "INSERT INTO abandoned(user_id,product_id,type,value,created_at,notified) VALUES(?,?,?,?,?,0)",
            (uid, pid, type_, value, datetime.utcnow().isoformat()))
        await db.commit()

async def abandoned_to_notify(minutes=15):
    lim = (datetime.utcnow() - timedelta(minutes=minutes)).isoformat()
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cur = await db.execute("SELECT * FROM abandoned WHERE notified=0 AND created_at < ?", (lim,))
        return await cur.fetchall()

async def mark_abandoned_notified(aid):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("UPDATE abandoned SET notified=1 WHERE id=?", (aid,))
        await db.commit()

async def clear_abandoned(uid, pid=None):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        if pid:
            await db.execute("DELETE FROM abandoned WHERE user_id=? AND product_id=?", (uid, pid))
        else:
            await db.execute("DELETE FROM abandoned WHERE user_id=?", (uid,))
        await db.commit()
