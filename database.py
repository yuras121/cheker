import aiosqlite

DB_NAME = "checker_pro.db"

async def init_db():
    """Створює таблиці при першому запуску"""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS global_stats (
                id INTEGER PRIMARY KEY,
                total_checks INTEGER DEFAULT 0
            )
        ''')
        # Додаємо перший запис, якщо база порожня (почнемо зі 100 для солідності)
        await db.execute('INSERT OR IGNORE INTO global_stats (id, total_checks) VALUES (1, 100)')
        await db.commit()

async def increment_checks():
    """Додає +1 до загальної статистики перевірок"""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('UPDATE global_stats SET total_checks = total_checks + 1 WHERE id = 1')
        await db.commit()

async def get_total_checks() -> int:
    """Отримує загальну кількість перевірок"""
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT total_checks FROM global_stats WHERE id = 1') as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0
