from flask import redirect, render_template, url_for, flash, request, session, current_app
from shop import db, app, photos, search
from .models import Brand, Category, AddProducts
from .forms import AddProduct
import secrets, os



def brands():
    brands = Brand.query.join(AddProducts, (Brand.id == AddProducts.brand_id)).all()
    return brands


def categories():
    categories = Category.query.join(AddProducts, (Category.id == AddProducts.category_id)).all()
    return categories


@app.route('/')
def home():
    page = request.args.get('page', 1, type=int)
    products = AddProducts.query.filter(AddProducts.stock > 0).paginate(page=page)
    return render_template('products/index.html', products=products, brands=brands(), categories=categories(), page=page)


@app.route('/result')
def result():
    searchword = request.args.get('q')
    products = AddProducts.query.msearch(searchword, fields=['name', 'description'], limit=10)
    return render_template('products/result.html', products=products, brands=brands(), categories=categories())


@app.route('/product/<int:id>')
def single_page(id):
    product = AddProducts.query.get_or_404(id)
    return render_template('products/single_page.html', product=product, brands=brands(), categories=categories())


@app.route('/brand/<int:id>')
def get_brand(id):
    brand = AddProducts.query.filter_by(brand_id=id)
    return render_template('products/index.html', brand=brand, brands=brands(), categories=categories())


@app.route('/category/<int:id>')
def get_category(id):
    get_cat_prod = AddProducts.query.filter_by(category_id=id)
    return render_template('products/index.html', get_cat_prod=get_cat_prod, categories=categories(), brands=brands())


@app.route('/addbrand', methods=['GET', 'POST'])
def addbrand():
    if 'email' not in session:
        flash(f'Please login first', 'danger')
        return redirect(url_for("login"))
    if request.method == "POST":
        getbrand = request.form.get('brand')
        brand = Brand(name=getbrand)
        db.session.add(brand)
        flash(f'The Brand {getbrand} was added to your database', 'success')
        db.session.commit()
        return redirect(url_for('addbrand'))
    return render_template('products/addbrand.html', brands='brands')


@app.route('/addcategory', methods=['GET', 'POST'])
def addcategory():
    if 'email' not in session:
        flash(f'Please login first', 'danger')
        return redirect(url_for("login"))
    if request.method == "POST":
        getcategory = request.form.get('category')
        category = Category(name=getcategory)
        db.session.add(category)
        flash(f'The category {getcategory} was added to your database', 'success')
        db.session.commit()
        return redirect(url_for('addcategory'))
    return render_template('products/addbrand.html', category='category')


@app.route('/updatebrand/<int:id>', methods=['GET', 'POST'])
def updatebrand(id):
    if 'email' not in session:
        flash(f'Please login first', 'danger')
        return redirect(url_for("login"))
    updatebrand = Brand.query.get_or_404(id)
    brand = request.form.get('brand')
    if request.method == 'POST':
        updatebrand.name = brand
        flash(f'Your Brand has been updated in your database', 'success')
        db.session.commit()
        return redirect(url_for('brand'))

    return render_template('products/updatebrand.html', title='Update Brand Page', updatebrand=updatebrand)


@app.route('/updatecategory/<int:id>', methods=['GET', 'POST'])
def updatecategory(id):
    if 'email' not in session:
        flash(f'Please login first', 'danger')
        return redirect(url_for("login"))
    updatecategory = Category.query.get_or_404(id)
    category = request.form.get('category')
    if request.method == 'POST':
        updatecategory.name = category
        flash(f'Your Category has been updated in your database', 'success')
        db.session.commit()
        return redirect(url_for('category'))

    return render_template('products/updatebrand.html', title='Update Category Page', updatecategory=updatecategory)



@app.route('/addproduct', methods=['POST', 'GET'])
def addproduct():
    brands = Brand.query.all()
    categories = Category.query.all()
    form = AddProduct(request.form)
    if request.method == "POST":
        name = form.name.data
        price = form.price.data
        discount = form.discount.data
        stock = form.stock.data
        colors = form.colors.data
        description = form.description.data
        brand = request.form.get('brand')
        category = request.form.get('category')
        image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
        image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")
        image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")
        addprod = AddProducts(name=name, price=price, discount=discount, stock=stock, colors=colors, description=description, brand_id=brand, category_id=category, image_1=image_1, image_2=image_2, image_3=image_3)
        db.session.add(addprod)
        flash(f"The product {name} has been added to your database", 'success')
        db.session.commit()
        return redirect(url_for('admin'))
    return render_template('products/addproduct.html', title="Add Product", form=form, brands=brands, categories=categories)


@app.route('/updateproduct/<int:id>', methods=['GET', 'POST'])
def updateproduct(id):
    if 'email' not in session:
        flash(f'Please login first', 'danger')
        return redirect(url_for("login"))
    brands = Brand.query.all()
    categories = Category.query.all()
    product = AddProducts.query.get_or_404(id)
    brand = request.form.get('brand')
    category = request.form.get('category')
    form = AddProduct(request.form)
    if request.method == "POST":
        product.name = form.name.data
        product.price = form.price.data
        product.discount = form.discount.data
        product.stock = form.stock.data
        product.brand_id = brand
        product.category_id = category
        product.colors = form.colors.data
        product.description = form.description.data
        if request.files.get('image_1'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_1))
                product.image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
            except:
                product.image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
        if request.files.get('image_2'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_2))
                product.image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")
            except:
                product.image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")

        if request.files.get('image_3'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_3))
                product.image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")
            except:
                product.image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")
        db.session.commit()
        flash(f'Your product has been updated to your database', 'success')
        return redirect(url_for('admin'))

    form.name.data = product.name
    form.price.data = product.price
    form.discount.data = product.discount
    form.stock.data = product.stock
    form.colors.data = product.colors
    form.description.data = product.description
    return render_template('products/updateproduct.html', title='Update Product Page',
                           form=form, brands=brands, categories=categories, product=product)


@app.route('/deletebrand/<int:id>', methods=['POST'])
def deletebrand(id):
    if 'email' not in session:
        flash(f'Please login first', 'danger')
        return redirect(url_for("login"))
    brand = Brand.query.get_or_404(id)
    if request.method == "POST":
        db.session.delete(brand)
        db.session.commit()
        flash(f'The brand {brand.name} has been deleted from your database', 'success')
        return redirect(url_for('admin'))
    flash(f'The brand {brand.name} cannot be deleted from your database', 'warning')
    return redirect(url_for('admin'))


@app.route('/deletecategory/<int:id>', methods=['POST'])
def deletecategory(id):
    if 'email' not in session:
        flash(f'Please login first', 'danger')
        return redirect(url_for("login"))
    category = Category.query.get_or_404(id)
    if request.method == "POST":
        db.session.delete(category)
        db.session.commit()
        flash(f'The category {category.name} has been deleted from your database', 'success')
        return redirect(url_for('admin'))
    flash(f'The category {category.name} cannot be deleted from your database', 'warning')
    return redirect(url_for('admin'))


@app.route('/deleteproduct/<int:id>', methods=['POST'])
def deleteproduct(id):
    if 'email' not in session:
        flash(f'Please login first', 'danger')
        return redirect(url_for("login"))
    product = AddProducts.query.get_or_404(id)
    if request.method == "POST":

        if request.files.get('image_1'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_1))
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_2))
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_3))
            except Exception as e:
                print(e)
        db.session.delete(product)
        db.session.commit()
        flash(f'The product {product.name} has been deleted from your database', 'success')
        return redirect(url_for('admin'))
    flash(f'The product {product.name} cannot be deleted from your database', 'warning')
    return redirect(url_for('admin'))