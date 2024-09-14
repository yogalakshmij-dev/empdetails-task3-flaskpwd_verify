from flask import Flask,session,render_template,redirect,request,url_for,flash
import re
from flask_mysqldb import MySQL
app=Flask(__name__)
app.secret_key="yoga@sql"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Yoga_1010@SQL'
app.config['MYSQL_DB'] = 'employee_details'

mysql = MySQL(app)

def validate_password(password):    
    if len(password)<8:
        return False 
    elif not re.search (r"[a-z]",password):
        return False 
    elif not re.search(r"[A-Z]",password):
        return False 
    elif not re.search(r"[0-9]",password):
        return False 
    elif not re.search(r"[!@#$%^&*+=]",password):
        return False 
    return True 


def loggedin():
    return "username" in session

@app.route("/")
def home():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM emp_detail")
    data = cur.fetchall()
    cur.close()
    return render_template("index.html", employee=data)

@app.route("/insert", methods=["GET", "POST"])
def insert():
    if request.method == "POST":
        name = request.form.get("name")
        age = request.form.get("age")
        employee_id=request.form.get("employee_id")
        emp_role=request.form.get("emp_role")
        salary=request.form.get("salary")
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO emp_detail (Name, Age, Employee_id,Emp_role,Salary) VALUES (%s, %s, %s, %s, %s)",
                    (name, age,employee_id,emp_role,salary))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for("home"))
    return render_template("insert.html")

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    if request.method == "POST":
        name = request.form.get("name")
        age = request.form.get("age")
        employee_id=request.form.get("employee_id")
        emp_role=request.form.get("emp_role")
        salary=request.form.get("salary")
        cur = mysql.connection.cursor()
        cur.execute(" UPDATE emp_detail SET Name=%s, Age=%s, Employee_id=%s,Emp_role=%s,Salary=%s WHERE id=%s",
                    (name, age,employee_id,emp_role,salary,id))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for("home"))
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM emp_detail WHERE id=%s", (id,))
    data = cur.fetchone()
    cur.close()
    return render_template("edit.html", employees=data)


@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM emp_detail WHERE id=%s", (id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for("home"))


@app.route("/signup",methods=["GET","POST"])
def signup():
    if request.method=="POST":
        username=request.form.get("username")
        password=request.form.get("password")
        if not validate_password(password):
            flash('Password should be at least 8 characters long and contain uppercase, lowercase, digit, and special characters.', 'danger')
            return redirect(url_for("signup"))
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO emp_password(username,password) VALUES(%s,%s)",(username,password))
        mysql.connection.commit()
        cur.close()
        flash("signup successfull",'success')
        return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        username = request.form['username']
        password =request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("select * from  emp_password where username=%s and password=%s",(username,password))
        data=cur.fetchone()
        mysql.connection.commit()
        
        if data:
            cur.execute("SELECT * FROM emp_detail WHERE Name=%s", (username,))
            emp_data = cur.fetchone()
            cur.close() 
            if emp_data:
                session["username"] = username
                session["emp_data"] = emp_data  
                flash("Login successful!", 'success')
                return redirect(url_for("profile"))
            else:
                flash("Employee details not found!", 'danger')
                return redirect(url_for("login"))
        else:
            cur.close()
            flash("Invalid username or password.", 'danger')
            return redirect(url_for("login"))
    return render_template("login.html")


@app.route("/profile")
def profile():
    if not loggedin():
        flash("Please log in to view your profile.",'danger')
        return redirect(url_for("login"))
    emp_data = session.get("emp_data")
    return render_template("profile.html", employee=emp_data)


@app.route("/logout")
def logout():
    session.pop("username",None)
    flash("You have been logged out sucessfully",'info')
    return redirect(url_for("login"))


if __name__=="__main__":
    app.run(debug=True)
    