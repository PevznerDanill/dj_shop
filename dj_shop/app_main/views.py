from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from app_users.models import Profile
from app_basket.basket import Basket
from django.http import HttpRequest, HttpResponse


class Index(TemplateView):
    """
    A view to display the main page.
    """
    template_name = 'app_main/index.html'

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        If the user is authenticated, adds the basket data and the related profile instance to the context.
        """
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            cur_profile = get_object_or_404(Profile, user=self.request.user)
            context['profile'] = cur_profile
            context['basket'] = Basket(self.request)

        return self.render_to_response(context)



