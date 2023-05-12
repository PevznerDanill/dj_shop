from django.shortcuts import render, reverse, get_object_or_404
from django.views.generic import CreateView, DetailView, TemplateView, View
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile
from django.contrib.auth import authenticate, login
from django.urls import reverse_lazy
from .forms import AddBalance
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponseRedirect, HttpRequest, HttpResponse
from django.contrib import messages
from django.db import transaction
from app_basket.basket import Basket
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login as auth_login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from typing import Dict, Union


class RegisterView(CreateView):
    """
    A view to get registered.
    """
    template_name = 'app_users/register.html'
    model = User
    form_class = UserCreationForm
    success_url = reverse_lazy('app_main:index')

    def form_valid(self, form: UserCreationForm) -> HttpResponseRedirect:
        """
        Creates a new Profile instance related to the new user and performs his login.
        """
        self.object = form.save()
        Profile.objects.create(user=self.object)
        response = HttpResponseRedirect(self.get_success_url())
        username = form.cleaned_data['username']
        password = form.cleaned_data['password1']
        user = authenticate(
            self.request, username=username, password=password
        )
        login(self.request, user=user)
        return response

    def get_success_url(self) -> str:
        """
        Generates a link to the Personal Account page of the new Profile.
        """
        profile = Profile.objects.get(user=self.object)
        return reverse_lazy('app_users:profile', kwargs={'pk': profile.pk})


class MyLoginView(LoginView):
    """
    Overrides the default LoginView to add next_page, template and
    """
    next_page = reverse_lazy('app_main:index')
    template_name = 'app_users/login.html'


class MyLogoutView(LogoutView):
    """
    Overrides the default LogoutView to add next_page.
    """
    next_page = reverse_lazy('app_users:login')


class ProfileView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """
    A view to display the details of the retrieved Profile instance.
    """
    template_name = 'app_users/profile.html'
    queryset = (
        Profile.objects.select_related('user')
    )
    context_object_name = 'profile'

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Overrides the default get method removing from it the declaration of the
        self.object attribute as it was declared in self.setup()
        """
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        """
        Overrides the default setup method to declare self.object attribute.

        """
        super().setup(request, *args, **kwargs)
        self.object = self.get_object()

    def test_func(self) -> bool:
        """
        Checks if the current user has the same profile as the retrieved one.
        """
        if self.request.user.is_authenticated:
            return self.object == get_object_or_404(Profile, user=self.request.user)

    def get_context_data(self, **kwargs) -> Dict[str, Union[Profile, Basket, View]]:
        """
        Adds basket data to the context.
        """
        context = super().get_context_data(**kwargs)
        context['basket'] = Basket(self.request)
        return context


class AddBalanceView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
    A view for increasing of the balance.
    """

    template_name = 'app_users/add_balance.html'

    def test_func(self) -> bool:
        """
        Checks if the profile instance related to the request.user is the same as the retrieved one.
        """
        if self.request.user.is_authenticated:
            return self.profile == get_object_or_404(Profile, user=self.request.user)

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        """
        Declares self.profile attribute to be ready for the test_func().
        """
        super().setup(request, *args, **kwargs)
        self.profile = get_object_or_404(Profile, pk=kwargs.get('pk'))

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Adds to the context the form for the balance, profile instance and the basket data.
        """
        form = AddBalance()
        context = {
            'profile': self.profile,
            'form': form,
            'basket': Basket(request),
        }
        return self.render_to_response(context)

    @transaction.atomic
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponseRedirect:
        """
        Adds the passed amount to the profile.balance and adds a success message to the context.
        """
        cur_profile = Profile.objects.get(pk=kwargs['pk'])
        form = AddBalance(request.POST)
        if form.is_valid():
            money_to_add = form.cleaned_data['balance']
            cur_profile.add_balance(money_to_add)

            success_msg = _('You successfully added ${money_to_add} to your balance').format(
                money_to_add=money_to_add,
            )
            messages.success(request, success_msg)
            return HttpResponseRedirect(reverse('app_users:add_balance', kwargs={'pk': cur_profile.pk}))


class StatusInfoView(LoginRequiredMixin, TemplateView):
    """
    A view to display the general information about the status-discount system.
    """
    template_name = 'app_users/status_info.html'

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Adds the profile instance and the basket data to the context.
        """
        context = self.get_context_data(**kwargs)
        context.update(
            {
                'profile': Profile.objects.get(user=self.request.user),
                'basket': Basket(self.request)
            }
        )
        return self.render_to_response(context)
