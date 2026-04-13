import os
import time
import multiprocessing as mp
from itertools import product
from collections import Counter
from unittest import result
import psycopg2
from psycopg2.extras import execute_values
import random

# ================== CONFIG ==================
DB_DSN = os.getenv("DB_DSN", "dbname=arbo20 user=postgres password=admin2025 host=127.0.0.1 port=5432")
BATCH_SIZE = 5000
GRID_N = 5
TARGET_SUM = 20
DIGITS = list(range(10))
ALLOWED_CENTERS = [4,5,6,7,8,9]

# ================== PRECOMPUTE VALID LINES ==================
def generate_valid_lines():
    valid = []
    for row in product(DIGITS, repeat=5):
        if sum(row) == TARGET_SUM:
            cnt = [0]*10
            for v in row:
                cnt[v] += 1
            valid.append((tuple(row), tuple(cnt)))
    print(f"[precompute] {len(valid)} lignes valides (somme {TARGET_SUM})")
    return valid

ALL_VALID_LINES = generate_valid_lines()

# ================== DB HELPERS ==================
def db_connect():
    return psycopg2.connect(DB_DSN)

def db_insert_batch(cur, center, rows):
    data = [(center, row) for row in rows]

    execute_values(
        cur,
        "INSERT INTO grids (center, grid) VALUES %s",
        data,
        template="(%s, %s)"
    )

def get_arbo20_models(page:int = 1, size:int = 100, center:int | None = None):
    if center is None:
        center = random.choice(ALLOWED_CENTERS)
    
    page = 0 if page < 1 else page - 1

    offset = page * size
    conn = db_connect()
    cur = conn.cursor()

    cur.execute("SELECT grid FROM grids WHERE center = %s ORDER BY id LIMIT %s OFFSET %s", (center, size, offset))
    rows = cur.fetchall()
    cur.execute("SELECT COUNT(*) FROM grids WHERE center = %s",(center,))
    total = cur.fetchone()[0]
    cur.close()
    conn.close()

    return {
        "page":1 if page < 1 else page + 1,
        "size":size,
        "center":center,
        "total":total,
        "total_pages": (total + size - 1) // size,
        "grids":[r[0] for r in rows]
    }

# ================== SOLVER ==================
def solve_for_center(center_value):
    print("start solve_for_center")
    conn = db_connect()
    cur = conn.cursor()

    start = time.time()
    buffer = []
    found_count = 0

    # Filtrage des lignes autorisées
    valid_rows_for = {}
    for r in range(GRID_N):
        rows = []
        if r == 2:
            for row, cnt in ALL_VALID_LINES:
                if row[2] == center_value and cnt[center_value] == 1:
                    rows.append((row, cnt))
        else:
            for row, cnt in ALL_VALID_LINES:
                if cnt[center_value] == 0:
                    rows.append((row, cnt))
        valid_rows_for[r] = rows
        print(f"[center {center_value}] row {r}: {len(rows)} candidates")

    start_col_sums = [TARGET_SUM] * 5
    start_counts = [0] * 10

    # Place d'abord la ligne centrale pour beaucoup de pruning
    ROW_ORDER = [2, 0, 1, 3, 4]
    def dfs(row_pos_index, col_sums, counts, grid_rows, progress=[0, time.time()]):
        """
        row_pos_index : index dans ROW_ORDER (0..4)
        col_sums : liste mutée des sommes restantes par colonne
        counts : liste mutée des occurrences par chiffre
        grid_rows : liste des lignes placées (on stocke par position ROW_ORDER)
        progress : [counter, last_print_time] pour logs légers
        """
        nonlocal buffer, found_count

        # watch / progress print toutes les 50000 itérations
        progress[0] += 1
        if progress[0] % 50000 == 0:
            now = time.time()
            if now - progress[1] > 5:
                print(f"[center {center_value}] dfs it={progress[0]} row_depth={row_pos_index} found={found_count}")
                progress[1] = now

        # quick infeasibility: for any column, remaining required > max possible
        rows_left = GRID_N - row_pos_index
        max_possible = 9 * rows_left
        for s in col_sums:
            if s > max_possible:
                return

        if row_pos_index == GRID_N:
            # grid_rows currently ordered in ROW_ORDER order; flatten into final row order (0..4)
            final_rows = [None]*GRID_N
            for idx, rpos in enumerate(ROW_ORDER):
                final_rows[rpos] = grid_rows[idx]
            flat = []
            for r in final_rows:
                flat.extend(r)
            buffer.append(flat)
            found_count += 1
            if len(buffer) >= BATCH_SIZE:
                db_insert_batch(cur, center_value, buffer)
                conn.commit()
                buffer.clear()
            return

        r = ROW_ORDER[row_pos_index]
        candidates = valid_rows_for[r]

        # iterate candidates (we avoid copying counts/cols as much as possible)
        for row, cnt in candidates:
            # column feasibility quick check
            ok = True
            # apply row into col_sums in-place (and revert later) to reduce allocations
            for j in range(5):
                v = row[j]
                if v > col_sums[j]:
                    ok = False
                    break
                col_sums[j] -= v
            if not ok:
                # revert the partial subtraction we did
                for k in range(j):
                    col_sums[k] += row[k]
                continue

            # update counts in-place with early exit
            exceed = False
            for d in range(10):
                counts[d] += cnt[d]
                limit = 1 if d == center_value else 3
                if counts[d] > limit:
                    exceed = True
                    # no break here: we will revert below
                    break

            if exceed:
                # revert counts and col_sums
                for d2 in range(10):
                    # we added cnt[d2] for indices up to d (but to be safe revert all)
                    counts[d2] -= cnt[d2]
                for j2 in range(5):
                    col_sums[j2] += row[j2]
                continue

            # push row into grid_rows (we store by current depth index)
            grid_rows.append(row)
            dfs(row_pos_index + 1, col_sums, counts, grid_rows, progress)
            grid_rows.pop()

            # revert counts and col_sums after recursion
            for d2 in range(10):
                counts[d2] -= cnt[d2]
            for j2 in range(5):
                col_sums[j2] += row[j2]

    dfs(0, start_col_sums, start_counts, [])

    if buffer:
        db_insert_batch(cur, center_value, buffer)
        conn.commit()

    conn.close()
    print(f"[center {center_value}] trouvé {found_count} solutions en {time.time()-start:.1f}s")
    print("start solve_for_center")
    return found_count

# ================== MULTICORE LAUNCH ==================
if __name__ == "__main__":
    print("start main")
    """ with mp.Pool(processes=3) as pool:
        print(f"pool {pool}")
        results = pool.map(solve_for_center, [4,5,6,7,8,9]) """
    
    results = solve_for_center(4)

    print("TOTAL  for 4 :", results)
    print("end main")


"""
   def dfs(row_index, col_sums, counts, grid_rows):
        nonlocal buffer, found_count

        if row_index == GRID_N:
            flat = []
            for r in grid_rows:
                flat.extend(r)

            buffer.append(flat)
            found_count += 1

            if len(buffer) >= BATCH_SIZE:
                db_insert_batch(cur, center_value, buffer)
                conn.commit()
                buffer = []
            return

        for row, cnt in valid_rows_for[row_index]:
            ok = True
            new_col = col_sums.copy()
            for j in range(5):
                if row[j] > new_col[j]:
                    ok = False
                    break
                new_col[j] -= row[j]
            if not ok:
                continue

            new_counts = counts.copy()
            for d in range(10):
                new_counts[d] += cnt[d]
                if new_counts[d] > (1 if d == center_value else 3):
                    ok = False
                    break
            if not ok:
                continue

            grid_rows.append(row)
            dfs(row_index + 1, new_col, new_counts, grid_rows)
            grid_rows.pop()

"""