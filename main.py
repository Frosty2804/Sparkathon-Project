import flet as ft
import copy
import subprocess
import json
from time import sleepexi
import asyncio

selected_product = {}
pb = ft.ProgressBar(width=400, visible=False)

# Defining Our Landing Page
class Landing(ft.View):
    def __init__(self, page: ft.Page):
        super(Landing, self).__init__(
            route="/",
            horizontal_alignment="center",
            vertical_alignment="center"
        )
        self.page = page

        self.cart_logo = ft.Icon(name="shopping_cart_outlined", size=64)
        self.title = ft.Text("Sparkathon : Our Idea", size=28, weight="bold", color="#a0cafd")
        self.subtitle = ft.Text("Made by Gabriel, Russell, Shuvayu and Sylvan", size=11, color="#ECEFF4")

        self.product_page_btn = ft.IconButton(
            "arrow_forward",
            width=54,
            height=54,
            style=ft.ButtonStyle(
                bgcolor={"": "#202020"},
                shape={"": ft.RoundedRectangleBorder(radius=8)},
                side={"": ft.BorderSide(2, "white54")},
            ),
            on_click=lambda e: self.page.go("/products"),
        )

        self.controls = [
            self.cart_logo,
            ft.Divider(height=25, color="transparent"),
            self.title,
            self.subtitle,
            ft.Divider(height=10, color="transparent"),
            self.product_page_btn,
        ]


# Define your model class => class that stores your data
class Model(object):
    products: dict = {
        0: {
            "id": "111",
            "img_src": "assets/phone1.png",
            "name": "Product 1",
            "description": "Experience the excellence of Product 1, a cutting-edge creation designed to elevate your daily routine. Crafted with precision and innovation, this product offers unmatched quality and performance. Enhance your lifestyle with Product 1 today.",
            "price": "$21.55",
            "pos":[5,5]
        },
        1: {
            "id": "222",
            "img_src": "assets/phone2.png",
            "name": "Product 2",
            "description": "Immerse yourself in the sophistication of Product 2. Uniquely crafted to meet your needs, this product combines style and functionality seamlessly. Elevate your daily experiences with the exceptional features of Product 2.",
            "price": "$32.99",
            "pos":[10,10]

        },
        2: {
            "id": "333",
            "img_src": "assets/phone3.png",
            "name": "Product 3",
            "description": "Discover the versatility of Product 3, a dynamic solution designed for modern living. Whether it's convenience, durability, or style you seek, Product 3 delivers on all fronts. Make a statement with this exceptional product",
            "price": "$45.75",
            "pos":[15,12]
        },
    }

    cart: dict = {}

    @staticmethod
    def get_products():
        return Model.products

    @staticmethod
    def get_cart():
        return Model.cart

    @staticmethod
    def add_item_to_cart(data: str):
        for _, values in Model.products.items():
            for key, value in values.items():
                if value == data:
                    if not Model.cart.get(value):
                        Model.cart[value] = {"quantity": 1, **values}

                    else:
                        Model.cart[value]["quantity"] += 1

    @staticmethod
    def return_product_details(data : str):                                      #New function similar to one above, to pass the correct product's details in dictionary {}
        for _, values in Model.products.items():
            for key, value in values.items():
                if value == data:
                    return values



# Defining our Products Page
class Product(ft.View):
    def __init__(self, page: ft.Page):
        super(Product, self).__init__(route="/products")
        self.page = page
        self.initilize()

    # we break the UI compoenents into several functions for better code readability

    # a method to initilize everything
    def initilize(self):
        # main row where items appear
        self.products = ft.Row(expand=True, scroll="auto", spacing=30)
        self.create_products()

        self.controls = [
            self.display_product_page_header(),
            ft.Text("Shop", size=32, color="#a0cafd"),
            ft.Text("We hope you have a good time shopping with us.", size=12),
            ft.Text(size=60),
            ft.Text("Browse the Latest Electronics", size=28, color="#ECEFF4"),
            self.products,
            self.display_product_page_footer(),
        ]

    def display_product_page_footer(self):
        return ft.Row([ft.Text("Sparkathon X Shop", size=10, color="#a0cafd")], alignment="center")

    def display_product_page_header(self):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon("settings", size=18),
                    ft.IconButton(
                        "shopping_cart_outlined",
                        on_click=lambda e: self.page.go("/cart"),
                        icon_size=18,
                    ),
                ],
                alignment="spaceBetween",
            )
        )
    def display_product_page(self, product_id, img_src):

        product = self.products[product_id]
        self.page.views.append(
        ft.View(
            f"/product_page/{product_id}",
            controls=[
            ft.Image(src=img_src, width=200, height=200),
            ft.Text(product["name"], size=24, weight="bold"),
            ft.Text(f"Price: {product['price']}"),
            ft.Text(product["description"]),
            ft.IconButton(
            "arrow_back",
            on_click=lambda _: self.page.go("/"),)
            ]
            )
        )
        self.page.update()
    # Define a method that creates the product UI items from the Model
    def create_products(self, products: dict = Model.get_products()):
        # loop over the data and extract the info based on keys
        for _, values in products.items():
            for (
                key,
                value,
            ) in values.items():
                # values.items() has a specific key:value pairing system
                if key == "img_src":
                    img_src = self.create_product_image(img_path=value)
                elif key == "name":
                    name = values["name"]
                elif key == "description":
                    description = values["description"]
                elif key == "id":
                    idd = values["id"]
                elif key == "price":
                    price = self.create_product_event(values["price"], idd)

            product_button = self.create_product_button(name, idd, description)

            self.create_full_item_view(img_src, product_button, price)

    # define a gather method that compiles everything
    def create_full_item_view(self, img_src, texts, price):
        item = ft.Column()

        item.controls.append(self.create_product_container(4, img_src))
        item.controls.append(self.create_product_container(4, texts))
        item.controls.append(self.create_product_container(1, price))

        self.products.controls.append(self.create_item_wrapper(item))

    # a final wrapper method
    def create_item_wrapper(self, item: ft.Column):
        return ft.Container(
            width=250, height=450, content=item, padding=8, border_radius=6
        )

    # define am ethod for the image UI
    def create_product_image(self, img_path: str):
        return ft.Container(
            image_src=img_path, image_fit="fill", border_radius=6, padding=10
        )

    # define a method for the text UI (name + description)
    def create_product_button(self, name: str, idd : int, description: str):
        product_button =  ft.ElevatedButton(
            text = name,
            data=idd,
            on_click=self.view_product
        )
        return ft.Column([product_button, ft.Text(description, size=11)])


    # define a method for prie and a add_to_cart button
    def create_product_event(self, price: str, idd: str):
        # we use the idd to keep track of the products being clicked
        return ft.Row(
            [
                ft.Text(price, size=14),
                ft.IconButton(
                    "add",
                    data=idd,
                    on_click=self.add_to_cart,
                ),
            ],
            alignment="spaceBetween",
        )

    # A method to wrap our product card inside a container
    def create_product_container(self, expand: bool, control: ft.control):
        return ft.Container(content=control, expand=expand, padding=5)

    # before the cart, one final method to add items to the cart
    def add_to_cart(self, e: ft.TapEvent):
        Model.add_item_to_cart(data=e.control.data)
        print(Model.cart)

    def view_product(self, e: ft.TapEvent):
        global selected_product                                                                    #Compulsary if you dont want to lose global dict contents as {}
        selected_product = copy.deepcopy(Model.return_product_details(data=e.control.data))        #Deep Copy static fn's returned dictionary(temporary memory) onto global dict(permanant)
        print(selected_product)
        self.page.go('/product_page')


# Finally, we define our cart class
class Cart(ft.View):
    def __init__(self, page: ft.Page):
        super(Cart, self).__init__(route="/cart")
        self.page = page
        self.initilize()

    # similiar to the products page, we break down the UI cart into functions

    # a method to initilize
    def initilize(self):
        self.cart_items = ft.Column(spacing=20)
        self.create_cart()

        self.controls = [
            ft.Row(
                [
                    ft.IconButton(
                        "arrow_back_ios_new_outlined",
                        on_click=lambda e: self.page.go("/products"),
                        icon_size=16,
                    )
                ],
                alignment="spaceBetween",
            ),
            ft.Text("Cart", size=32),
            ft.Text("Your cart items"),
            self.cart_items,
        ]

    def create_cart(self, cart: dict = Model.get_cart()):
        for _, values in cart.items():
            for key, value in values.items():
                if key == "img_src":
                    img_src = self.create_item_image(img_path=value)
                elif key == "quantity":
                    quantity = self.create_item_quantity(values["quantity"])
                elif key == "name":
                    name = self.create_item_name(values["name"])
                elif key == "price":
                    price = self.create_item_price(values["price"])

            self.compile_cart_item(img_src, quantity, name, price)

    # we also have a method to compile all the items
    def create_cart_item(self):
        return ft.Row(alignment="spaceBetween")

    def compile_cart_item(self, img_src, quantity, name, price):
        row = self.create_cart_item()

        row.controls.append(img_src)
        row.controls.append(name)
        row.controls.append(quantity)
        row.controls.append(price)

        self.cart_items.controls.append(self.create_item_wrap(row))

    # we can now create the seperate UI components for each data
    def create_item_wrap(self, control: ft.Control):
        return ft.Container(
            content=control,
            padding=10,
            border=ft.border.all(1, "white10"),
            border_radius=6,
        )

    def create_item_image(self, img_path):
        return ft.Container(width=32, height=32, image_src=img_path, bgcolor="teal")

    def create_item_quantity(self, quantity: int):
        return ft.Text(f"{quantity} X")

    def create_item_name(self, name: str):
        return ft.Text(name, size=16)

    def create_item_price(self, price: str):
        return ft.Text(price)



class ProductPage(ft.View):
    def __init__(self, page: ft.Page):
        super(ProductPage, self).__init__(route="/product_page")
        self.page = page
        self.page.bgcolor = "pink600"
        page.add()
        self.initilize()


    def display_map(self, e: ft.TapEvent):
        # self.page.views.clear()
        s_file = open("settings.py","w")
        s_file.write(f'''position = {selected_product["pos"]} ''')
        s_file.close()

        old_controls = []
        for widget in self.controls:
            old_controls.append(widget)
        self.controls.clear()
        pr = ft.ProgressRing(width = 50, height = 50, stroke_width = 2, visible = True)
        text = ft.Text("Buckle your seatbelts...", size = 20)
        self.loading_icon.controls.append(pr)
        self.loading_icon.controls.append(text)
        row = ft.Row(
            [
                self.loading_icon
            ],
            expand = True,
            alignment = ft.MainAxisAlignment.CENTER,
            vertical_alignment = ft.CrossAxisAlignment.CENTER
        )

        self.controls.append(row)

        for i in range(0, 101):
            pr.value = i * 0.01
            sleep(0.1)
            self.page.update()

        subprocess.Popen(["python", "map_demo.py"])
        self.controls.clear()
        for widget in old_controls:
            self.controls.append(widget)
        self.page.update()


    def create_productpage_buttons(self, name: str, idd: int, description : str):
        return ft.Container(
            content=ft.Row(
                [
                    ft.IconButton(
                    "arrow_back",
                    on_click=lambda _: self.page.go("/products"),),

                    ft.ElevatedButton(
                        text = name,
                        data = idd,
                        on_click= self.display_map)
                ],
                alignment="spaceBetween",
            )
        )

    def initilize(self):
        self.products = ft.Row(expand=True, scroll="auto", spacing=30)
        self.loading_icon = ft.Column(alignment = ft.MainAxisAlignment.CENTER, horizontal_alignment = ft.CrossAxisAlignment.CENTER)

        self.controls = [

            # row,
            self.create_productpage_buttons("Find My Location", 4, "if you wanna make your enemies suffer excrutiating pain, suggest them flet!"),

            ft.Text(selected_product["name"], size=24, weight="bold"),
            ft.Divider(height=25, color="transparent"),
            ft.Text("Price: " + selected_product['price']),
            ft.Divider(height=25, color="transparent"),
            ft.Text(selected_product["description"]),
            ft.Divider(height=25, color="transparent"),
            ft.Image(src=selected_product['img_src'], width=200, height=200),
        ]

        self.page.update()


def main(page: ft.Page):
    page.window.height = 800
    page.window.width = 500
    page.bgcolor = "pink600"
    page.fonts = {
        "Inter": "https://rsms.me/inter/inter.css",
    }
    page.theme = ft.Theme(font_family="Inter")

    def router(route):
        page.views.clear()

        if page.route == "/":
            landing = Landing(page)
            page.views.append(landing)

        if page.route == "/products":
            products = Product(page)
            page.views.append(products)

        if page.route == "/cart":
            cart = Cart(page)
            page.views.append(cart)
        if page.route == "/product_page":
            product_page = ProductPage(page)
            page.views.append(product_page)

        page.update()

    page.on_route_change = router
    page.go("/")


ft.app(target=main, assets_dir="assets")
