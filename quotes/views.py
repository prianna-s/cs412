from django.shortcuts import render

import random
from django.shortcuts import render

quotes_list = [
    "Do stuff. Be clenched, curious. Not waiting for inspiration's shove or society's kiss on your forehead. Pay attention. It's all about paying attention. Attention is vitality. It connects you with others. It makes you eager. Stay eager.",
    "All photographs are memento mori. To take a photograph is to participate in another person’s (or thing’s) mortality, vulnerability, mutability. Precisely by slicing out this moment and freezing it, all photographs testify to time’s relentless melt.",
    "A writer, I think, is someone who pays attention to the world.",
]

images_list = [
    "https://compote.slate.com/images/778c2ab4-9257-491d-9edf-dffee255047a.jpeg?crop=1560%2C1040%2Cx0%2Cy0",
    "https://www.theparisreview.org/il/dfea80cf50/large/Susan-Sontag.jpg",
    "https://gaycitynews.com/wp-content/uploads/2021/04/sontag-by-avedon-New-Yorker-e1618936052793.jpg",
]

def quote(request):
    selected_quote = random.choice(quotes_list)
    selected_image = random.choice(images_list)
    context = {
        'quote': selected_quote,
        'image': selected_image
    }
    return render(request, 'quotes/quote.html', context)

def show_all(request):
    context = {
        'quotes': quotes_list,
        'images': images_list
    }
    return render(request, 'quotes/show_all.html', context)

def about(request):
    context = {
        'person_name': 'Susan Sontag',
        'biography': 'Susan Lee Sontag was an American writer, critic, and public intellectual. She mostly wrote essays, but also published novels; she published her first major work, the essay "Notes on Camp", in 1964',
        'creator_note': 'Created by Prianna Sharan.'
    }
    return render(request, 'quotes/about.html', context)
