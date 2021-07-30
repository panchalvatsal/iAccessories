from flask import render_template, session, request, redirect, url_for, flash, current_app, make_response, Flask
from flask_login import login_required, current_user, logout_user, login_user
from shop import app, db, photos, search, bcrypt, login_manager
from .forms import CustomerRegisterForm, CustomerLoginFrom, ContactForm
from .model import Register, CustomerOrder
import secrets
import os, json
import pdfkit
import stripe



@app.route('/payment', methods=['POST'])
@login_required
def payment():
    publishable_key = 'pk_test_51JDT1mSGnjHjLb0UTFXRee57JgDRohu5t0nGBKuJVJXpMIkgXCzsNLU3Kuha25d4O3aYk1aahBWJeNDMMZJ80n1I00GGkLv1e8'
    stripe.api_key = 'sk_test_51JDT1mSGnjHjLb0Uw0IVR4vdR9nC7pJ2ll4TJM1mrMgjK1AT8b0OBS3l528uMz7JdrGUKKKPAi5RJsCwT9YLEUu8002arkAtko'
    invoice = request.form.get('invoice')
    amount = request.form.get('amount')
    name = request.form.get('name')
    address = request.form.get('address')
    if request.method == "POST":
        try:
            customer = stripe.Customer.create(
              email=request.form['stripeEmail'],
              source=request.form['stripeToken'],
            )

            charge = stripe.Charge.create(
                name=name,
                customer=customer.id,
                description='iAccessories',
                address=address,
                amount=amount,
                currency='usd',
                )
            orders = CustomerOrder.query.filter_by(customer_id=current_user.id,
                                                   invoice=invoice).order_by(CustomerOrder.id.desc()).first()
            orders.status = 'Paid'
            db.session.commit()
            flash(f'Thank you for ordering!')
            return render_template('/')

        except stripe.error.CardError as e:
            flash(f'Your card has been declined')


# @app.route('/thanks')
# def thanks():
#     session = stripe.checkout.Session.retrieve(request.args.get('session_id'))
#     customer = stripe.Customer.retrieve(session.customer)
#     return render_template_string('<html><body><h1>Thanks for your order, {{customer.name}}!</h1></body></html>')

@app.route('/customers/register', methods=['GET', 'POST'])
def customer_register():
    form = CustomerRegisterForm()
    if form.validate_on_submit():
        hash_password = bcrypt.generate_password_hash(form.password.data)
        register = Register(name=form.name.data, username=form.username.data, email=form.email.data,
                            password=hash_password, country=form.country.data, city=form.city.data,
                            contact=form.contact.data, address=form.address.data, zipcode=form.zipcode.data)
        db.session.add(register)
        flash(f'Welcome {form.name.data} Thank you for registering', 'success')
        db.session.commit()
        return redirect(url_for('customer_register'))
    return render_template('customers/register.html', form=form)


@app.route('/customers/login', methods=['GET', 'POST'])
def customerLogin():
    form = CustomerLoginFrom()
    if form.validate_on_submit():
        user = Register.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('You are logged in now!', 'success')
            next = request.args.get('next')
            return redirect(next or url_for('home'))
        flash('Incorrect email and password', 'danger')
        return redirect(url_for('customerLogin'))

    return render_template('customers/login.html', form=form)


@app.route('/customer/logout')
def customer_logout():
    logout_user()
    return redirect(url_for('home'))


def updateshoppingcart():
    for key, shopping in session['Shoppingcart'].items():
        session.modified = True
        del shopping['image']
        del shopping['colors']
    return updateshoppingcart


@app.route('/getorder')
@login_required
def get_order():
    if current_user.is_authenticated:
        customer_id = current_user.id
        invoice = secrets.token_hex(5)
        updateshoppingcart()
        try:
            order = CustomerOrder(invoice=invoice, customer_id=customer_id, orders=session['Shoppingcart'])
            db.session.add(order)
            db.session.commit()
            session.pop('Shoppingcart')
            flash('Your order has been sent successfully', 'success')
            return redirect(url_for('orders', invoice=invoice))
        except Exception as e:
            print(e)
            flash('Something went wrong while sending your order', 'danger')
            return redirect(url_for('getCart'))


@app.route('/orders/<invoice>')
@login_required
def orders(invoice):
    if current_user.is_authenticated:
        grandTotal = 0
        subTotal = 0
        customer_id = current_user.id
        customer = Register.query.filter_by(id=customer_id).first()
        orders = CustomerOrder.query.filter_by(customer_id=customer_id, invoice=invoice).order_by(CustomerOrder.id.desc()).first()
        for _key, product in orders.orders.items():
            discount = (product['discount']/100) * float(product['price'])
            subTotal += float(product['price']) * int(product['quantity'])
            subTotal -= discount
            tax = ("%.2f" % (.06 * float(subTotal)))
            grandTotal = ("%.2f" % (1.06 * float(subTotal)))

    else:
        return redirect(url_for('customerLogin'))
    return render_template('customers/order.html', invoice=invoice, tax=tax,subTotal=subTotal,grandTotal=grandTotal,
                           customer=customer,orders=orders)





@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if request.method == 'POST':
        flash('Form posted. We will get back to u soon', 'success')
        return render_template('contact.html')

    elif request.method == 'GET':
        return render_template('contact.html', form=form)



@app.route('/about')
def about():
    return render_template('about.html')

