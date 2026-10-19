from django.shortcuts import render

# Create your views here.
def index(request):
    context = {}
    return render(request, 'home/index.html',context)

def aboutus(request):
    context = {}
    return render(request, 'home/aboutus.html',context)

def privacy_policy(request):
    context = {}
    return render(request, 'home/privacy-policy.html',context)

def refund_policy(request):
    context = {}
    return render(request, 'home/refund-policy.html',context)

def terms_of_service(request):
    context = {}
    return render(request, 'home/terms-of-services.html',context)

def contactus(request):
    context = {}
    return render(request, 'home/contactus.html',context)