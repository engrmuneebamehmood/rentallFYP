from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("customer_signup/", views.customer_signup, name="customer_signup"),
    path("customer_login/", views.customer_login, name="customer_login"),
    path("car_dealer_signup/", views.car_dealer_signup, name="car_dealer_signup"),
    path("car_dealer_login/", views.car_dealer_login, name="car_dealer_login"),
    path("add_car/", views.add_car, name="add_car"),
    path("all_cars/", views.all_cars, name="all_cars"),
    path('edit_car/<int:car_id>/', views.edit_car, name='edit_car'),

    path("delete_car/<int:myid>/", views.delete_car, name="delete_car"),
    path("customer_homepage/", views.customer_homepage, name="customer_homepage"),
    path("search_results/", views.search_results, name="search_results"),
    path("car_rent/", views.car_rent, name="car_rent"),
    path("order_details/", views.order_details, name="order_details"),
    path("past_orders/", views.past_orders, name="past_orders"),
    path("delete_order/<int:myid>/", views.delete_order, name="delete_order"),
    path("all_orders/", views.all_orders, name="all_orders"),
    path("complete_order/", views.complete_order, name="complete_order"),
    path("earnings/", views.earnings, name="earnings"),
    path("signout/", views.signout, name="signout"),
    path('order_details/', views.order_details_view, name='order_details'),
    path('payment_successful/', views.payment_successful, name='payment_successful'),
    path('payment_cancelled/', views.payment_cancelled, name='payment_cancelled'),
    path('stripe_webhook/', views.stripe_webhook, name='stripe_webhook'),

    path('about-us/', views.about_us, name='about_us'),




    path('books/',views.books,name='books'),
    path('furniture/', views.furniture, name='furniture'),
    path('electronic/',views.electronic,name='electronic'),
    path('dresses/', views.dresses, name='dresses'),
    path('jewelry/', views.jewelry, name='jewelry'),
    path('vehicle/', views.vehicle, name='vehicle'),
    path('house/', views.house, name='house'),



    path('contact-us/', views.contact_us, name='contact_us'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
    path('FAQ/', views.FAQ, name='FAQ'),

    path('done/', views.done, name='done'),

    path('error/', views.error, name='error'),


    path('see_more/', views.see_more, name='see_more'),

    path('recommendation/', views.recommendation, name='recommendation'),

    path('foryou/', views.foryou, name='foryou'),





    path('chatbot/', views.chatbotmodel, name='chatbot'),








]
