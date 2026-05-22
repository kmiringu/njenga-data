from flask import Flask, jsonify, request, send_from_directory
import sqlite3, os

app = Flask(__name__, static_folder='calculator')
DB  = os.path.join(os.path.dirname(__file__), 'data', 'njenga.db')

def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def materials_index():
    conn = db()
    row = conn.execute("""
        SELECT AVG(price_index) as idx FROM material_prices
        WHERE year = (SELECT MAX(year) FROM material_prices)
          AND quarter = (
            SELECT quarter FROM material_prices
            WHERE year = (SELECT MAX(year) FROM material_prices)
            ORDER BY quarter DESC LIMIT 1)
    """).fetchone()
    conn.close()
    return round(row['idx'], 2)

def steel_index():
    conn = db()
    row = conn.execute("""
        SELECT price_index FROM material_prices
        WHERE material = 'steel'
          AND year = (SELECT MAX(year) FROM material_prices)
          AND quarter = (
            SELECT quarter FROM material_prices
            WHERE year = (SELECT MAX(year) FROM material_prices)
            ORDER BY quarter DESC LIMIT 1)
    """).fetchone()
    conn.close()
    return round(row['price_index'], 1)

def category_costs(county, unit_type):
    """Real per-category costs from CAHF — averaged across multiple records."""
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

def all_counties_costs(unit_type):
    conn = db()
    rows = conn.execute("""
        SELECT county, SUM(avg_amount) as total FROM (
            SELECT county, cost_category, AVG(amount_kes) as avg_amount
            FROM cost_benchmarks WHERE unit_type = ?
            GROUP BY county, cost_category
        ) GROUP BY county ORDER BY total ASC
    """, (unit_type,)).fetchall()
    conn.close()
    return [{'county': r['county'], 'base_cost': round(r['total'])} for r in rows]

def median_income(county):
    conn = db()
    row = conn.execute("""
        SELECT median_monthly_income_kes FROM household_income
        WHERE county = ? ORDER BY year DESC LIMIT 1
    """, (county,)).fetchone()
    conn.close()
    return row['median_monthly_income_kes'] if row else None

def material_trend():
    conn = db()
    rows = conn.execute("""
        SELECT year, quarter, material, price_index
        FROM material_prices ORDER BY year, quarter, material
    """).fetchall()
    conn.close()
    labels, data = [], {}
    for r in rows:
        label = f"{r['year']} {r['quarter']}"
        if label not in labels:
            labels.append(label)
        if r['material'] not in data:
            data[r['material']] = []
        data[r['material']].append(round(r['price_index'], 1))
    return {'labels': labels, 'series': data}

# ── API ───────────────────────────────────────────────────────────────────────

@app.route('/api/meta')
def meta():
    conn = db()
    counties   = [r['county']    for r in conn.execute("SELECT DISTINCT county FROM cost_benchmarks ORDER BY county").fetchall()]
    unit_types = [r['unit_type'] for r in conn.execute("SELECT DISTINCT unit_type FROM cost_benchmarks ORDER BY unit_type").fetchall()]
    incomes    = {r['county']: r['median_monthly_income_kes'] for r in conn.execute("SELECT county, median_monthly_income_kes FROM household_income").fetchall()}
    conn.close()
    return jsonify({
        'counties':      counties,
        'unit_types':    unit_types,
        'incomes':       incomes,
        'current_index': materials_index(),
        'steel_index':   steel_index(),
        'base_index':    100
    })

@app.route('/api/costs')
def costs():
    """Return per-category costs for a county/unit_type so frontend can render checkboxes."""
    county    = request.args.get('county', 'Nairobi')
    unit_type = request.args.get('unit_type', '2BR')
    cats      = category_costs(county, unit_type)
    curr_idx  = materials_index()
    total     = sum(c['amount'] for c in cats)
    for c in cats:
        c['pct']             = round(c['amount'] / total * 100, 1)
        c['adjusted_amount'] = round(c['amount'] * (curr_idx / 100))
    return jsonify({'categories': cats, 'current_index': curr_idx})

@app.route('/api/calculate', methods=['POST'])
def calculate():
    d         = request.json
    county    = d.get('county', 'Nairobi')
    utype     = d.get('unit_type', '2BR')
    income    = float(d.get('income', 40000))
    rate      = float(d.get('savings_rate', 0.30))
    # list of categories James says he already has covered
    excluded  = set(d.get('excluded_categories', []))

    curr_idx  = materials_index()
    cats      = category_costs(county, utype)

    if not cats:
        return jsonify({'error': 'No data for this county/unit type'}), 404

    full_base = sum(c['amount'] for c in cats)
    full_adj  = round(full_base * (curr_idx / 100))

    # what James still needs to save for
    needed_cats = [c for c in cats if c['category'] not in excluded]
    remaining_base = sum(c['amount'] for c in needed_cats)
    remaining_adj  = round(remaining_base * (curr_idx / 100))

    annual_sav = round(income * rate * 12)
    years      = round(remaining_adj / annual_sav, 1) if annual_sav > 0 else 0

    # savings so far (excluded categories = already funded)
    already_funded = round((full_base - remaining_base) * (curr_idx / 100))

    # enrich categories with adjusted amounts and pct of full cost
    for c in cats:
        c['adjusted_amount'] = round(c['amount'] * (curr_idx / 100))
        c['pct']             = round(c['amount'] / full_base * 100, 1)
        c['excluded']        = c['category'] in excluded

    # labour pct of full cost
    labour_pct = next((c['pct'] for c in cats if c['category'] == 'Labour'), 0)

    # what James still needs — ordered savings plan from DB categories
    savings_plan = []
    for c in needed_cats:
        adj  = round(c['amount'] * (curr_idx / 100))
        yrs  = round(adj / annual_sav, 1) if annual_sav > 0 else 0
        savings_plan.append({
            'category': c['category'],
            'cost':     adj,
            'years':    yrs,
            'pct':      round(c['amount'] / remaining_base * 100, 1) if remaining_base > 0 else 0
        })

    # county comparison
    all_costs    = all_counties_costs(utype)
    comparisons  = []
    for co in all_costs:
        # apply same exclusions proportionally for comparison
        excluded_ratio = (full_base - remaining_base) / full_base if full_base > 0 else 0
        adj_c   = round(co['base_cost'] * (1 - excluded_ratio) * (curr_idx / 100))
        yrs_c   = round(adj_c / annual_sav, 1) if annual_sav > 0 else 0
        inc_c   = median_income(co['county'])
        yrs_med = round(adj_c / (inc_c * rate * 12), 1) if inc_c else None
        comparisons.append({
            'county':       co['county'],
            'adjusted_cost': adj_c,
            'years_user':   yrs_c,
            'years_median': yrs_med,
            'is_selected':  co['county'] == county
        })
    cheapest = comparisons[0]

    # verdict
    if years == 0:
        verdict = 'Ready to build'
        advice  = 'You have already covered all cost categories. You are ready to begin.'
        level   = 'green'
    elif years <= 5:
        verdict = 'Build now — within reach'
        advice  = f"At your savings rate you can cover the remaining costs in {years} years. You have already taken care of KSh {already_funded:,} worth of costs."
        level   = 'green'
    elif years <= 10:
        verdict = 'Build in phases'
        advice  = f"Save category by category — start with {savings_plan[0]['category'].lower()} in {savings_plan[0]['years']} years, then work through the rest. Full completion in {years} years."
        level   = 'amber'
    else:
        verb    = f"Building in {cheapest['county']} cuts that to {cheapest['years_user']} years." if cheapest['county'] != county else ""
        advice  = f"At {years} years this is a long road. {verb} Or increase your monthly savings rate to shorten the timeline."
        verdict = 'Not yet — but here is your path'
        level   = 'red'

    return jsonify({
        'county':           county,
        'unit_type':        utype,
        'full_cost':        full_adj,
        'already_funded':   already_funded,
        'remaining_cost':   remaining_adj,
        'current_index':    curr_idx,
        'annual_savings':   annual_sav,
        'years':            years,
        'labour_pct':       labour_pct,
        'steel_change':     round(steel_index() - 100, 1),
        'verdict':          verdict,
        'advice':           advice,
        'level':            level,
        'categories':       cats,
        'savings_plan':     savings_plan,
        'comparisons':      comparisons,
        'cheapest':         cheapest,
        'excluded':         list(excluded)
    })

@app.route('/api/trends')
def trends():
    return jsonify(material_trend())

@app.route('/')
def index():
    return send_from_directory('calculator', 'index.html')

if __name__ == '__main__':
    print("NjengaData running at http://localhost:5000")
    app.run(debug=True, port=5000)
