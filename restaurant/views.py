from django.shortcuts import render
from django.utils import timezone
import random
from datetime import datetime, timedelta

# Daily special options
daily_specials = ["Pizza Margherita", 
                  "BBQ Burger", 
                  "Sushi Platter", 
                  "Pasta Alfredo"]

# Main page view
def main(request):
    return render(request, 'restaurant/main.html')

# Order page view
def order(request):
    daily_special = random.choice(daily_specials)
    context = {
        'daily_special': daily_special,
        'menu_items': [
            {'name': 'Pizza', 'price': 12.00, 'options': ['Cheese', 'Pepperoni', 'Veggie']},
            {'name': 'Burger', 'price': 10.00, 'options': ['Lettuce', 'Tomato', 'Cheese']},
            {'name': 'Pasta', 'price': 15.00},
            {'name': 'Salad', 'price': 8.00},
        ]
    }
    return render(request, 'restaurant/order.html', context)


# Example items and their prices (replace with your own)
MENU_ITEMS = {
    'Pizza': 12.00,
    'Burger': 10.00,
    'Pasta': 15.00,
    'Salad': 8.00,
}

def confirmation(request):
    if request.method == 'POST':
        # Get the form data from the request
        selected_items = request.POST.getlist('items')  # List of ordered items
        customer_name = request.POST.get('name')
        customer_phone = request.POST.get('phone')
        customer_email = request.POST.get('email')

        # Calculate the total price of the ordered items
        total_price = 0
        ordered_items = []

        for item in selected_items:
            if item in MENU_ITEMS:
                ordered_items.append(item)
                total_price += MENU_ITEMS[item]  # Add the price of each selected item
            if item in daily_specials:
                ordered_items.append(item)
                total_price += 10

        # Generate a random pickup time between 30 and 60 minutes from the current time
        random_minutes = random.randint(30, 60)
        ready_time = datetime.now() + timedelta(minutes=random_minutes)

        # Pass the information to the context to display on the confirmation page
        context = {
            'name': customer_name,
            'phone': customer_phone,
            'email': customer_email,
            'ordered_items': ordered_items,
            'total_price': total_price,
            'ready_time': ready_time.strftime('%I:%M %p'),  # Format time as HH:MM AM/PM
        }

        return render(request, 'restaurant/confirmation.html', context)

    # In case of GET request, redirect to the order page
    return render(request, 'restaurant/order.html')
