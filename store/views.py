from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Product, Category, CustomUser
from .forms import SignUpForm, UpdateUserForm, ChangePasswordForm
from django.contrib.auth import get_user_model

User = get_user_model()  # your custom user model


# =========================
# User Authentication
# =========================

def register_user(request):
    """
    Register a new user and redirect to OTP verification if needed.
    """
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # require OTP verification
            user.save()

            # Generate OTP (6-digit random)
            import random
            otp_code = str(random.randint(100000, 999999))
            user.otp_code = otp_code
            user.save()

            # TODO: Send OTP via email here
            messages.success(request, f"Account created! Your OTP is: {otp_code} (Send via email in production)")
            return redirect('verify_otp', user_id=user.id)
        else:
            messages.error(request, "There was a problem registering. Please try again.")
            return redirect('register')
    else:
        form = SignUpForm()
    return render(request, 'register.html', {'form': form})


def login_user(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Authenticate using email and password
        user = authenticate(request, email=email, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, "You have been logged in successfully")
                return redirect('home')
            else:
                messages.error(request, "Your account is not verified yet. Check your email.")
                return redirect('login')
        else:
            messages.error(request, "Invalid credentials. Please try again")
            return redirect('login')

    return render(request, 'login.html')
def verify_otp(request, user_id):
    """
    Verify the OTP code for a new user.
    """
    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        otp_entered = request.POST.get('otp')
        if otp_entered == user.otp_code:
            user.is_active = True
            user.otp_code = ""
            user.save()
            messages.success(request, "Your account has been verified successfully!")
            return redirect('login')
        else:
            messages.error(request, "Invalid OTP. Please try again.")
            return redirect('verify_otp', user_id=user.id)

    return render(request, 'verify_otp.html', {'user': user})


def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('home')


# =========================
# User Profile & Password
# =========================

@login_required
def update_user(request):
    """
    Update current user profile.
    """
    current_user = request.user
    form = UpdateUserForm(request.POST or None, instance=current_user)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            login(request, current_user)  # refresh session
            messages.success(request, "Profile updated successfully!")
            return redirect('home')

    return render(request, "update_user.html", {'user_form': form})


@login_required
def update_password(request):
    """
    Update current user password.
    """
    current_user = request.user

    if request.method == "POST":
        form = ChangePasswordForm(current_user, request.POST)
        if form.is_valid():
            form.save()
            login(request, current_user)
            messages.success(request, "Password updated successfully!")
            return redirect('update_user')
        else:
            for error in form.errors.values():
                messages.error(request, error)
            return redirect('update_password')
    else:
        form = ChangePasswordForm(current_user)

    return render(request, 'update_password.html', {'form': form})


# =========================
# Products & Categories
# =========================

def home(request):
    """
    Home page showing all products.
    """
    products = Product.objects.all()
    return render(request, 'home.html', {'products': products})


def about(request):
    """
    About page.
    """
    return render(request, 'about.html')


def category_summary(request):
    """
    Page showing all categories.
    """
    categories = Category.objects.all()
    return render(request, 'category_summary.html', {"categories": categories})


def category(request, category_name):
    """
    Show products by category.
    """
    category_name = category_name.replace('-', ' ')
    try:
        category = Category.objects.get(name=category_name)
        products = Product.objects.filter(category=category)
        return render(request, 'category.html', {'products': products, 'category': category})
    except Category.DoesNotExist:
        messages.error(request, "That category doesn't exist.")
        return redirect('home')


def product(request, pk):
    """
    Product detail page.
    """
    try:
        product = Product.objects.get(id=pk)
        return render(request, 'product.html', {'product': product})
    except Product.DoesNotExist:
        messages.error(request, "That product doesn't exist.")
        return redirect('home')