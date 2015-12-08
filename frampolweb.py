from __future__ import unicode_literals
from flask import Flask, render_template, request, redirect, url_for, flash
from flaskext.mysql import MySQL
import os


mysql = MySQL()
app = Flask(__name__)

# Set session secret key
app.secret_key = '101'

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'CDMA1xafri'
app.config['MYSQL_DATABASE_DB'] = 'frampol_subscribers'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/show_entries/')
def show_entries():
    sql = 'SELECT subscriber.sub_id, subscriber.ipaddress ,subscriber.attribute ,subscriber.plan_id ,subscriber.dom_id ,domains.domain_name ,plan.plan_name\
    FROM subscriber \
    INNER JOIN domains \
    ON subscriber.dom_id=domains.dom_id \
    INNER JOIN PLAN  \
    ON subscriber.plan_id =plan.plan_id ORDER BY subscriber.ipaddress '
    cursor.execute(sql)
    conn.commit()
    data = cursor.fetchall()
    subscribers = [
        dict(sub_id=row[0], ipaddress=row[1], attribute=row[2], plan_id=row[3], dom_id=row[4], domain_name=row[5],
             plan_name=row[6]) for
        row in data]
    total = len(subscribers)

    app_root = os.path.dirname(os.path.abspath(__file__))
    file_to_write_your_data = os.path.join(app_root, 'static/frampol')

    with open(file_to_write_your_data, 'w') as f:
        for sub in subscribers:
            ipaddress = str(sub['ipaddress'])
            domain_name = str(sub['domain_name'])
            ip_at_domain = ("".join([ipaddress, domain_name]))
            attribute = str(sub['attribute'])
            plan = str(sub['plan_name'])

            contents = (" ".join([ipaddress, ip_at_domain, attribute, plan]))
            f.write(contents)
            f.write("\n")

    return render_template('display.html', subscribers=subscribers, total=total)


@app.route('/add_users', methods=['POST'])
def add_users():
    ipaddress = request.form["ipaddress"]
    plan_id = int(request.form["plan_id"])
    dom_id = int(request.form["dom_id"])
    attribute = request.form["attribute"]
    sql = 'insert into subscriber (ipaddress ,plan_id, dom_id ,attribute) values (%s,%s ,%s ,%s)'
    cursor.execute(sql, [ipaddress, plan_id, dom_id, attribute])
    conn.commit()
    conn.close
    flash('Subscriber with IP Address ' + ipaddress + ' has been successfully Added')
    return redirect(url_for('show_entries'))


@app.route('/edit_entry/<int:sub_id>')
def edit_entry(sub_id):
    id = str(sub_id)
    sql = 'SELECT subscriber.sub_id, subscriber.ipaddress ,subscriber.plan_id ,subscriber.dom_id ,domains.domain_name ,plan.plan_name \
    FROM subscriber \
    INNER JOIN domains \
    ON subscriber.dom_id=domains.dom_id \
    INNER JOIN PLAN  \
    ON subscriber.plan_id =plan.plan_id WHERE sub_id=' + id
    cursor.execute(sql)
    conn.commit()
    data = cursor.fetchall()
    subscribers = [
        dict(sub_id=row[0], ipaddress=row[1], plan_id=row[2], dom_id=row[3], domain_name=row[4],
             plan_name=row[5]) for
        row in data]
    # entries = [{"title": row[0], "text": row[1], "id": row[2]} for row in data]
    # Below is the dropdown for PLANs

    sql = 'select plan_name ,domain_name ,plan_id, dom_id from plan ,domains ';
    cursor.execute(sql)
    conn.commit()
    data = cursor.fetchall()
    dropdown = [dict(plan_name=row[0], domain_name=row[1], plan_id=row[2], dom_id=row[3]) for row in data]
    return render_template('edit.html', subscribers=subscribers, dropdown=dropdown)
    conn.close


@app.route('/show_dropdowns/')
def show_dropdowns():
    sql = 'select plan_name ,domain_name ,plan_id, dom_id from plan ,domains ';
    cursor.execute(sql)
    conn.commit()
    data = cursor.fetchall()
    dropdown = [dict(plan_name=row[0], domain_name=row[1], plan_id=row[2], dom_id=row[3]) for row in data]
    return render_template('add_user.html', dropdown=dropdown)


@app.route('/update_entry/<int:sub_id>', methods=['GET', 'POST'])
def update_entry(sub_id):
    id = str(sub_id)
    ipaddress = request.form["ipaddress"]
    plan_id = int(request.form["plan_id"])
    data = (ipaddress, plan_id)
    sql = 'UPDATE subscriber SET ipaddress =%s,plan_id=%s  WHERE sub_id=' + id
    cursor.execute(sql, data)
    conn.commit()
    conn.close
    flash('Subscriber with IP Address ' + ipaddress + ' has been successfully updated ')
    return redirect(url_for('show_entries'))


@app.route('/delete_entry/<int:sub_id>')
def delete_entry(sub_id):
    id = str(sub_id)
    sql_to_populate_query_into_a_dict = 'select ipaddress from subscriber WHERE sub_id=' + id
    cursor.execute(sql_to_populate_query_into_a_dict)
    conn.commit()
    data = cursor.fetchall()
    subscribers = [dict(ipaddress=row[0]) for row in data]
    for sub in subscribers:
        ipaddress = str(sub['ipaddress'])

    sql_to_delete_the_subscriber = 'delete from subscriber WHERE sub_id=' + id
    cursor.execute(sql_to_delete_the_subscriber)
    conn.commit()
    flash('Subscriber with IP Address ' + ipaddress + ' has been successfully deleted ')
    return redirect(url_for('show_entries'))
    conn.close

# Run
if __name__ == '__main__':
    app.run(debug=True)
