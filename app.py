from flask import Flask, jsonify, request, send_from_directory
import sqlite3, os

app = Flask(__name__, static_folder='calculator')
DB  = os.path.join(os.path.dirname(__file__), 'data', 'njenga.db')

def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

# ── helpers ──────────────────────────────────────────────────────────────────

def materials_index():
    """Average index across steel, cement, timber for the latest quarter."""
    conn = db()
    row = conn.execute("""
        SELECT AVG(price_index) as idx
        FROM material_prices
        WHERE year = (SELECT MAX(year) FROM material_prices)
          AND quarter = (
                SELECT quarter FROM material_prices
                WHERE year = (SELECT MAX(year) FROM material_prices)
                ORDER BY quarter DESC LIMIT 1
              )
    """).fetchone()
    conn.close()
    return round(row['idx'], 2)

def steel_index():
    """Steel-specific index for latest quarter (used in findings display)."""
    conn = db()
    row = conn.execute("""
        SELECT price_index FROM material_prices
        WHERE material = 'steel'
          AND year = (SELECT MAX(year) FROM material_prices)
          AND quarter = (
                SELECT quarter FROM material_prices
                WHERE year = (SELECT MAX(year) FROM material_prices)
                ORDER BY quarter DESC LIMIT 1
              )
    """).fetchone()
    conn.close()
    return round(row['price_index'], 1)

def base_cost(county, unit_type):
    """Average cost per category from cost_benchmarks, summed."""
    conn = db()
    row = conn.execute("""
        SELECT SUM(avg_amount) as total FROM (
            SELECT cost_category, AVG(amount_kes) as avg_amount
            FROM cost_benchmarks
            WHERE county = ? AND unit_type = ?
            GROUP BY cost_category
        )
    """, (county, unit_type)).fetchone()
    conn.close()
    return round(row['total']) if row['total'] else None

def cost_breakdown(county, unit_type):
    """Per-category averages for the cost breakdown chart."""
    conn = db()
    rows = conn.execute("""
        SELECT cost_category, AVG(amount_kes) as avg_amount
        FROM cost_benchmarks
        WHERE county = ? AND unit_type = ?
        GROUP BY cost_category
        ORDER BY avg_amount DESC
    """, (county, unit_type)).fetchall()
    conn.close()
    return [{'category': r['cost_category'], 'amount': round(r['avg_amount'])} for r in rows]

def median_income(county):
    """Median monthly income from household_income table."""
    conn = db()
    row = conn.execute("""
        SELECT median_monthly_income_kes FROM household_income
        WHERE county = ? ORDER BY year DESC LIMIT 1
    """, (county,)).fetchone()
    conn.close()
    return row['median_monthly_income_kes'] if row else None

def all_counties_costs(unit_type):
    """Base costs for all counties for comparison."""
    conn = db()
    rows = conn.execute("""
        SELECT county, SUM(avg_amount) as total FROM (
            SELECT county, cost_category, AVG(amount_kes) as avg_amount
            FROM cost_benchmarks
            WHERE unit_type = ?
            GROUP BY county, cost_category
        ) GROUP BY county ORDER BY total ASC
    """, (unit_type,)).fetchall()
    conn.close()
    return [{'county': r['county'], 'base_cost': round(r['total'])} for r in rows]

def material_trend():
    """Full price index trend for all materials — for the trend chart."""
    conn = db()
    rows = conn.execute("""
        SELECT year, quarter, material, price_index
        FROM material_prices ORDER BY year, quarter, material
    """).fetchall()
    conn.close()
    data = {}
    labels = []
    for r in rows:
        label = f"{r['year']} {r['quarter']}"
        if label not in labels:
            labels.append(label)
        if r['material'] not in data:
            data[r['material']] = []
        data[r['material']].append(round(r['price_index'], 1))
    return {'labels': labels, 'series': data}

# ── API routes ────────────────────────────────────────────────────────────────

@app.route('/api/meta')
def meta():
    """Counties, unit types, and current index — for populating dropdowns."""
    conn = db()
    counties = [r['county'] for r in conn.execute(
        "SELECT DISTINCT county FROM cost_benchmarks ORDER BY county").fetchall()]
    unit_types = [r['unit_type'] for r in conn.execute(
        "SELECT DISTINCT unit_type FROM cost_benchmarks ORDER BY unit_type").fetchall()]
    incomes = {}
    for r in conn.execute("SELECT county, median_monthly_income_kes FROM household_income").fetchall():
        incomes[r['county']] = r['median_monthly_income_kes']
    conn.close()
    return jsonify({
        'counties':   counties,
        'unit_types': unit_types,
        'incomes':    incomes,
        'current_index': materials_index(),
        'steel_index':   steel_index(),
        'base_index':    100
    })

@app.route('/api/calculate', methods=['POST'])
def calculate():
    d        = request.json
    county   = d.get('county', 'Nairobi')
    utype    = d.get('unit_type', '2BR')
    income   = float(d.get('income', 40000))
    rate     = float(d.get('savings_rate', 0.30))

    curr_idx = materials_index()
    base     = base_cost(county, utype)
    if not base:
        return jsonify({'error': 'No data for this county/unit type'}), 404

    adjusted     = round(base * (curr_idx / 100))
    annual_sav   = round(income * rate * 12)
    years        = round(adjusted / annual_sav, 1)

    # breakdown
    breakdown = cost_breakdown(county, utype)
    total_b   = sum(c['amount'] for c in breakdown)
    for c in breakdown:
        c['pct'] = round(c['amount'] / total_b * 100, 1)

    # labour pct
    labour_pct = next((c['pct'] for c in breakdown if c['category'] == 'Labour'), 0)

    # phase plan
    phases = [
        {'name': 'Foundation',   'share': 0.18},
        {'name': 'Substructure', 'share': 0.22},
        {'name': 'Walling',      'share': 0.28},
        {'name': 'Roofing',      'share': 0.20},
        {'name': 'Finishing',    'share': 0.12},
    ]
    for p in phases:
        p['cost']  = round(adjusted * p['share'])
        p['years'] = round((adjusted * p['share']) / annual_sav, 1)

    # county comparison
    all_costs = all_counties_costs(utype)
    comparisons = []
    for c in all_costs:
        adj_c  = round(c['base_cost'] * (curr_idx / 100))
        yrs_c  = round(adj_c / annual_sav, 1)
        inc_c  = median_income(c['county'])
        yrs_median = round(adj_c / (inc_c * 0.30 * 12), 1) if inc_c else None
        comparisons.append({
            'county':        c['county'],
            'adjusted_cost': adj_c,
            'years_user':    yrs_c,
            'years_median':  yrs_median,
            'is_selected':   c['county'] == county
        })

    cheapest = comparisons[0]

    # verdict
    if years <= 5:
        verdict = 'Build now'
        advice  = f"At your savings rate you can afford to build in {years} years. Consider starting the foundation phase immediately — it only takes {phases[0]['years']} years to fund."
        level   = 'green'
    elif years <= 10:
        verdict = 'Build in phases'
        advice  = f"You cannot fund the full build upfront. Start with the foundation in {phases[0]['years']} years, then build phase by phase. The full build completes in {years} years."
        level   = 'amber'
    else:
        verdict = 'Not yet — but here is your path'
        advice  = (f"At {years} years this is a long road in {county}. "
                   f"Building in {cheapest['county']} cuts that to {cheapest['years_user']} years. "
                   f"Or start with just the foundation — you can break ground in {phases[0]['years']} years.")
        level   = 'red'

    return jsonify({
        'county':        county,
        'unit_type':     utype,
        'base_cost':     base,
        'adjusted_cost': adjusted,
        'current_index': curr_idx,
        'annual_savings':annual_sav,
        'years':         years,
        'labour_pct':    labour_pct,
        'steel_change':  round(steel_index() - 100, 1),
        'verdict':       verdict,
        'advice':        advice,
        'level':         level,
        'breakdown':     breakdown,
        'phases':        phases,
        'comparisons':   comparisons,
        'cheapest':      cheapest
    })

@app.route('/api/trends')
def trends():
    return jsonify(material_trend())

@app.route('/')
def index():
    return send_from_directory('calculator', 'index.html')

if __name__ == '__main__':
    print("NjengaData calculator running at http://localhost:5000")
    app.run(debug=True, port=5000)
