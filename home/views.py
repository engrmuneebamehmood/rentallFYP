from django.shortcuts import render, get_object_or_404
# Create your views here.
from django.shortcuts import redirect

from django.http.response import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import *


from django.conf import settings

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse
from .models import Order
from django.contrib.auth.models import User
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import stripe
import time


import requests
import json


def calculate_distances(origin, destinations):
    destinations_str = '|'.join(destinations)
    base_url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins": origin,
        "destinations": destinations_str,
        "units": "metric",
        # "key": 'AIzaSyDADLDbMn2L46lP1UiVqiwDBTsmuq692ug',
        "key": 'AIzaSyA8uxf4Zc_TbJOEuq6orMtspgDkDV6ajNo',
    }

    # response = requests.get(base_url, params=params)
    # data = response.json()
    # print(data)

    data = {
              'destination_addresses': [
                'Rawalpindi, Punjab, Pakistan',
                'Rawalpindi, Punjab, Pakistan',
                'Pindigheb, Attock, Punjab, Pakistan',
                'Lahore, Punjab, Pakistan',
                'Rawalpindi, Punjab, Pakistan',
                'Islamabad, Islamabad Capital Territory, Pakistan',
                'Rawalpindi, Punjab, Pakistan',
                'Rawalpindi, Punjab, Pakistan',
                'Rawalpindi, Punjab, Pakistan'
              ],
              'origin_addresses': [
                'Islamabad, Islamabad Capital Territory, Pakistan'
              ],
              'rows': [
                {
                  'elements': [
                    {
                      'distance': {
                        'text': '120.8 km',
                        'value': 23826
                      },
                      'duration': {
                        'text': '120.8mins',
                        'value': 2828
                      },
                      'status': 'OK'
                    },
                    {
                      'distance': {
                        'text': '0 km',
                        'value': 23826
                      },
                      'duration': {
                        'text': ' 362.3 mins',
                        'value': 2828
                      },
                      'status': 'OK'
                    },
                    {
                      'distance': {
                        'text': '105 km',
                        'value': 104936
                      },
                      'duration': {
                        'text': '1 hour 31 mins',
                        'value': 5488
                      },
                      'status': 'OK'
                    },
                    {
                      'distance': {
                        'text': '377 km',
                        'value': 376588
                      },
                      'duration': {
                        ' text': '4 hours 32 mins',
                        'value': 16328
                      },
                      'status': 'OK'
                    },
                    {
                      'distance': {
                        'text': '23.8 km',
                        'value': 23826
                      },
                      'duration': {
                        'text': '47 mins',
                        'value ': 2828
                      },
                      'status': 'OK'
                    },
                    {
                      'distance': {
                        'text': '1 m',
                        'value': 0
                      },
                      'duration': {
                        'text': '1 min',
                        'value': 0
                      },
                      'status': 'OK'
                    },
                    {
                      'distance': {
                        'text': '23.8 km',
                        'value': 23826
                      },
                      'duration': {
                        'text': '47 mins',
                        'value': 2828
                      },
                      'status': 'OK'
                    },
                    {
                      'distance': {
                        'text': '23.8 km',
                        'value': 23826
                      },
                      'duration': {
                        'text': '47 mins',
                        'value': 2828
                      },
                      'status': 'OK'
                    },
                    {
                      'distance': {
                        'text': '23.8 km',
                        'value': 23826
                      },
                      'duration': {
                        'text': '47 mins',
                        'value': 2828
                      },
                      'status': 'OK'
                    }
                  ]
                }
              ],
              'status': 'OK'
          }

    # print('Response from the Google Maps API: ', data)

    distances = []
    if data["status"] == "OK":
        elements = data["rows"][0]["elements"]
        for i, element in enumerate(elements):
            if element["status"] == "OK":
                distance_km = element["distance"]["value"] / 1000
                distances.append(round(distance_km, 1))
            else:
                distances.append({
                    "destination": destinations[i],
                    "error": "Error with this destination address."
                })
    else:
        return {"error": "Error with the API request."}

    return distances


def index(request):
    login = request.user.is_authenticated
    cars = Car.objects.all()
    distances = [None] * cars.count()

    if login:
        try:
            customer = Customer.objects.get(user=request.user)
            customer_city = customer.location.location

            destinations = [car.car_dealer.location.location for car in cars]
            distances = calculate_distances(customer_city, destinations)
        except Customer.DoesNotExist:
            login = False

    cars_with_distances_and_status = []

    for car, distance in zip(cars, distances):
        # Check if there is any incomplete order for this car
        incomplete_order = Order.objects.filter(car=car, is_complete=False).exists()

        # Determine the status based on the incomplete_order
        status = 'Rented' if incomplete_order else 'Available'

        # Add the car, distance, and status to the list
        cars_with_distances_and_status.append((car, distance, status))

    return render(request, "index.html", {
        'cars_with_distances_and_status': cars_with_distances_and_status,
        'login': login,
    })
def customer_signup(request):
    if request.user.is_authenticated:
        return redirect("/")
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        phone = request.POST['phone']
        location = request.POST['location']

        if password1 != password2:
            return redirect("/customer_signup")

        user = User.objects.create_user(username=username, email=email, first_name=first_name, last_name=last_name,
                                        password=password1)
        user.save()
        try:
            location_name = request.POST['location'].lower()
            location = Location.objects.get(location=location_name)
        except Location.DoesNotExist:
            location = Location.objects.create(location=location_name)
        except:
            location = None

        if location is None:
            # Handle the case where location is None
            return HttpResponse("Location is required.")
        else:
            # Proceed with creating the customer
            customer = Customer(user=user, phone=phone, location=location, type="Customer")
            customer.save()

        alert = True
        return render(request, "customer_signup.html", {'alert': alert})
    return render(request, "customer_signup.html")


from .models import Customer
from django.contrib import messages

from django.views.decorators.csrf import csrf_protect


def customer_login(request):
    if request.user.is_authenticated:
        return redirect("/")
    else:
        if request.method == "POST":
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)

            if user is not None:
                if Customer.objects.filter(user=user).exists():
                    customer = Customer.objects.get(user=user)
                    if customer.type == "Customer":
                        login(request, user)
                        return redirect("/customer_homepage")
                else:
                    messages.error(request, "You are not registered as a customer.")
            else:
                messages.error(request, "Invalid username or password.")

    return render(request, "customer_login.html")
from django.contrib import messages

from django.shortcuts import render, redirect
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from .models import CarDealer, Location

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from .models import CarDealer, Location

def car_dealer_signup(request):
    if request.method == "POST":
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        location = request.POST.get('location', '').lower()
        phone = request.POST.get('phone')
        easypaisa_number = request.POST.get('easypaisa_number')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return render(request, "car_dealer_signup.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
            return render(request, "car_dealer_signup.html")

        # Create the User object without easypaisa_number
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password1
        )
        user.save()

        # Get or create the Location object
        location_obj, created = Location.objects.get_or_create(location=location)

        # Create the CarDealer object and include easypaisa_number
        car_dealer = CarDealer(
            car_dealer=user,
            phone=phone,
            location=location_obj,
            type="Car Dealer",
            easypaisa_number=easypaisa_number
        )
        car_dealer.save()

        messages.success(request, "Account created successfully!")
        return redirect('car_dealer_login')

    return render(request, "car_dealer_signup.html")
def car_dealer_login(request):
    if request.user.is_authenticated:
        return redirect("/")

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            if CarDealer.objects.filter(car_dealer=user).exists():
                car_dealer = CarDealer.objects.get(car_dealer=user)
                if car_dealer.type == "Car Dealer":
                    login(request, user)
                    return redirect("/all_cars")
                else:
                    messages.error(request, "You are not registered as a vendor.")
            else:
                messages.error(request, "You are not registered as a vendor.")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "car_dealer_login.html")

def signout(request):
    logout(request)
    return redirect('/')

from django.shortcuts import render, redirect
from .models import Car


def add_car(request):
    if request.method == 'POST':
        car_name = request.POST['car_name']
        location = request.POST['location']
        image = request.FILES['image']
        capacity = request.POST['capacity']
        rent = request.POST['rent']
        category = request.POST['category']

        # Retrieve the CarDealer instance associated with the current user
        car_dealer = CarDealer.objects.get(car_dealer=request.user)

        car = Car(
            name=car_name,
            location=location,
            image=image,
            capacity=capacity,
            rent=rent,
            category=category,
            car_dealer=car_dealer  # Set the car_dealer attribute
        )
        car.save()
        return render(request, 'add_car.html', {'alert': True})
    return render(request, 'add_car.html')


def all_cars(request):
    dealer = CarDealer.objects.filter(car_dealer=request.user).first()
    cars = Car.objects.filter(car_dealer=dealer)
    return render(request, "all_cars.html", {'cars': cars})


def edit_car(request, car_id):
    car = get_object_or_404(Car, id=car_id)

    if request.method == "POST":
        car.name = request.POST['car_name']
        car.location = request.POST['location']
        car.capacity = request.POST['capacity']
        car.rent = request.POST['rent']

        if 'image' in request.FILES:
            car.image = request.FILES['image']

        car.save()
        alert = True
        return render(request, "edit_car.html", {'alert': alert, 'car': car})
    else:
        return render(request, "edit_car.html", {'car': car})
def delete_car(request, myid):
    if not request.user.is_authenticated:
        return redirect("/car_dealer_login")
    car = Car.objects.filter(id=myid)
    car.delete()
    return redirect("/all_cars")


def customer_homepage(request):
    return render(request, "customer_homepage.html")


def search_results(request):
    if request.method == 'POST':
        location = request.POST.get('location')
        if location:
            location = location.lower()
            vehicles_list = []
            location_objects = Location.objects.filter(location=location)

            for loc in location_objects:
                cars = Car.objects.filter(location=loc)
                for car in cars:
                    car_dealer = car.car_dealer
                    vehicle_dictionary = {
                        'name': car.name,
                        'id': car.id,
                        'image': car.image.url,
                        'location': car.location,
                        'capacity': car.capacity,
                        'category': car.category,
                        'phone': car_dealer.phone,
                        'car_dealer': car_dealer.car_dealer.username,
                    }

                    # Determine if the car is available or on rent
                    if car.is_available:
                        vehicle_dictionary['status'] = 'Available'
                    else:
                        # Check if this car is in completed orders
                        is_completed = Order.objects.filter(car=car, is_complete=True).exists()
                        if is_completed:
                            vehicle_dictionary['status'] = 'Available'
                        else:
                            vehicle_dictionary['status'] = 'On Rent'

                    vehicles_list.append(vehicle_dictionary)

            request.session['vehicles_list'] = vehicles_list

            return render(request, "search_results.html", {
                'vehicles_list': vehicles_list,
            })
        else:
            return render(request, "search_results.html", {'error': 'Please provide a valid location'})
    else:
        return HttpResponse("Method not allowed")


from django.shortcuts import render
from .models import Car


from django.shortcuts import render, get_object_or_404
from .models import Car


def payment_successful(request):
	stripe.api_key = settings.STRIPE_SECRET_KEY_TEST
	checkout_session_id = request.GET.get('session_id', None)
	session = stripe.checkout.Session.retrieve(checkout_session_id)
	customer = stripe.Customer.retrieve(session.customer)
	# customer_id = Customer.user
	# user_payment = UserPayment.objects.get(customer=1)
	# user_payment.stripe_checkout_id = checkout_session_id
	# user_payment.save()
	return render(request, 'payment_successful.html', {'customer': customer})


def payment_cancelled(request):
	stripe.api_key = settings.STRIPE_SECRET_KEY_TEST
	return render(request, 'payment_cancelled.html')


@csrf_exempt
def stripe_webhook(request):
	stripe.api_key = settings.STRIPE_SECRET_KEY_TEST
	time.sleep(10)
	payload = request.body
	signature_header = request.META['HTTP_STRIPE_SIGNATURE']
	event = None
	try:
		event = stripe.Webhook.construct_event(
			payload, signature_header, settings.STRIPE_WEBHOOK_SECRET_TEST
		)
	except ValueError as e:
		return HttpResponse(status=400)
	except stripe.error.SignatureVerificationError as e:
		return HttpResponse(status=400)
	if event['type'] == 'checkout.session.completed':
		session = event['data']['object']
		session_id = session.get('id', None)
		time.sleep(15)
		user_payment = UserPayment.objects.get(stripe_checkout_id=session_id)
		user_payment.payment_bool = True
		user_payment.save()
	return HttpResponse(status=200)




from django.shortcuts import render
from django.contrib.auth.models import User
from .models import Order
from django.shortcuts import render
from django.contrib.auth.models import User
from .models import Order, Car





def delete_order(request, myid):
    order = Order.objects.filter(id=myid)
    order.delete()
    return redirect("/past_orders")



def all_orders(request):
    username = request.user
    user = User.objects.get(username=username)
    car_dealer = CarDealer.objects.get(car_dealer=user)

    # Filter orders based on car dealer and completion status
    orders = Order.objects.filter(car_dealer=car_dealer)

    return render(request, "all_orders.html", {'all_orders': orders})


def complete_order(request):
    if request.method == 'POST':
        order_id = request.POST.get('id')
        order = get_object_or_404(Order, id=order_id)

        # Update order status to complete
        order.is_complete = True
        order.save()

    return redirect('/all_orders/')


def earnings(request):
    username = request.user
    user = User.objects.get(username=username)
    car_dealer = CarDealer.objects.get(car_dealer=user)
    orders = Order.objects.filter(car_dealer=car_dealer)
    all_orders = []
    for order in orders:
        all_orders.append(order)
    return render(request, "earnings.html", {'amount': car_dealer.earnings, 'all_orders': all_orders})


def order_details_view(request, total_rent=None):
    if request.method == 'POST':
        # Assuming you have retrieved the necessary data from the form
        car_id = request.POST.get('id')
        days = int(request.POST.get('days'))

        # Perform necessary calculations (e.g., calculating total rent)
        # Here, you would calculate the total rent based on car_id and days

        # Create an order object (assuming you have an Order model)
        # You need to replace this with the actual creation logic based on your models
        order = Order.objects.create(car_id=car_id, days=days, rent=total_rent)

        # Render the order completion page with necessary context
        return render(request, 'order_completion.html', {'order': order})

    # Handle GET request or other cases
    return HttpResponse("Method not allowed")





def about_us(request):
    return render(request, 'about_us.html')

def contact_us(request):
    return render(request, 'contact_us.html')

def privacy_policy(request):
    return render(request, 'privacy_policy.html')

def terms_of_service(request):
    return render(request, 'terms_of_service.html')

def FAQ(request):
    return render(request, 'FAQ.html')


def books(request):
    books_items = Car.objects.filter(category='books')

    login = request.user.is_authenticated
    distances = [None] * books_items.count()
    customer_city = None

    if login:
        try:
            customer = Customer.objects.get(user=request.user)
            customer_city = customer.location.location

            destinations = [book.car_dealer.location.location for book in books_items]
            distances = calculate_distances(customer_city, destinations)
        except Customer.DoesNotExist:
            login = False

    books_with_distances = zip(books_items, distances)

    return render(request, 'books.html', {
        'books_with_distances': books_with_distances,
        'login': login,
        'customer_city': customer_city,
    })


def furniture(request):
    furniture_items = Car.objects.filter(category='furniture')

    login = request.user.is_authenticated
    customer_city = None
    distances = [None] * furniture_items.count()

    if login:
        try:
            customer = Customer.objects.get(user=request.user)
            customer_city = customer.location.location

            destinations = [furniture.car_dealer.location.location for furniture in furniture_items]
            distances = calculate_distances(customer_city, destinations)
        except Customer.DoesNotExist:
            login = False

    furniture_with_distances_and_status = []

    for furniture, distance in zip(furniture_items, distances):
        # Check if there is any incomplete order for this furniture item
        incomplete_order = Order.objects.filter(car=furniture, is_complete=False).exists()

        # Determine the status based on the incomplete_order
        status = 'Rented' if incomplete_order else 'Available'

        # Add the furniture item, distance, and status to the list
        furniture_with_distances_and_status.append((furniture, distance, status))

    return render(request, 'furniture.html', {
        'furniture_with_distances_and_status': furniture_with_distances_and_status,
        'login': login,
        'customer_city': customer_city
    })


def electronic(request):
    electronic_items = Car.objects.filter(category='electronics')

    login = request.user.is_authenticated
    customer_city = None
    distances = [None] * electronic_items.count()

    if login:
        try:
            customer = Customer.objects.get(user=request.user)
            customer_city = customer.location.location

            destinations = [electronic.car_dealer.location.location for electronic in electronic_items]
            distances = calculate_distances(customer_city, destinations)
        except Customer.DoesNotExist:
            login = False

    electronic_with_distances_and_status = []

    for electronic, distance in zip(electronic_items, distances):
        # Check if there is any incomplete order for this electronic item
        incomplete_order = Order.objects.filter(car=electronic, is_complete=False).exists()

        # Determine the status based on the incomplete_order
        status = 'Rented' if incomplete_order else 'Available'

        # Add the electronic item, distance, and status to the list
        electronic_with_distances_and_status.append((electronic, distance, status))

    return render(request, 'electronic.html', {
        'electronic_with_distances_and_status': electronic_with_distances_and_status,
        'login': login,
        'customer_city': customer_city
    })


def dresses(request):
    dresses_items = Car.objects.filter(category='dresses')

    login = request.user.is_authenticated
    customer_city = None
    distances = [None] * dresses_items.count()

    if login:
        try:
            customer = Customer.objects.get(user=request.user)
            customer_city = customer.location.location

            destinations = [dress.car_dealer.location.location for dress in dresses_items]
            distances = calculate_distances(customer_city, destinations)
        except Customer.DoesNotExist:
            login = False

    dresses_with_distances_and_status = []

    for dress, distance in zip(dresses_items, distances):
        # Check if there is any incomplete order for this dress item
        incomplete_order = Order.objects.filter(car=dress, is_complete=False).exists()

        # Determine the status based on the incomplete_order
        status = 'Rented' if incomplete_order else 'Available'

        # Add the dress item, distance, and status to the list
        dresses_with_distances_and_status.append((dress, distance, status))

    return render(request, 'dresses.html', {
        'dresses_with_distances_and_status': dresses_with_distances_and_status,
        'login': login,
        'customer_city': customer_city
    })


def jewelry(request):
    jewelry_items = Car.objects.filter(category='jewelry')

    login = request.user.is_authenticated
    customer_city = None
    distances = [None] * jewelry_items.count()

    if login:
        try:
            customer = Customer.objects.get(user=request.user)
            customer_city = customer.location.location

            destinations = [jewelry.car_dealer.location.location for jewelry in jewelry_items]
            distances = calculate_distances(customer_city, destinations)
        except Customer.DoesNotExist:
            login = False

    jewelry_with_distances_and_status = []

    for jewelry, distance in zip(jewelry_items, distances):
        # Check if there is any incomplete order for this jewelry item
        incomplete_order = Order.objects.filter(car=jewelry, is_complete=False).exists()

        # Determine the status based on the incomplete_order
        status = 'Rented' if incomplete_order else 'Available'

        # Add the jewelry item, distance, and status to the list
        jewelry_with_distances_and_status.append((jewelry, distance, status))

    return render(request, 'jewelry.html', {
        'jewelry_with_distances_and_status': jewelry_with_distances_and_status,
        'login': login,
        'customer_city': customer_city
    })


def vehicle(request):
    vehicle_items = Car.objects.filter(category='vehicle')

    login = request.user.is_authenticated
    customer_city = None
    distances = [None] * vehicle_items.count()

    if login:
        try:
            customer = Customer.objects.get(user=request.user)
            customer_city = customer.location.location

            destinations = [vehicle.car_dealer.location.location for vehicle in vehicle_items]
            distances = calculate_distances(customer_city, destinations)
        except Customer.DoesNotExist:
            login = False

    vehicle_with_distances_and_status = []

    for vehicle, distance in zip(vehicle_items, distances):
        # Check if there is any incomplete order for this vehicle item
        incomplete_order = Order.objects.filter(car=vehicle, is_complete=False).exists()

        # Determine the status based on the incomplete_order
        status = 'Rented' if incomplete_order else 'Available'

        # Add the vehicle item, distance, and status to the list
        vehicle_with_distances_and_status.append((vehicle, distance, status))

    return render(request, 'vehicle.html', {
        'vehicle_with_distances_and_status': vehicle_with_distances_and_status,
        'login': login,
        'customer_city': customer_city
    })


def house(request):
    house_items = Car.objects.filter(category='house')

    login = request.user.is_authenticated
    customer_city = None
    distances = [None] * house_items.count()

    if login:
        try:
            customer = Customer.objects.get(user=request.user)
            customer_city = customer.location.location

            destinations = [house.car_dealer.location.location for house in house_items]
            distances = calculate_distances(customer_city, destinations)
        except Customer.DoesNotExist:
            login = False

    house_with_distances_and_status = []

    for house, distance in zip(house_items, distances):
        # Check if there is any incomplete order for this house item
        incomplete_order = Order.objects.filter(car=house, is_complete=False).exists()

        # Determine the status based on the incomplete_order
        status = 'Rented' if incomplete_order else 'Available'

        # Add the house item, distance, and status to the list
        house_with_distances_and_status.append((house, distance, status))

    return render(request, 'house.html', {
        'house_with_distances_and_status': house_with_distances_and_status,
        'login': login,
        'customer_city': customer_city
    })
from django.shortcuts import render
from .models import Car

def see_more(request):
    cars = Car.objects.all()
    login = request.user.is_authenticated
    customer_city = None
    distances = [None] * cars.count()

    if login:
        try:
            customer = Customer.objects.get(user=request.user)
            customer_city = customer.location.location

            destinations = [car.car_dealer.location.location for car in cars]
            distances = calculate_distances(customer_city, destinations)
        except Customer.DoesNotExist:
            login = False

    cars_with_distances_and_status = []

    for car, distance in zip(cars, distances):
        # Check if there is any incomplete order for this car item
        incomplete_order = Order.objects.filter(car=car, is_complete=False).exists()

        # Determine the status based on the incomplete_order
        status = 'Rented' if incomplete_order else 'Available'

        # Add the car item, distance, and status to the list
        cars_with_distances_and_status.append((car, distance, status))

    return render(request, 'see_more.html', {
        'cars_with_distances_and_status': cars_with_distances_and_status,
        'login': login,
        'customer_city': customer_city
    })


from django.shortcuts import render, HttpResponse
from django.contrib.auth.models import User
from .models import Order, Car
def order_details(request):
    if request.method == 'POST':
        stripe.api_key = settings.STRIPE_SECRET_KEY_TEST
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items = [
                {
                    'price': settings.PRODUCT_PRICE,
                    'quantity': 1
                }
            ],
            mode = 'payment',
            customer_creation = 'always',
            success_url = settings.REDIRECT_DOMAIN + '/payment_successful?session_id={CHECKOUT_SESSION_ID}',
            cancel_url = settings.REDIRECT_DOMAIN + '/payment_cancelled',
        )
        return redirect(checkout_session.url, code=303)


        return render(request, "order_details.html",)
    return render(request, "order_details.html")



def car_rent(request):
    if request.method == 'POST':
        id = request.POST.get('id')


        if id:
            car = get_object_or_404(Car, id=id)
            cost_per_day = int(car.rent)

            # Fetch the dealer associated with the selected car
            dealer = car.car_dealer
            easypaisa_number = dealer.easypaisa_number



            # Pass the dealer information to the template context, including the CNIC
            context = {
                'car': car,
                'cost_per_day': cost_per_day,
                'dealer': dealer,
                'image_url': car.image.url,


            }

            return render(request, 'car_rent.html', context)

    # If request method is GET or if no 'id' or 'cnic' was found in POST data,
    # render a template or redirect as appropriate
    return render(request, 'car_rent_form.html')




from datetime import datetime
from django.shortcuts import render
from dateutil import parser as dateparser
from .models import Car, CarDealer, Order
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
def done(request):
    if request.method == 'POST':
        car_id = request.POST['id']
        car = get_object_or_404(Car, id=car_id)

        # Retrieve data from the POST request
        first_name = request.POST.get('first_name')
        days = int(request.POST.get('days'))
        card = int(request.POST.get('card'))
        phone = int(request.POST.get('phone'))

        # Correct usage of datetime.strptime
        borrow_from = dateparser.parse(request.POST.get('borrow_from')).date()
        borrow_to = dateparser.parse(request.POST.get('borrow_to')).date()

        if car.is_available:
            car_dealer = car.car_dealer
            rent = int(car.rent) * days
            car_dealer.earnings += rent
            car_dealer.save()

            # Handle file uploads
            cnic_front = request.FILES.get('cnic_front')
            cnic_back = request.FILES.get('cnic_back')
            fs = FileSystemStorage()
            cnic_front_name = fs.save(cnic_front.name, cnic_front) if cnic_front else None
            cnic_back_name = fs.save(cnic_back.name, cnic_back) if cnic_back else None

            # Create the order
            try:
                order = Order(
                    car=car, car_dealer=car_dealer, user=request.user, rent=rent, days=days, card=card,
                    borrow_from=borrow_from, borrow_to=borrow_to,
                    cnic_front=cnic_front_name, cnic_back=cnic_back_name,phone=phone,
                )
                order.save()
            except Order.DoesNotExist:
                order = Order.objects.get(
                    car=car, car_dealer=car_dealer, user=request.user, rent=rent, days=days,
                    card=card, borrow_from=borrow_from, borrow_to=borrow_to,phone=phone,
                )

            # Update car availability
            car.is_available = False
            car.save()

            # Pass the retrieved data to the template
            return render(request, 'done.html', {
                'days': days, 'card': card, 'phone': phone, 'first_name': first_name,
                'borrow_from': borrow_from, 'borrow_to': borrow_to,
                'cnic_front_url': fs.url(cnic_front_name) if cnic_front else None,
                'cnic_back_url': fs.url(cnic_back_name) if cnic_back else None
            })

    # Handle cases where the method is not POST (optional)
    return render(request, 'done.html')


def error():
    return None


def past_orders(request):
    all_orders = []
    user = User.objects.get(username=request.user)
    try:
        orders = Order.objects.filter(user=user)
    except Order.DoesNotExist:
        orders = None

    if orders is not None:
        for order in orders:
            order_status = "Returned" if order.is_complete else "Active"
            order_dictionary = {
                'id': order.id,
                'rent': order.rent,
                'car': order.car,
                'days': order.days,
                'car_dealer': order.car_dealer,
                'borrow_from': order.borrow_from,
                'borrow_to': order.borrow_to,
                'status': order_status,
            }
            all_orders.append(order_dictionary)

    return render(request, "past_orders.html", {'all_orders': all_orders})


from django.contrib.auth.models import User
from .models import Order, Car



from django.shortcuts import render


import datetime

from .models import Order

from .recommendor  import build_recommendation_model
def recommendation(request):
    user_id = request.user.id
    recommended_car_ids = build_recommendation_model(user_id)
    recommended_cars = Car.objects.filter(id__in=recommended_car_ids)

    login = request.user.is_authenticated
    customer_city = None

    if login:
        try:
            customer = Customer.objects.get(user=request.user)
            customer_city = customer.location.location
        except Customer.DoesNotExist:
            login = False

    # Add status formatting
    for car in recommended_cars:
        car.is_available_text = "Available" if car.is_available else "Rented"

    return render(request, 'recommendation.html', {
        'recommended_cars': recommended_cars,
        'login': login,
        'customer_city': customer_city
    })

from mlxtend.frequent_patterns import fpgrowth
import pandas as pd
from .models import Order, Car


def generate_recommendations():
    # Query all orders
    orders = Order.objects.filter(is_complete=True).values_list('user_id', 'car_id')

    # Create a DataFrame
    data = pd.DataFrame(list(orders), columns=['user_id', 'car_id'])

    # Create a one-hot encoding DataFrame
    one_hot_encoded = data.pivot_table(index='user_id', columns='car_id', aggfunc=len, fill_value=0)

    # Convert counts to binary values
    one_hot_encoded = one_hot_encoded.applymap(lambda x: 1 if x > 0 else 0)

    # Generate frequent itemsets
    frequent_itemsets = fpgrowth(one_hot_encoded, min_support=0.1, use_colnames=True)

    # Sort frequent itemsets by support
    frequent_itemsets = frequent_itemsets.sort_values(by='support', ascending=False)

    # Extract and return recommended car IDs
    recommended_car_ids = frequent_itemsets['itemsets'].apply(lambda x: list(x)).explode().unique().tolist()

    return recommended_car_ids


def foryou(request):
    # Generate recommendations
    recommended_car_ids = generate_recommendations()

    # Fetch details of recommended cars
    recommended_cars = Car.objects.filter(id__in=recommended_car_ids)

    login = request.user.is_authenticated
    customer_city = None
    distances = [None] * recommended_cars.count()

    if login:
        try:
            customer = Customer.objects.get(user=request.user)
            customer_city = customer.location.location

            destinations = [car.car_dealer.location.location for car in recommended_cars]
            distances = calculate_distances(customer_city, destinations)
        except Customer.DoesNotExist:
            login = False

    cars_with_distances_and_status = []

    for car, distance in zip(recommended_cars, distances):
        # Check if there is any incomplete order for this car item
        incomplete_order = Order.objects.filter(car=car, is_complete=False).exists()

        # Determine the status based on the incomplete_order
        status = 'Rented' if incomplete_order else 'Available'

        # Add the car item, distance, and status to the list
        cars_with_distances_and_status.append((car, distance, status))

    return render(request, 'foryou.html', {
        'cars_with_distances_and_status': cars_with_distances_and_status,
        'login': login,
        'customer_city': customer_city
    })






from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from .chatbot import load_model, generate_response
import json
import traceback

# Load the model when the module is imported
load_model()

@csrf_exempt  # Disable CSRF for simplicity, but consider security implications
def chatbotmodel(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))  # Decode the request body correctly
            user_input = data.get('user_input', '')
            if not user_input:
                return JsonResponse({'error': 'No user input provided'}, status=400)
            response = generate_response(user_input)
            return JsonResponse({'response': response})
        except json.JSONDecodeError as e:
            return JsonResponse({'error': f'Invalid JSON: {str(e)}'}, status=400)
        except Exception as e:
            # Print the traceback for debugging purposes
            traceback.print_exc()
            return JsonResponse({'error': f'Error: {str(e)}'}, status=500)
    else:
        # Render the chatbot interface on GET request
        return render(request, 'chatbot.html')



