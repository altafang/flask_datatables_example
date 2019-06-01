from flask import Flask, render_template, request
import sqlite3
import pandas as pd

# Database file
DB = "data.sqlite"

# Create app
app = Flask(__name__)
app.config.from_object(__name__)

# Basic initial home page
@app.route("/")
@app.route("/index/")
def index():
    # Load table from database
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    df = pd.read_sql("SELECT * FROM my_items", conn)
    conn.close()
    # Add empty column for checkboxes
    df[" "] = ""
    # Only display the empty column and the id column
    html_table = df.to_html(escape=False, index=False, justify="left",
                            columns=[" ", "id"])
    # Manually change table id and class.
    # (built-in pandas way doesn't seem to work)
    split_html = html_table.split("\n")
    split_html[0] = """<table id="output" class="display">"""
    html_table = "\n".join(split_html)
    # Determine indices of rows with flag == 1, which will be selected
    selected_rows = df[df["flag"] == 1].index.tolist()
    # Pass html_table and selected_rows to template
    return render_template("index.html", table=html_table,
                           selected_rows=selected_rows)

# Handle selection/deselection events
@app.route("/_handle_selection")
def update_db_from_app():
    # Get data from request
    selected = int(request.args.get('selected', 0))
    row_data = request.args.get('row_data', 0) # This will be a string
    # Get from row_data string the value in the "id" column.
    # Thus this parsing will be table-dependent.
    id = int(row_data[2:-3].split(",")[1].replace('"', ''))
    # Now update database with the selection/deselection information
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("UPDATE my_items SET flag=? WHERE id=?", (selected, id))
    conn.commit()
    conn.close()
    return render_template("index.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
