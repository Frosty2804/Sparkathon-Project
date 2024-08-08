import flet as ft
import copy
import subprocess
import colors
from time import sleep
import os
import shutil
import requests

if not os.path.exists("uploads"):
    os.makedirs("uploads")

# Defining Our Landing Page
class Landing(ft.View):
    def __init__(self, page: ft.Page):
        super(Landing, self).__init__(
            route="/",
            horizontal_alignment="center",
            vertical_alignment="center",
            bgcolor=colors.default_color
        )
        self.page = page

        self.cart_logo = ft.Icon(name="shopping_cart_outlined", size=64, color=colors.icon_color)
        self.title = ft.Text("Sparkathon : Our Idea", size=28, weight=ft.FontWeight.BOLD, color=colors.text_color)
        self.subtitle = ft.Text("Made by Gabriel, Russell, Shuvayu and Sylvan", size=11, color=colors.text_color)

        self.product_page_btn = ft.IconButton(
            "arrow_forward",
            icon_color=colors.icon_color,
            width=54,
            height=54,
            style=ft.ButtonStyle(
                bgcolor={"": colors.panel_color},
                shape={"": ft.RoundedRectangleBorder(radius=8)},
                side={"": ft.BorderSide(2, colors.icon_color)},
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
    CONVERSION_RATES = {
        "USD": 1.0,
        "EUR": 0.85,
        "INR": 82.50
    }
    SYMBOLS = {
        "USD": "$",
        "EUR": "€",
        "INR": "₹"
    }

    currency = "USD"

    products: dict = {
        0: {
            "id": "111",
            "img_src": "assets/xbox.png",
            "name": "Fridge",
            "description": "Experience the excellence of Product 1, a cutting-edge creation designed to elevate your daily routine. Crafted with precision and innovation, this product offers unmatched quality and performance. Enhance your lifestyle with Product 1 today.",
            "price": SYMBOLS["USD"] + str(25.99 * CONVERSION_RATES["USD"]),
            "usd_price": "$25.99",
            "pos":[1120,704]
        },
        1: {
            "id": "222",
            "img_src": "assets/mac.png",
            "name": "Overpriced Laptop",
            "description": "Immerse yourself in the sophistication of Product 2. Uniquely crafted to meet your needs, this product combines style and functionality seamlessly. Elevate your daily experiences with the exceptional features of Product 2.",
            "price": SYMBOLS["USD"] + str(45.99 * CONVERSION_RATES["USD"]),
            "usd_price": "$45.99",
            "pos":[768,288]
        },
        2: {
            "id": "333",
            "img_src": "assets/phone.png",
            "name": "Phone",
            "description": "Discover the versatility of Product 3, a dynamic solution designed for modern living. Whether it's convenience, durability, or style you seek, Product 3 delivers on all fronts. Make a statement with this exceptional product",
            "price": SYMBOLS["USD"] + str(65.99 * CONVERSION_RATES["USD"]),
            "usd_price": "$65.99",
            "pos":[1152,96]
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
    def update_prices(currency : str):
        for product in Model.products.values():
            conversion_rate = Model.CONVERSION_RATES[currency]
            converted_price = float(product["usd_price"][1:]) * conversion_rate
            product["price"] = Model.SYMBOLS[currency] + str(round(converted_price, 2))
            Model.currency = currency

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
        super(Product, self).__init__(route="/products", bgcolor = colors.default_color)
        self.page = page
        self.initilize()

    # we break the UI compoenents into several functions for better code readability

    # a method to initilize everythong
    def initilize(self):
        # this is the main row where items apepar ,,,
        self.products = ft.Row(expand=True, scroll="auto", spacing=30)
        self.create_products()

        self.controls = [
            self.display_product_page_header(),
            ft.Text("Shop", size=32, color=colors.text_color, weight=ft.FontWeight.BOLD),
            ft.Text("We hope you have a good time shopping with us.", size=12, color=colors.text_color),
            ft.Divider(height=70, color="transparent"),
            ft.Text("Browse the Latest Electronics", size=28, color=colors.text_color),
            self.products,
            self.display_product_page_footer(),
        ]

    def display_product_page_footer(self):
        return ft.Row([ft.Text("Sparkathon X Shop", size=10, color=colors.text_color, italic=True)], alignment="center")

    def display_product_page_header(self):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon("settings", size=18, color=colors.icon_color),
                    self.create_dropdown(),
                    ft.IconButton(
                        "shopping_cart_outlined",
                        on_click=lambda e: self.page.go("/cart"),
                        icon_size=18,
                        icon_color=colors.icon_color
                    ),
                    ft.ElevatedButton(
                        "Customer Support",
                        on_click=lambda e: self.page.go("/customer_support"),
                    ),
                ],
                alignment="spaceBetween",
            )
        )

    def create_dropdown(self):
        self.dd =  ft.Dropdown(
            width=100,
            value=Model.currency,
            label="Currency",
            label_style={"color": colors.text_color},
            options=[
                ft.dropdown.Option("USD"),
                ft.dropdown.Option("EUR"),
                ft.dropdown.Option("INR"),
            ],
            bgcolor=colors.panel_color,
            color=colors.text_color,
            border_color="transparent",
            on_change=self.on_dropdown_changed,
            autofocus=True
        )
        return self.dd

    def on_dropdown_changed(self, e):
        Model.update_prices(self.dd.value)
        self.products.controls.clear()
        self.create_products()
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
    def create_full_item_view(self, img_src, button, price):
        item = ft.Column()

        item.controls.append(self.create_product_container(4, img_src))
        item.controls.append(self.create_product_container(4, button))
        item.controls.append(self.create_product_container(1, price))

        self.products.controls.append(self.create_item_wrapper(item))

    # a final wrapper method
    def create_item_wrapper(self, item: ft.Column):
        return ft.Container(
            width=250, height=450, content=item, padding=8, border_radius=6, bgcolor=colors.panel_color
        )

    # define am method for the image UI
    def create_product_image(self, img_path: str):
        return ft.Container(
            image_src=img_path, image_fit="contain", border_radius=6, padding=10
        )

    # define a method for the button UI
    def create_product_button(self, name: str, idd : int, description: str):
        product_button =  ft.ElevatedButton(
            text = name,
            data=idd,
            on_click=self.view_product,
            bgcolor=colors.default_color,
            color=colors.text_color
        )
        return ft.Column([product_button, ft.Text(description, size=11)])


    # define a method for price and a add_to_cart button
    def create_product_event(self, price: str, idd: str):
        # we use the idd to keep track of the products being clicked
        return ft.Row(
            [
                ft.Text(price, size=14),
                ft.IconButton(
                    "add",
                    data=idd,
                    icon_color="#f8f8f2",
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

    def view_product(self, e: ft.TapEvent):
        global selected_product                                                                    #Compulsary if you dont want to lose global dict contents as {}
        selected_product = copy.deepcopy(Model.return_product_details(data=e.control.data))        #Deep Copy static fn's returned dictionary(temporary memory) onto global dict(permanant)
        self.page.go('/product_page')

# Customer Support
class CS_Chat(ft.View):
    def __init__(self, page: ft.Page):
        super(CS_Chat, self).__init__(route="/cs_chat", bgcolor= colors.default_color)
        self.page = page
        self.initialize()

    def initialize(self):
        self.controls = [
            ft.Row(
                [
                    ft.IconButton(
                        "arrow_back_ios_new_outlined",
                        on_click=lambda e: self.page.go("/customer_support"),
                        icon_size=16,
                    ),
                ],
                alignment="spaceBetween",
            ),
            ft.Text("Contact Us", size=32),
            ft.Text("Feel free to reach out to us with any inquiries or support requests."),
            # Add more controls or content as needed
        ]  

class Call_CS(ft.View):
    def __init__(self, page: ft.Page):
        super(Call_CS, self).__init__(route="/call_cs", bgcolor= colors.default_color)
        self.page = page
        self.initialize()

    def initialize(self):
        self.controls = [
            ft.Row(
                [
                    ft.IconButton(
                        "arrow_back_ios_new_outlined",
                        on_click=lambda e: self.page.go("/customer_support"),
                        icon_size=16,
                    ),
                ],
                alignment="spaceBetween",
            ),
            ft.Text("Contact Us", size=32),
            ft.Text("Feel free to reach out to us with any inquiries or support requests."),
            # Add more controls or content as needed
        ]



class Send_Video(ft.View):
    def __init__(self, page: ft.Page):
        super(Send_Video, self).__init__(route="/send_video", bgcolor= colors.default_color)
        self.page = page
        self.initialize()
    
    

    def initialize(self):
        
        def saveupload(e:ft.FilePickerResultEvent):
            for x in e.files:
                #print(x.path)
                #print(x.name)
                your_copy = os.path.join(os.getcwd(), "uploads")
                shutil.copy(x.path, your_copy)
            pass
        
        
        file_picker = ft.FilePicker(
            on_result=saveupload
        )   
        self.page.overlay.append(file_picker)
        
        self.controls = [
            ft.Row(
                [
                    ft.IconButton(
                        "arrow_back_ios_new_outlined",
                        on_click=lambda e: self.page.go("/customer_support"),
                        icon_size=16,
                    ),
                ],
                alignment="spaceBetween",
            ),
            ft.Text("Send a Video", size=32),
            ft.Text("Send a Video of your Problem: "),
            ft.ElevatedButton("Send Video", on_click=lambda e:file_picker.pick_files())
            # Add more controls or content as needed
        ]



# Finally, we define our cart class
class Cart(ft.View):
    def __init__(self, page: ft.Page):
        super(Cart, self).__init__(route="/cart", bgcolor = colors.default_color)
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
                        icon_color=colors.icon_color
                    )
                ],
                alignment="spaceBetween",
            ),
            ft.Text("Cart", size=32, weight = ft.FontWeight.BOLD, color=colors.text_color),
            ft.Text("Your cart items", color=colors.text_color),
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
                    price = self.create_item_price(values["usd_price"], values["quantity"])

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
        return ft.Container(width=32, height=32, image_src=img_path, bgcolor=colors.default_color)

    def create_item_quantity(self, quantity: int):
        return ft.Text(f"{quantity} X", color=colors.text_color)

    def create_item_name(self, name: str):
        return ft.Text(name, size=16, color=colors.text_color)

    def create_item_price(self, price: str, quantity: int):
        total_price = "$" + str(float(price[1:]) * quantity)
        return ft.Text(total_price, color=colors.text_color)


class ProductPage(ft.View):
    def __init__(self, page: ft.Page):
        super(ProductPage, self).__init__(route="/product_page", bgcolor = colors.default_color)
        self.page = page
        page.add()
        self.initilize()


    def initilize(self):
        self.loading_icon = ft.Column(alignment = ft.MainAxisAlignment.CENTER, horizontal_alignment = ft.CrossAxisAlignment.CENTER)

        self.controls = [
            self.create_productpage_buttons("Find My Location", 4, "if you wanna make your enemies suffer excrutiating pain, suggest them flet!"),
            ft.Text(selected_product["name"], size=24, weight="bold", color=colors.text_color),
            ft.Divider(height=25, color="transparent"),
            ft.Text("Price: " + selected_product['price'], color=colors.text_color),
            ft.Divider(height=25, color="transparent"),
            ft.Text(selected_product["description"], color=colors.text_color),
            ft.Divider(height=25, color="transparent"),
            ft.Image(src=selected_product['img_src'], width=200, height=200),
        ]

    def create_productpage_buttons(self, name: str, idd: int, description : str):
        return ft.Container(
            content= ft.Row(
                [
                    ft.IconButton(
                    "arrow_back_ios_new_outlined",
                    icon_color = colors.icon_color,
                    on_click=lambda _: self.page.go("/products"),),

                    ft.ElevatedButton(
                        text = name,
                        data = idd,
                        bgcolor=colors.panel_color,
                        color=colors.text_color,
                        on_click= self.display_map)
                ],
                alignment="spaceBetween",
            )
        )

    def display_map(self, e: ft.TapEvent):
        s_file = open("target_position.py","w")
        s_file.write(f'''position = {selected_product["pos"]} ''')
        s_file.close()

        old_controls = []
        for widget in self.controls:
            old_controls.append(widget)
        self.controls.clear()
        pr = ft.ProgressRing(width = 50, height = 50, stroke_width = 2, visible = True, color=colors.icon_color)
        text = ft.Text("Buckle your seatbelts...", size = 20, color=colors.text_color)
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

        subprocess.Popen(["python", "interactive_map.py"])
        self.loading_icon.controls.clear()
        self.controls.clear()
        pr.value = 0

        for widget in old_controls:
            self.controls.append(widget)
            self.page.update()


class CustomerSupport(ft.View):
    def __init__(self, page: ft.Page):
        super(CustomerSupport, self).__init__(route="/customer_support", bgcolor= colors.default_color)
        self.page = page
        self.initialize()

    def initialize(self):
        self.controls = [
            ft.Row(
                [
                    ft.IconButton(
                        "arrow_back_ios_new_outlined",
                        on_click=lambda e: self.page.go("/products"),
                        icon_size=16,
                    ),
                ],
                alignment="spaceBetween",
            ),
            ft.Text("Customer Support", size=32),
            ft.Text("Welcome to our customer support page. How can we assist you today?"),
            ft.ElevatedButton(
                text="Call Us",
                on_click=lambda e: self.page.go("/call_cs"),
            ),
            ft.ElevatedButton(
                text="Chat with Customer Support",
                on_click=lambda e: self.page.go("/cs_chat"),
            ),
            ft.ElevatedButton(
                text="Send a video",
                on_click=lambda e: self.page.go("/send_video"),
            ),
            # Add more controls as needed
        ]



def main(page: ft.Page):
    page.window.height = 800
    page.window.width = 500
    page.fonts = {
        "Inter": "https://rsms.me/inter/inter.css",
    }
    page.theme = ft.Theme(font_family="Inter")

    def router(route):
        page.views.clear()

        if page.route == "/":
            landing = Landing(page)
            page.views.append(landing)

        elif page.route == "/products":
            products = Product(page)
            page.views.append(products)

        elif page.route == "/cart":
            cart = Cart(page)
            page.views.append(cart)

        elif page.route == "/product_page":
            product_page = ProductPage(page)
            page.views.append(product_page)
            
        elif page.route == "/customer_support":
            customer_support = CustomerSupport(page)
            page.views.append(customer_support)
        
        elif page.route == "/call_cs":
            call_cs = Call_CS(page)
            page.views.append(call_cs)
           
        elif page.route == "/cs_chat":
            cs_chat = CS_Chat(page)
            page.views.append(cs_chat)
        
        elif page.route == "/send_video":
            send_video = Send_Video(page)
            page.views.append(send_video)

        page.update()

    page.on_route_change = router
    page.go("/")


ft.app(target=main, assets_dir="assets")
